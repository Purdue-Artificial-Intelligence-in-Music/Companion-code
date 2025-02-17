import pretty_midi
import numpy as np
import subprocess
import os
from typing import Tuple, List

def midi_pitch_to_frequency(pitch: int) -> float:
    """Convert a MIDI pitch number to frequency (Hz)."""
    return 440.0 * 2 ** ((pitch - 69) / 12)

def generate_breakdown(baseline_notes: List[pretty_midi.Note],
                       variant_notes: List[pretty_midi.Note],
                       output_filename: str) -> None:
    """
    Generates a CSV file comparing baseline and variant note data.
    Each row contains:
      baseline_timestamp, baseline_frequency, baseline_duration,
      variant_timestamp, variant_frequency, variant_duration
    """
    # sort both lists by note start time
    baseline_sorted = sorted(baseline_notes, key=lambda n: n.start)
    variant_sorted = sorted(variant_notes, key=lambda n: n.start)
    count = min(len(baseline_sorted), len(variant_sorted))
    
    with open(output_filename, 'w') as f:
        f.write("baseline_timestamp,baseline_frequency,baseline_duration,"
                "variant_timestamp,variant_frequency,variant_duration\n")
        for i in range(count):
            b = baseline_sorted[i]
            v = variant_sorted[i]
            b_freq = midi_pitch_to_frequency(b.pitch)
            v_freq = midi_pitch_to_frequency(v.pitch)
            b_duration = b.end - b.start
            v_duration = v.end - v.start
            f.write(f"{b.start:.3f},{b_freq:.2f},{b_duration:.3f},"
                    f"{v.start:.3f},{v_freq:.2f},{v_duration:.3f}\n")

