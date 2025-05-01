import mido
import random
import numpy as np
import os
import matplotlib.pyplot as plt
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from scipy import interpolate

def apply_baseline(midi_file):
    """Save the MIDI file as-is (Baseline case)."""
    midi_file.save("solo_baseline.mid")

def apply_gradual_tempo_shift(midi_file, shift_percent=10, interval_seconds=10):
    """Gradually increases or decreases tempo by ±shift_percent every interval_seconds."""
    new_midi = MidiFile()
    for track in midi_file.tracks:
        new_track = MidiTrack()
        tempo = bpm2tempo(120)  # Default tempo (120 BPM)
        time_elapsed = 0
        for msg in track:
            new_track.append(msg)
            if msg.time > 0:
                time_elapsed += mido.tick2second(msg.time, midi_file.ticks_per_beat, tempo)
                if time_elapsed >= interval_seconds:
                    tempo += int(tempo * (shift_percent / 100))
                    new_track.append(mido.MetaMessage('set_tempo', tempo=tempo))
                    time_elapsed = 0
        new_midi.tracks.append(new_track)
    new_midi.save("solo_temp_shift.mid")
    
def apply_smooth_tempo_curve(midi_file, output_file="smooth_tempo_curve.mid", curve_type="sine", 
                             max_tempo_change=0.3, curve_periods=2):
    """
    Apply a smooth tempo curve to a MIDI file.
    
    Args:
        midi_file: Input MIDI file
        output_file: Path to save the output file
        curve_type: Type of tempo curve ('sine', 'accelerando', or 'ritardando')
        max_tempo_change: Maximum tempo change factor (e.g., 0.3 = ±30% from baseline tempo)
        curve_periods: Number of complete cycles for sine wave (ignored for other curve types)
    
    Returns:
        Path to the output file
    """
    # Create a new MIDI file
    new_midi = MidiFile(type=midi_file.type, ticks_per_beat=midi_file.ticks_per_beat)
    
    # Find the total duration of the piece in ticks
    total_ticks = 0
    for track in midi_file.tracks:
        track_ticks = sum(msg.time for msg in track)
        total_ticks = max(total_ticks, track_ticks)
    
    # Find the original tempo (use 120 BPM as default if not specified)
    original_tempo = 500000  # Default 120 BPM in microseconds per beat
    for track in midi_file.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                original_tempo = msg.tempo
                break
    
    # Create the tempo curve function
    def tempo_factor_at_position(position):
        """Calculate tempo factor (1.0 = no change) at a relative position in the piece."""
        if curve_type == 'sine':
            # Sinusoidal tempo curve (oscillates between faster and slower)
            return 1.0 + max_tempo_change * np.sin(2 * np.pi * curve_periods * position)
        elif curve_type == 'accelerando':
            # Accelerando (gradually speeds up)
            return 1.0 - max_tempo_change * position
        elif curve_type == 'ritardando':
            # Ritardando (gradually slows down)
            return 1.0 + max_tempo_change * position
        else:
            return 1.0  # No change for unknown curve types
    
    # Calculate tempo changes at regular intervals
    num_tempo_changes = 100  # Number of tempo changes to insert
    tempo_changes = []
    
    for i in range(num_tempo_changes + 1):
        position = i / num_tempo_changes  # Relative position in the piece (0.0 to 1.0)
        tick_position = int(position * total_ticks)
        tempo_factor = tempo_factor_at_position(position)
        new_tempo = int(original_tempo / tempo_factor)  # Slower tempo = higher tempo value
        tempo_changes.append((tick_position, new_tempo))
    
    # Create a tempo map track
    tempo_track = MidiTrack()
    
    # Add initial tempo and time signature
    tempo_track.append(MetaMessage('set_tempo', tempo=tempo_changes[0][1], time=0))
    
    # Add the tempo change messages
    last_tick = 0
    for tick_pos, tempo in tempo_changes[1:]:
        delta_time = tick_pos - last_tick
        tempo_track.append(MetaMessage('set_tempo', tempo=tempo, time=delta_time))
        last_tick = tick_pos
    
    # Add the tempo track as the first track
    new_midi.tracks.append(tempo_track)
    
    # Add the rest of the tracks, preserving all events except tempo changes
    for track in midi_file.tracks:
        new_track = MidiTrack()
        for msg in track:
            # Skip tempo messages in other tracks to avoid conflicts
            if not (msg.type == 'set_tempo'):
                new_track.append(msg.copy())
        new_midi.tracks.append(new_track)
    
    # Save the modified MIDI file
    new_midi.save(output_file)
    
    # Return the path to the generated file
    return output_file

