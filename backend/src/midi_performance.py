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
    (in beats) via update_score_position(). This polyphonic version allows multiple notes to
    play concurrently.

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
        self.last_beat = 0

        # Initialize FluidSynth.
        self.fs = fluidsynth.Synth(samplerate=44100)
        self.fs.start()
        sfid = self.fs.sfload(r"soundfonts\FluidR3_GM.sf2")
        self.fs.program_select(0, sfid, 0, program_number)

        # Extract note info in quarter-note units.
        self.notes = self._midi_to_notes_quarter(self.midi_file_path, self.instrument_index)
        self.notes.sort(key=lambda n: n[2])

        # Threading and note playback management.
        self._stop_event = threading.Event()
        self._performance_thread = None

        # List to track active note threads (for polyphony).
        self._active_note_threads = []
        self._active_note_lock = threading.Lock()

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
        self._next_note_index = 0

    def _note_worker(self, midi_note: int, duration_sec: float):
        """
        Worker function to play a note.

        Parameters
        ----------
        midi_note : int
            MIDI note number to play.
        duration_sec : float
            Duration in seconds to play the note.
        """
        self.fs.noteon(0, midi_note, 100)
        sleep(duration_sec)
        self.fs.noteoff(0, midi_note)
        # Remove this thread from active note threads.
        current = threading.current_thread()
        with self._active_note_lock:
            if current in self._active_note_threads:
                self._active_note_threads.remove(current)

    def _play_note(self, frequency: float, quarter_duration: float):
        """
        Play a note based on the current tempo, allowing for overlapping (polyphonic) playback.

        Parameters
        ----------
        frequency : float
            Frequency of the note in Hertz.
        quarter_duration : float
            Duration of the note in beats.
        """
        duration_sec = quarter_duration * (60.0 / self.current_tempo)
        midi_note = self._frequency_to_midi(frequency)
        # Create a new thread for this note.
        note_thread = threading.Thread(
            target=self._note_worker, args=(midi_note, duration_sec), daemon=True
        )
        with self._active_note_lock:
            self._active_note_threads.append(note_thread)
        note_thread.start()

    def _performance_loop(self):
        """
        Internal loop that monitors the score follower and plays notes accordingly.

        The loop waits until the score follower's position (in beats) passes a note's scheduled offset.
        If multiple notes are reached, they are all launched (allowing for polyphony).
        """
        while not self._stop_event.is_set() and self._next_note_index < len(self.notes):
            # Launch all notes whose scheduled beat is reached.
            while (self._next_note_index < len(self.notes) and
                   self.score_position >= self.notes[self._next_note_index][2]):
                frequency, quarter_duration, quarter_offset = self.notes[self._next_note_index]
                if (self.score_position - quarter_offset < .1 and (self.last_beat < self._next_note_index)):
                    print(
                        f"Playing note at beat {quarter_offset}: {frequency:.2f} Hz, "
                        f"duration {quarter_duration} beats"
                    )
                    self._play_note(frequency, quarter_duration)
                    self.last_beat = self._next_note_index
                self._next_note_index += 1
            sleep(0.005)
        print("Performance loop ended.")

    def start(self):
        """
        Start the performance.

        Begins the performance loop (in a separate thread), which monitors the score
        follower's position and plays notes as they are reached.
        """
        self._stop_event.clear()
        self._performance_thread = threading.Thread(
            target=self._performance_loop, daemon=True
        )
        self._performance_thread.start()
        print("Performance started.")

    def stop(self):
        """
        Stop the performance.

        Signals the performance loop to stop, waits for the loop to finish, and cleans up
        the FluidSynth synthesizer after waiting for all active note threads to finish.
        """
        self._stop_event.set()
        if self._performance_thread is not None:
            self._performance_thread.join()
        # Wait for all active note threads to finish.
        while True:
            with self._active_note_lock:
                if not self._active_note_threads:
                    break
            sleep(0.01)
        self.fs.delete()
        print("Performance stopped.")


# =============================================================================
# Example usage of the MidiPerformance class (polyphonic).
# =============================================================================
if __name__ == "__main__":
    import threading
    from time import sleep

    # Create a MidiPerformance instance with a MIDI file and an initial tempo (BPM).
    performance = MidiPerformance(
        midi_file_path=r"data/midi/twinkle_twinkle.mid", tempo=180, instrument_index=0, program_number=25
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
            sleep(0.01)
            performance.update_score_position(position)

    sf_thread = threading.Thread(target=simulate_score_follower, daemon=True)
    sf_thread.start()

    # Let the performance run for some time.
    sleep(100)

    # Stop the performance.
    performance.stop()