class MIDIProcessor:
    def __init__(self, input_midi: str, soundfont_path: str):
        self.input_midi = input_midi
        self.soundfont_path = soundfont_path

        pm = pretty_midi.PrettyMIDI(input_midi)
        self.solo_midi = pretty_midi.PrettyMIDI(initial_tempo=pm.estimate_tempo())

        if len(pm.instruments) > 0:
            self.solo_midi.instruments.append(pm.instruments[0])

        self.solo_midi.write('solo_baseline.mid')
        self._convert_to_wav('solo_baseline.mid', 'solo_baseline.wav')
        print("Created solo baseline")

    def create_pauses(self, pause_duration: float = 0.75) -> None:
        modified = pretty_midi.PrettyMIDI(initial_tempo=self.solo_midi.estimate_tempo())
        modified.instruments = [pretty_midi.Instrument(0)]

        tempo = self.solo_midi.estimate_tempo()
        beats_per_measure = 3
        seconds_per_measure = 60.0 / tempo * beats_per_measure

        notes = sorted(self.solo_midi.instruments[0].notes, key=lambda x: x.start)
        total_shift = 0
        last_measure = -1

        for note in notes:
            new_note = pretty_midi.Note(
                velocity=note.velocity,
                pitch=note.pitch,
                start=note.start,
                end=note.end
            )
            current_measure = int(new_note.start / seconds_per_measure)

            if current_measure > last_measure and last_measure != -1:
                total_shift += pause_duration

            new_note.start += total_shift
            new_note.end += total_shift

            modified.instruments[0].notes.append(new_note)
            last_measure = current_measure

        modified.write('solo_pauses.mid')
        self._convert_to_wav('solo_pauses.mid', 'solo_pauses.wav')
        print("Created solo pauses version")

    def create_rubato(self, variation_pct: float = 15.0) -> None:
        modified = pretty_midi.PrettyMIDI(initial_tempo=self.solo_midi.estimate_tempo())
        modified.instruments = [pretty_midi.Instrument(0)]
        time_groups = {}

        for note in self.solo_midi.instruments[0].notes:
            start_time = round(note.start, 3)
            if start_time not in time_groups:
                time_groups[start_time] = []
            time_groups[start_time].append(note)

        for start_time, notes in sorted(time_groups.items()):
            variation = 1.0 + (np.random.rand() * 2 - 1) * (variation_pct / 100.0)
            for note in notes:
                new_note = pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=note.start,
                    end=note.start + ((note.end - note.start) * variation)
                )
                modified.instruments[0].notes.append(new_note)

        modified.write('solo_rubato.mid')
        self._convert_to_wav('solo_rubato.mid', 'solo_rubato.wav')
        print("Created solo rubato version")

    def create_gradual_shifts(self, max_tempo_change: float = 1.3, 
                              min_tempo_change: float = 0.7, 
                              shift_rate: float = 0.01) -> None:
        modified = pretty_midi.PrettyMIDI()
        modified.instruments = [pretty_midi.Instrument(0)]
        tempo_factor = 1.0
        increasing = True

        for note in self.solo_midi.instruments[0].notes:
            new_note = pretty_midi.Note(
                velocity=note.velocity,
                pitch=note.pitch,
                start=note.start * tempo_factor,
                end=note.end * tempo_factor
            )
            modified.instruments[0].notes.append(new_note)

            if increasing:
                tempo_factor += shift_rate
                if tempo_factor >= max_tempo_change:
                    increasing = False
            else:
                tempo_factor -= shift_rate
                if tempo_factor <= min_tempo_change:
                    increasing = True

        modified.write('solo_gradual_shifts.mid')
        self._convert_to_wav('solo_gradual_shifts.mid', 'solo_gradual_shifts.wav')
        print("Created solo gradual shifts version")

    def create_smooth_temp_shifts(self, max_tempo_change: float = 1.1, 
                                  min_tempo_change: float = 0.9, 
                                  shift_rate: float = 0.001) -> None:
        """
        Applies very slight, gradual tempo changes (up and down) within a tight range.
        """
        modified = pretty_midi.PrettyMIDI(initial_tempo=self.solo_midi.estimate_tempo())
        modified.instruments = [pretty_midi.Instrument(0)]
        tempo_factor = 1.0
        increasing = True

        for note in self.solo_midi.instruments[0].notes:
            new_note = pretty_midi.Note(
                velocity=note.velocity,
                pitch=note.pitch,
                start=note.start * tempo_factor,
                end=note.end * tempo_factor
            )
            modified.instruments[0].notes.append(new_note)

            if increasing:
                tempo_factor += shift_rate
                if tempo_factor >= max_tempo_change:
                    increasing = False
            else:
                tempo_factor -= shift_rate
                if tempo_factor <= min_tempo_change:
                    increasing = True

        modified.write('solo_smooth_temp_shifts.mid')
        self._convert_to_wav('solo_smooth_temp_shifts.mid', 'solo_smooth_temp_shifts.wav')
        print("Created solo smooth tempo shifts version")

    def _convert_to_wav(self, midi_path: str, wav_path: str) -> None:
        command = [
            'fluidsynth',
            '-ni',
            self.soundfont_path,
            midi_path,
            '-F',
            wav_path,
            '-r',
            '44100'
        ]
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error converting {midi_path} to WAV: {e}")
            print(f"FluidSynth output: {e.output.decode()}")
            raise

    def process_all(self) -> None:
        # create all variant versions.
        print("Creating version with pauses...")
        self.create_pauses()
        print("Creating rubato version...")
        self.create_rubato()
        print("Creating gradual shifts version...")
        self.create_gradual_shifts()
        print("Creating smooth tempo shifts version...")
        self.create_smooth_temp_shifts()
        print("All variations created successfully!")

        
       
        baseline_pm = pretty_midi.PrettyMIDI('solo_baseline.mid')
        baseline_notes = baseline_pm.instruments[0].notes

        pauses_pm = pretty_midi.PrettyMIDI('solo_pauses.mid')
        generate_breakdown(baseline_notes, pauses_pm.instruments[0].notes, 
                           "baseline_pauses_breakdown.csv")
        
        rubato_pm = pretty_midi.PrettyMIDI('solo_rubato.mid')
        generate_breakdown(baseline_notes, rubato_pm.instruments[0].notes, 
                           "baseline_rubato_breakdown.csv")
        
        gradual_pm = pretty_midi.PrettyMIDI('solo_gradual_shifts.mid')
        generate_breakdown(baseline_notes, gradual_pm.instruments[0].notes, 
                           "baseline_gradual_shifts_breakdown.csv")
        print("Generated breakdown CSV files.")

def main():
    input_midi = "input.mid"
    soundfont = "soundfont.sf2"
    
    if not os.path.exists(input_midi):
        raise FileNotFoundError(f"Input MIDI file '{input_midi}' not found")
    if not os.path.exists(soundfont):
        raise FileNotFoundError(f"Soundfont file '{soundfont}' not found")
    
    processor = MIDIProcessor(input_midi, soundfont)
    processor.process_all()

if __name__ == "__main__":
    main()