def apply_abrupt_tempo_jump(midi_file, jump_percent=25, measures=[8, 16, 24]):
    """Applies abrupt tempo changes at specified measure boundaries."""
    new_midi = MidiFile()
    tempo = bpm2tempo(120)
    measure_length = midi_file.ticks_per_beat * 4  # Assuming 4/4 time
    current_measure = 0

    for track in midi_file.tracks:
        new_track = MidiTrack()
        ticks_elapsed = 0
        for msg in track:
            new_track.append(msg)
            if msg.time > 0:
                ticks_elapsed += msg.time
                if ticks_elapsed >= measure_length:
                    current_measure += 1
                    ticks_elapsed = 0
                    if current_measure in measures:
                        tempo += int(tempo * (jump_percent / 100))
                        new_track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        new_midi.tracks.append(new_track)
    new_midi.save("solo_tempo_jump.mid")

def apply_deliberate_pauses(midi_file, pause_seconds=0.75):
    """Inserts pauses before strong beats at measure boundaries."""
    new_midi = MidiFile()
    pause_ticks = mido.second2tick(pause_seconds, midi_file.ticks_per_beat, bpm2tempo(120))
    
    for track in midi_file.tracks:
        new_track = MidiTrack()
        ticks_elapsed = 0
        for msg in track:
            if msg.type == 'note_on' and ticks_elapsed % (midi_file.ticks_per_beat * 4) == 0:
                new_track.append(Message('note_off', note=msg.note, velocity=msg.velocity, time=pause_ticks))
            new_track.append(msg)
            ticks_elapsed += msg.time
        new_midi.tracks.append(new_track)
    new_midi.save("solo_pauses.mid")

def apply_rubato(midi_file, rubato_percent=15):
    """Randomly lengthens or shortens note durations within phrases."""
    new_midi = MidiFile()
    
    for track in midi_file.tracks:
        new_track = MidiTrack()
        for msg in track:
            if msg.type in ['note_on', 'note_off']:
                variation = int(msg.time * (random.uniform(-rubato_percent, rubato_percent) / 100))
                msg.time = max(0, msg.time + variation)
            new_track.append(msg)
        new_midi.tracks.append(new_track)
    new_midi.save("solo_rubato.mid")

def plot_tempo_curve(curve_type, max_tempo_change=0.3, curve_periods=2, output_file="tempo_curve.png"):
    """
    Plot a tempo curve to visualize tempo changes over time.
    
    Args:
        curve_type: Type of tempo curve ('sine', 'accelerando', 'ritardando', or 'random')
        max_tempo_change: Maximum tempo change
        curve_periods: Number of periods for sine curve
        output_file: Path to save the plot
    """
    # Create the tempo curve function
    def tempo_factor_at_position(position):
        if curve_type == 'sine':
            return 1.0 + max_tempo_change * np.sin(2 * np.pi * curve_periods * position)
        elif curve_type == 'accelerando':
            return 1.0 - max_tempo_change * position
        elif curve_type == 'ritardando':
            return 1.0 + max_tempo_change * position
        elif curve_type == 'random':
            # Use a pre-generated curve for consistency (for plotting only)
            np.random.seed(42)  # For reproducibility
            num_points = 10
            x_points = np.linspace(0, 1, num_points)
            y_points = 1.0 + max_tempo_change * (2 * np.random.random(num_points) - 1)
            y_points[0] = 1.0
            y_points[-1] = 1.0
            interp = interpolate.PchipInterpolator(x_points, y_points)
            return float(interp(position))
        else:
            return 1.0
    
    # Generate the curve points
    x = np.linspace(0, 1, 1000)
    y = [tempo_factor_at_position(pos) for pos in x]
    
    # Calculate the effective BPM at 120 BPM baseline
    base_bpm = 120
    bpm_values = [base_bpm * factor for factor in y]
    
    # Create plot
    plt.figure(figsize=(10, 6))
    
    # Plot tempo factor
    plt.subplot(2, 1, 1)
    plt.plot(x, y)
    plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.3)
    plt.title(f'Tempo Factor Curve ({curve_type})')
    plt.ylabel('Tempo Factor')
    plt.grid(True, alpha=0.3)
    
    # Plot effective BPM
    plt.subplot(2, 1, 2)
    plt.plot(x, bpm_values)
    plt.axhline(y=base_bpm, color='r', linestyle='--', alpha=0.3)
    plt.title('Effective BPM (at 120 BPM baseline)')
    plt.xlabel('Position in Piece')
    plt.ylabel('BPM')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    
    return output_file

