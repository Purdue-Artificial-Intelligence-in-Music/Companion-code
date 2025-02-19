import math
import threading
from time import sleep, time
from typing import List, Tuple
import fluidsynth
from music21 import converter, chord, note


class MidiPerformance:
    """
    Class for performing a MIDI file’s score in real time based on an external score follower.

    The class extracts note information from a MIDI file (with timing in quarter-note units)
    and plays the notes using FluidSynth. The performance is run in a separate thread.
    During the performance, the current tempo (in BPM) can be adjusted via the
    set_tempo() method, and an external score follower can update the current score position
    (in beats) via update_score_position(). This polyphonic version uses a single scheduler to
    trigger note-on and note-off events so that notes that are meant to be played together
    are sent concurrently. Additionally, a note is only triggered if it is within one 8th
    note (0.5 beats) behind the score follower.
    
    Attributes
    ----------
    midi_file_path : str
        Path to the MIDI file.
    current_tempo : float
        Current tempo in beats per minute.
    instrument_index : int
        Index of the instrument (part) to extract notes from.
    notes : List[Tuple[float, float, float]]
        List of note tuples (frequency, quarter_duration, quarter_offset), where:
            frequency : float
                Frequency of the note in Hertz.
            quarter_duration : float
                Duration of the note in beats.
            quarter_offset : float
                Onset time (offset) in beats.
    score_position : float
        Current position (in beats) of the soloist as estimated by the score follower.
    """

    def __init__(self, midi_file_path: str, tempo: float, instrument_index: int = 0, program_number: int = 43):
        """
        Initialize the MidiPerformance with a MIDI file and an initial tempo.

        Parameters
        ----------
        midi_file_path : str
            Path to the MIDI file.
        tempo : float
            Initial tempo in beats per minute.
        instrument_index : int, optional
            Index of the instrument to extract from the MIDI file (default is 0).
        program_number : int, optional
            MIDI program number to choose the instrument (default is 43, which is a cello).
        """
        self.midi_file_path = midi_file_path
        self.current_tempo = tempo
        self.instrument_index = instrument_index
        self.score_position = 0.0  # in beats
        self._next_note_index = 0

        # Initialize FluidSynth.
        self.fs = fluidsynth.Synth(samplerate=44100)
        self.fs.start()
        sfid = self.fs.sfload(r"soundfonts\FluidR3_GM.sf2")
        self.fs.program_select(0, sfid, 0, program_number)

        # Extract note info in quarter-note units.
        self.notes = self._midi_to_notes_quarter(self.midi_file_path, self.instrument_index)
        self.notes.sort(key=lambda n: n[2])

        # Threading and performance loop management.
        self._stop_event = threading.Event()
        self._performance_thread = None

        # List to track active notes (tuples of (midi_note, scheduled_note_off_time)).
        self._active_notes = []
        self._notes_lock = threading.Lock()

    def _midi_to_notes_quarter(
        self, midi_file_path: str, instrument_index: int
    ) -> List[Tuple[float, float, float]]:
        """
        Parse a MIDI file and extract note information in quarter-note units.

        Parameters
        ----------
        midi_file_path : str
            Path to the MIDI file.
        instrument_index : int
            Index of the instrument (part) to extract notes from.

        Returns
        -------
        List[Tuple[float, float, float]]
            List of tuples, where each tuple is (frequency, quarter_duration, quarter_offset).
        """
        try:
            midi_stream = converter.parse(midi_file_path)
        except Exception as e:
            print(f"Error parsing MIDI file: {e}")
            return []

        parts = midi_stream.parts
        if instrument_index < 0 or instrument_index >= len(parts):
            raise IndexError(
                f"Instrument index {instrument_index} is out of range. Please choose between 0 and {len(parts)-1}."
            )

        selected_part = parts[instrument_index]
        flat_part = selected_part.flat.stripTies()

        notes_list = []
        for element in flat_part.notes:
            quarter_offset = element.offset
            quarter_duration = element.duration.quarterLength
            if isinstance(element, note.Note):
                frequency = element.pitch.frequency
                notes_list.append((frequency, quarter_duration, quarter_offset))
            elif isinstance(element, chord.Chord):
                for pitch in element.pitches:
                    frequency = pitch.frequency
                    notes_list.append((frequency, quarter_duration, quarter_offset))
        return notes_list

    @staticmethod
    def _frequency_to_midi(frequency: float) -> int:
        """
        Convert a frequency in Hertz to a MIDI note number.

        Parameters
        ----------
        frequency : float
            Frequency in Hertz.

        Returns
        -------
        int
            MIDI note number (0-127).
        """
        midi_note = 69 + 12 * math.log2(frequency / 440.0)
        return int(round(midi_note))

    def set_tempo(self, tempo: float):
        """
        Update the current tempo.

        Parameters
        ----------
        tempo : float
            New tempo in beats per minute.
        """
        self.current_tempo = tempo

    def update_score_position(self, position: float):
        """
        Update the score follower's current position.

        Parameters
        ----------
        position : float
            Current position in beats (quarter-note units).
        """
        self.score_position = position

    def _trigger_note(self, frequency: float, quarter_duration: float):
        """
        Trigger a note immediately (sending note-on) and schedule its note-off time.

        Parameters
        ----------
        frequency : float
            Frequency of the note in Hertz.
        quarter_duration : float
            Duration of the note in beats.
        """
        duration_sec = quarter_duration * (60.0 / self.current_tempo)
        midi_note = self._frequency_to_midi(frequency)
        now = time()
        note_off_time = now + duration_sec
        self.fs.noteon(0, midi_note, 100)
        with self._notes_lock:
            self._active_notes.append((midi_note, note_off_time))

    def _performance_loop(self):
        """
        Internal loop that monitors the score follower, triggers note-on events, and sends note-off events.

        When the score follower's position reaches or passes a note's scheduled offset, the note is triggered
        immediately—but only if it is within one 8th note (0.5 beats) behind the current score position.
        Otherwise, the note is skipped to prevent a burst of delayed notes. The loop also continuously checks
        if any active notes have reached their note-off time.
        """
        eighth_note = 0.5  # 0.5 beats equals an eighth note (assuming a quarter note = 1 beat)
        while not self._stop_event.is_set() and self._next_note_index < len(self.notes):
            current_time = time()
            # Process note-off events.
            with self._notes_lock:
                remaining_notes = []
                for midi_note, off_time in self._active_notes:
                    if current_time >= off_time:
                        self.fs.noteoff(0, midi_note)
                    else:
                        remaining_notes.append((midi_note, off_time))
                self._active_notes = remaining_notes

            # Trigger notes that have been reached.
            while (self._next_note_index < len(self.notes) and 
                   self.score_position >= self.notes[self._next_note_index][2]):
                frequency, quarter_duration, quarter_offset = self.notes[self._next_note_index]
                # Only trigger the note if it is within one 8th note behind the score follower.
                if (self.score_position - quarter_offset) <= eighth_note:
                    self._trigger_note(frequency, quarter_duration)
                else:
                    print(f"Skipping note at beat {quarter_offset:.2f} (score position: {self.score_position:.2f})")
                self._next_note_index += 1

            sleep(0.001)  # Short sleep for tight timing

        # Turn off any remaining active notes.
        with self._notes_lock:
            for midi_note, _ in self._active_notes:
                self.fs.noteoff(0, midi_note)
            self._active_notes.clear()
        print("Performance loop ended.")

    def start(self):
        """
        Start the performance.

        Begins the performance loop (in a separate thread), which monitors the score
        follower's position and triggers notes as scheduled.
        """
        self._stop_event.clear()
        self._performance_thread = threading.Thread(target=self._performance_loop, daemon=True)
        self._performance_thread.start()
        print("Performance started.")

    def stop(self):
        """
        Stop the performance.

        Signals the performance loop to stop, waits for the loop to finish, and cleans up
        the FluidSynth synthesizer.
        """
        self._stop_event.set()
        if self._performance_thread is not None:
            self._performance_thread.join()
        # Turn off any remaining active notes.
        with self._notes_lock:
            for midi_note, _ in self._active_notes:
                self.fs.noteoff(0, midi_note)
            self._active_notes.clear()
        self.fs.delete()
        print("Performance stopped.")

    def is_active(self) -> bool:
        """
        Check if the performance is currently active.

        Returns
        -------
        bool
            True if the performance is active, False otherwise.
        """
        return self._performance_thread is not None and self._performance_thread.is_alive()


# =============================================================================
# Example usage of the MidiPerformance class (polyphonic, with timing adjustments).
# =============================================================================
if __name__ == "__main__":
    import threading
    from time import sleep

    # Create a MidiPerformance instance with a MIDI file and an initial tempo (BPM).
    performance = MidiPerformance(
        midi_file_path=r"data/midi/pirates_of_the_aegean.mid", tempo=200, instrument_index=1, program_number=25
    )

    # Start the performance.
    sleep(2)
    performance.start()

    # Simulate score follower updates.
    def simulate_score_follower():
        position = 0
        prev_time = time()
        # Assume the piece is 144 beats long.
        while position < 144:
            current_time = time()
            elapsed_time = current_time - prev_time
            position += elapsed_time * performance.current_tempo / 60  # in beats
            prev_time = current_time
            sleep(0.005)
            performance.update_score_position(position)

    sf_thread = threading.Thread(target=simulate_score_follower, daemon=True)
    sf_thread.start()

    # Let the performance run for some time.
    sleep(100)

    # Stop the performance.
    performance.stop()
