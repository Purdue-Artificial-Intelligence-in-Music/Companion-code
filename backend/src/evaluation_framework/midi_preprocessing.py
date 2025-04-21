import mido
import csv

def midi_note_to_frequency(note):
    return 440.0 * (2.0 ** ((note - 69) / 12.0))

def process_accompaniment(file_path, output_csv):
    midi = mido.MidiFile(file_path)
    note_data = []  
    note_on_times = {} 
    
    current_time = 0 
    ticks_per_beat = midi.ticks_per_beat
    default_tempo = mido.bpm2tempo(60)  # Default tempo: 60 BPM (1,000,000 microseconds per beat)
    current_tempo = None  # Initialize tempo as None to detect absence of `set_tempo`
    
    # Ensure the MIDI file has at least two tracks
    if len(midi.tracks) < 2:
        raise ValueError("The MIDI file does not have a second track (accompaniment).")
    
    # Process only the second track (index 1)
    accompaniment_track = midi.tracks[1]
    
    for msg in accompaniment_track:
        current_time += msg.time 
        
        # Update tempo if a set_tempo message is encountered
        if msg.type == 'set_tempo':
            current_tempo = msg.tempo
        
        if msg.type == 'note_on' and msg.velocity > 0:
            note_on_times[msg.note] = current_time
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in note_on_times:
                start_time = note_on_times[msg.note]
                duration = current_time - start_time
                
                # Use default tempo if no set_tempo was found
                if current_tempo is None:
                    current_tempo = default_tempo
                    print("Did not find a `set_tempo` message. Using default tempo: 60 BPM.")

                # Time per tick calculation based on the current tempo
                time_per_tick = current_tempo / 1e6 / ticks_per_beat
                
                timestamp = start_time * time_per_tick
                duration_seconds = duration * time_per_tick
                frequency = midi_note_to_frequency(msg.note)
                
                note_data.append({
                    'Timestamp (s)': timestamp,
                    'Frequency (Hz)': frequency,
                    'Duration (s)': duration_seconds
                })
                
                del note_on_times[msg.note]  

    # Write the processed accompaniment data to a CSV file
    with open(output_csv, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['Timestamp (s)', 'Frequency (Hz)', 'Duration (s)'])
        writer.writeheader()
        writer.writerows(note_data)

# Run the function on the second track of the MIDI file
process_accompaniment('midi_extra_functions/Sco_01_Jupiter_vn_vc.mid', 'accompaniment_output.csv')
