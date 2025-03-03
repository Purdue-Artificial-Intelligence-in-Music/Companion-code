import math
import threading
import heapq
from time import sleep, time
import fluidsynth
from music21 import converter, chord, note


class MidiPerformance:
    """
    Plays a MIDI file in real time with polyphony using a priority queue for scheduling.
    """

    def __init__(self, midi_file_path: str, tempo: float, instrument_index: int = 0, program_number: int = 43):
        self.midi_file_path = midi_file_path
        self.current_tempo = tempo  # BPM
        self.instrument_index = instrument_index
        self.score_position = 0.0  # beats
        self.queue = []  # Priority queue for scheduled notes
        self.queue_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.active_notes = {}  # Track active notes {midi_note: end_time}

        # Initialize FluidSynth
        self.fs = fluidsynth.Synth(samplerate=44100)
        self.fs.start()
        sfid = self.fs.sfload(r"soundfonts/FluidR3_GM.sf2")
        self.fs.program_select(0, sfid, 0, program_number)

        print(f"Initialized FluidSynth with instrument {program_number} (MIDI program).")

        # Extract notes and schedule them
        self.notes = self._midi_to_notes_quarter(midi_file_path, instrument_index)
        self._schedule_notes()

        # Thread for playing notes
        self.worker_thread = threading.Thread(target=self._note_worker, daemon=True)
        self.worker_thread.start()

    def _midi_to_notes_quarter(self, midi_file_path: str, instrument_index: int):
        """Parses a MIDI file and extracts note information in quarter-note units."""
        try:
            midi_stream = converter.parse(midi_file_path)
        except Exception as e:
            print(f"Error parsing MIDI file: {e}")
            return []

        parts = midi_stream.parts
        if instrument_index >= len(parts):
            raise IndexError(f"Instrument index {instrument_index} is out of range. Available: {len(parts)}")

        selected_part = parts[instrument_index]
        flat_part = selected_part.flat.stripTies()

        notes_dict = {}
        for element in flat_part.notes:
            quarter_offset = element.offset
            quarter_duration = element.duration.quarterLength
            if isinstance(element, note.Note):
                frequency = element.pitch.frequency
                midi_note = self._frequency_to_midi(frequency)
                notes_dict.setdefault(quarter_offset, []).append((midi_note, quarter_duration))
            elif isinstance(element, chord.Chord):
                for pitch in element.pitches:
                    frequency = pitch.frequency
                    midi_note = self._frequency_to_midi(frequency)
                    notes_dict.setdefault(quarter_offset, []).append((midi_note, quarter_duration))

        return sorted(notes_dict.items())  # (offset, [(midi_note, duration), ...])

    def _schedule_notes(self):
        """Schedules notes using a priority queue based on their onset time."""
        with self.queue_lock:
            for offset, notes in self.notes:
                heapq.heappush(self.queue, (offset, notes))

    @staticmethod
    def _frequency_to_midi(frequency: float) -> int:
        """Convert frequency in Hz to MIDI note number."""
        return int(round(69 + 12 * math.log2(frequency / 440.0)))

    def _note_worker(self):
        """Worker thread that plays notes based on scheduled offsets, allowing polyphony."""
        while not self.stop_event.is_set():
            current_time = time()
            
            # Check for notes to stop
            with self.queue_lock:
                for midi_note in list(self.active_notes.keys()):
                    if current_time >= self.active_notes[midi_note]:
                        self.fs.noteoff(0, midi_note)
                        del self.active_notes[midi_note]

                if not self.queue:
                    sleep(0.005)
                    continue

                next_offset, notes = heapq.heappop(self.queue)

            # Convert beats to real-time delay
            delay = (next_offset - self.score_position) * (60.0 / self.current_tempo)
            if delay > 0:
                sleep(delay)

            # Play all notes at this offset (polyphony)
            print(f"Playing {len(notes)} notes at beat {next_offset}: {[n[0] for n in notes]} (MIDI Notes)")
            for midi_note, duration in notes:
                self.fs.noteon(0, midi_note, 100)
                end_time = current_time + (duration * (60.0 / self.current_tempo))
                self.active_notes[midi_note] = end_time

    def update_score_position(self, position: float):
        """Updates the external score position in beats."""
        self.score_position = position

    def set_tempo(self, tempo: float):
        """Changes the playback tempo."""
        self.current_tempo = tempo

    def stop(self):
        """Stops playback and cleans up resources."""
        self.stop_event.set()
        self.worker_thread.join()
        self.fs.delete()
        print("Performance stopped.")

# =============================================================================
# Example usage
# =============================================================================
if __name__ == "__main__":
    from time import sleep

    # Create a MidiPerformance instance
    performance = MidiPerformance(
        midi_file_path=r"data/midi/fur_elise.mid", tempo=100, instrument_index=0, program_number=25
    )

    # Simulate score follower updates
    def simulate_score_follower():
        position = 0
        prev_time = time()
        while position < 144:
            elapsed_time = time() - prev_time
            position += elapsed_time * performance.current_tempo / 60
            prev_time = time()
            sleep(0.05)
            performance.update_score_position(position)

    sf_thread = threading.Thread(target=simulate_score_follower, daemon=True)
    sf_thread.start()

    # Let the performance run for some time
    sleep(100)

    # Stop the performance
    performance.stop()