def process_urmp_piece(piece_folder, curve_type="sine", max_tempo_change=0.3, curve_periods=2):
    """
    Apply tempo alterations to a URMP piece.
    
    Args:
        piece_folder: Folder in the URMP dataset (e.g., '02_Sonata_vn_vn')
        curve_type: Type of tempo curve
        max_tempo_change: Maximum tempo change factor
        curve_periods: Number of periods for sine curve
        
    Returns:
        Dictionary with paths to output files
    """
    # URMP dataset configuration
    URMP_FOLDER = 'audio_URMP_stringoriginals->duets'
    # If folder not found, try the simpler "duets" fallback
    if not os.path.exists(URMP_FOLDER):
        URMP_FOLDER = 'duets'
    
    # Extract piece info
    piece_id = piece_folder.split('_')[0]
    piece_name = piece_folder.split('_')[1]
    
    # Path to MIDI file
    midi_path = os.path.join(URMP_FOLDER, piece_folder, f'Sco_{piece_folder}.mid')
    
    if not os.path.exists(midi_path):
        print(f"MIDI file not found: {midi_path}")
        return None
    
    # Create output directory
    output_dir = os.path.join('tempo_altered', piece_folder)
    os.makedirs(output_dir, exist_ok=True)
    
    # Load MIDI file
    try:
        midi_file = MidiFile(midi_path)
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        return None
    
    # Plot the tempo curve
    plot_path = os.path.join(output_dir, f'{curve_type}_curve.png')
    plot_tempo_curve(curve_type, max_tempo_change, curve_periods, plot_path)
    
    # Apply the tempo alterations
    output_path = os.path.join(output_dir, f'{curve_type}_altered.mid')
    altered_midi = apply_smooth_tempo_curve(
        midi_file, 
        output_file=output_path,
        curve_type=curve_type,
        max_tempo_change=max_tempo_change,
        curve_periods=curve_periods
    )
    
    return {
        'original_midi': midi_path,
        'altered_midi': output_path,
        'curve_plot': plot_path
    }

if __name__ == "__main__":
    # Test with available pieces
    urmp_pieces = [
        '02_Sonata_vn_vn',
        '12_Spring_vn_vn',
        '13_Hark_vn_vn',
        '24_Pirates_vn_vn',
        '26_King_vn_vn',
        '32_Fugue_vn_vn',
        '35_Rondeau_vn_vn',
        '36_Rondeau_vn_vn',
        '38_Jerusalem_vn_vn',
        '44_K515_vn_vn'
    ]
    
    print("URMP Tempo Alteration Tool")
    print("-------------------------")
    print("1. Apply alteration to a single piece")
    print("2. Generate example curves")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == '1':
        # Show list of pieces
        print("\nAvailable pieces:")
        for i, piece in enumerate(urmp_pieces):
            print(f"{i+1}. {piece}")
        
        piece_idx = int(input("Enter piece number (1-10): ")) - 1
        if 0 <= piece_idx < len(urmp_pieces):
            piece = urmp_pieces[piece_idx]
            
            # Show alteration options
            print("\nTempo alteration types:")
            print("1. Sine wave (oscillating tempo)")
            print("2. Accelerando (gradually speeds up)")
            print("3. Ritardando (gradually slows down)")
            
            alt_choice = int(input("Enter alteration type (1-3): "))
            curve_type = ["sine", "accelerando", "ritardando"][alt_choice-1]
            
            max_change = float(input("Enter maximum tempo change (0.0-1.0): "))
            
            if curve_type == "sine":
                periods = float(input("Enter number of oscillation cycles: "))
                result = process_urmp_piece(piece, curve_type, max_change, periods)
            else:
                result = process_urmp_piece(piece, curve_type, max_change)
            
            if result:
                print(f"\nFiles generated:")
                for key, path in result.items():
                    print(f"- {key}: {path}")
        else:
            print("Invalid piece number")
    
    elif choice == '2':
        # Generate example curves
        output_dir = "tempo_curves"
        os.makedirs(output_dir, exist_ok=True)
        
        curve_types = ["sine", "accelerando", "ritardando"]
        for curve_type in curve_types:
            output_file = os.path.join(output_dir, f"{curve_type}_example.png")
            plot_tempo_curve(curve_type, output_file=output_file)
            print(f"Generated {curve_type} example curve: {output_file}")
    
    else:
        print("Invalid choice")
