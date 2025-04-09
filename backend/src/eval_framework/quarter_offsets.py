

import os
import pandas as pd
import numpy as np
from collections import defaultdict
from mido import MidiFile, tick2second, tempo2bpm

# Reference tempo for quarter note conversion (Sonata's tempo is around 100 BPM)
REFERENCE_TEMPO = 100

def extract_notes(midi_path):
    print(f"Extracting notes from {midi_path}")
    
    midi = MidiFile(midi_path)
    ticks_per_beat = midi.ticks_per_beat
    
    # Track tempo changes throughout the piece
    tempo_changes = []
    initial_tempo = 500000  # Default 120 BPM
    
    for track in midi.tracks:
        absolute_tick = 0
        for msg in track:
            absolute_tick += msg.time
            if msg.type == 'set_tempo':
                tempo_changes.append((absolute_tick, msg.tempo))
                if absolute_tick == 0:
                    initial_tempo = msg.tempo
    
    if not any(tick == 0 for tick, _ in tempo_changes):
        tempo_changes.append((0, initial_tempo))
    
    tempo_changes.sort(key=lambda x: x[0])
    
    # Extract and process all notes
    all_notes = []
    track_notes = defaultdict(list)
    note_counter = 0
    
    for track_idx, track in enumerate(midi.tracks):
        absolute_tick = 0
        active_notes = {}
        
        for msg in track:
            absolute_tick += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                note_id = (msg.note, getattr(msg, 'channel', 0))
                active_notes[note_id] = {
                    'start_tick': absolute_tick,
                    'velocity': msg.velocity,
                    'track': track_idx
                }
            
            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                note_id = (msg.note, getattr(msg, 'channel', 0))
                if note_id in active_notes:
                    start_data = active_notes[note_id]
                    duration_ticks = absolute_tick - start_data['start_tick']
                    
                    if duration_ticks > 0:
                        start_seconds = tick_to_seconds(start_data['start_tick'], tempo_changes, ticks_per_beat)
                        end_seconds = tick_to_seconds(absolute_tick, tempo_changes, ticks_per_beat)
                        duration_seconds = end_seconds - start_seconds
                        
                        start_beat = start_data['start_tick'] / ticks_per_beat
                        end_beat = absolute_tick / ticks_per_beat
                        duration_beat = duration_ticks / ticks_per_beat
                        
                        # Convert to quarter note beats (1 measure in 6/8 time = 2 quarter notes)
                        quarter_note_beat = start_beat * (2/6)
                        
                        note = {
                            'note_id': note_counter,
                            'pitch': note_id[0],
                            'track': track_idx,
                            'start_tick': start_data['start_tick'],
                            'end_tick': absolute_tick,
                            'duration_ticks': duration_ticks,
                            'start_seconds': start_seconds,
                            'end_seconds': end_seconds,
                            'duration_seconds': duration_seconds,
                            'start_beat': start_beat,
                            'end_beat': end_beat,
                            'duration_beat': duration_beat,
                            'quarter_note_beat': quarter_note_beat
                        }
                        
                        all_notes.append(note)
                        track_notes[track_idx].append(note)
                        note_counter += 1
                    
                    del active_notes[note_id]
    
    all_notes.sort(key=lambda x: x['start_tick'])
    for track_idx in track_notes:
        track_notes[track_idx].sort(key=lambda x: x['start_tick'])
    
    return {
        'notes': all_notes,
        'track_notes': track_notes,
        'ticks_per_beat': ticks_per_beat,
        'tempo_changes': tempo_changes
    }

def tick_to_seconds(tick, tempo_changes, ticks_per_beat):
    seconds = 0.0
    last_tick = 0
    last_tempo = tempo_changes[0][1]
    
    for change_tick, tempo in tempo_changes:
        if change_tick < tick:
            tick_delta = change_tick - last_tick
            seconds += tick2second(tick_delta, ticks_per_beat, last_tempo)
            last_tick = change_tick
            last_tempo = tempo
        else:
            break
    
    remaining_ticks = tick - last_tick
    seconds += tick2second(remaining_ticks, ticks_per_beat, last_tempo)
    
    return seconds

def compare_midi_files(baseline_path, accelerando_path, output_path):
    baseline_data = extract_notes(baseline_path)
    accelerando_data = extract_notes(accelerando_path)
    
    comparison_data = []
    global_note_id = 0
    
    for baseline_note in baseline_data['notes']:
        matched_notes = [
            n for n in accelerando_data['notes'] 
            if n['pitch'] == baseline_note['pitch'] and 
            abs(n['start_beat'] - baseline_note['start_beat']) < 0.01
        ]
        
        if not matched_notes:
            print(f"Warning: No matching note found for baseline note ID {baseline_note['note_id']}")
            continue
        
        accelerando_note = matched_notes[0]
        
        record = {
            'note_number': global_note_id,
            'pitch': baseline_note['pitch'],
            'track': baseline_note['track'],
            'original_tick': baseline_note['start_tick'],
            'accelerando_tick': accelerando_note['start_tick'],
            'original_beat': baseline_note['start_beat'],
            'accelerando_beat': accelerando_note['start_beat'],
            'original_quarter_note_beat': baseline_note['quarter_note_beat'],
            'accelerando_quarter_note_beat': accelerando_note['quarter_note_beat'],
            'original_seconds': baseline_note['start_seconds'],
            'accelerando_seconds': accelerando_note['start_seconds'],
            'seconds_diff': accelerando_note['start_seconds'] - baseline_note['start_seconds'],
            'time_saving_percent': (baseline_note['start_seconds'] - accelerando_note['start_seconds']) / baseline_note['start_seconds'] * 100 if baseline_note['start_seconds'] > 0 else 0
        }
        
        comparison_data.append(record)
        global_note_id += 1
    
    df = pd.DataFrame(comparison_data)
    df = df.sort_values('original_seconds')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Note offset comparison saved to: {output_path}")
    
    return df

def create_simplified_quarter_note_mapping(comparison_df, output_path, reference_tempo=REFERENCE_TEMPO):
    quarter_note_duration = 60 / reference_tempo
    
    simplified = pd.DataFrame({
        'Note Number': comparison_df['note_number'],
        'Pitch': comparison_df['pitch'],
        'Original Beat Offset (6/8)': comparison_df['original_beat'],
        'Accelerando Beat Offset (6/8)': comparison_df['accelerando_beat'],
        'Original Quarter Note Beat': comparison_df['original_quarter_note_beat'],
        'Accelerando Quarter Note Beat': comparison_df['accelerando_quarter_note_beat'],
        'Original Time (s)': comparison_df['original_seconds'],
        'Accelerando Time (s)': comparison_df['accelerando_seconds'],
        'Time Difference (s)': comparison_df['seconds_diff'],
        'Time Saving (%)': comparison_df['time_saving_percent']
    })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    simplified.to_csv(output_path, index=False)
    print(f"Simplified quarter note mapping saved to: {output_path}")
    
    return simplified

def main():
    # To be edited
    baseline_path = "path/to/baseline.mid"
    accelerando_path = "path/to/accelerando.mid"
    output_path = "path/to/output.csv"
    
    comparison_df = compare_midi_files(baseline_path, accelerando_path, output_path)
    simplified_path = output_path.replace('.csv', '_simplified.csv')
    create_simplified_quarter_note_mapping(comparison_df, simplified_path)

if __name__ == "__main__":
    main()
