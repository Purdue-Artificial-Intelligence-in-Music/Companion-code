import os
import mido
from typing import List, Tuple
import numpy as np

def get_notes_from_file(midi_file: str) -> List[Tuple[float, float, int]]:
    """Extract note timings from the track with the most notes in a MIDI file.
    Returns list of (start_time, end_time, note_number) tuples in beats."""
    print(f"Processing {midi_file}...")
    try:
        mid = mido.MidiFile(midi_file)
        if len(mid.tracks) == 0:
            print(f"Warning: No tracks found in {midi_file}")
            return []

        print(f"Found {len(mid.tracks)} tracks")
        
        # Find track with most notes
        max_notes = []
        ticks_per_beat = mid.ticks_per_beat
        
        for track_idx, track in enumerate(mid.tracks):
            notes = []
            current_time = 0
            active_notes = {}  # note_number -> (start_time, start_ticks)
            
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = (current_time / ticks_per_beat, current_time)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        start_time, start_ticks = active_notes[msg.note]
                        end_time = current_time / ticks_per_beat
                        notes.append((start_time, end_time, msg.note))
                        del active_notes[msg.note]
            
            if len(notes) > len(max_notes):
                max_notes = notes
        
        print(f"Found {len(max_notes)} notes")
        return sorted(max_notes, key=lambda x: x[0])
    except Exception as e:
        print(f"Error processing {midi_file}: {str(e)}")
        return []

def generate_notes_file(dir_path: str, output_file: str):

    print(f"\nProcessing directory: {dir_path}")
    
    # Process each MIDI file
    alteration_files = ['baseline.mid', 'rubato.mid', 'ritardando.mid', 'accelerando.mid', 
                       'sine_wave_tempo.mid', 'pauses.mid']
    
    with open(output_file, 'w') as f:
        f.write("Note Timings Analysis\n")
        f.write("===================\n\n")
        
        for filename in alteration_files:
            file_path = os.path.join(dir_path, filename)
            if os.path.exists(file_path):
                print(f"\nProcessing {filename}")
                notes = get_notes_from_file(file_path)
                
                f.write(f"\n{filename}\n")
                f.write("-" * len(filename) + "\n")
                f.write("Note # | Note | Start (beats) | End (beats) | Duration (beats)\n")
                f.write("-" * 60 + "\n")
                
                for i, (start, end, note) in enumerate(notes):
                    duration = end - start
                    f.write(f"{i+1:6d} | {note:3d} | {start:11.2f} | {end:9.2f} | {duration:14.2f}\n")
                
                f.write("\n")
            else:
                print(f"File not found: {filename}")

def main():
   
    base_dir = "altered_urmp"
    if not os.path.exists(base_dir):
        print(f"Error: Directory {base_dir} not found!")
        return
        
    print(f"Starting analysis of {base_dir}")
    for dir_name in os.listdir(base_dir):
        if not os.path.isdir(os.path.join(base_dir, dir_name)):
            continue
            
        dir_path = os.path.join(base_dir, dir_name)
        output_file = os.path.join(dir_path, "note_timings.txt")
        print(f"\nProcessing {dir_name}...")
        generate_notes_file(dir_path, output_file)

if __name__ == "__main__":
    main() 
