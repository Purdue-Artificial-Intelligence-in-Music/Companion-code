import mido

def remove_selected_tracks(input_file, output_file, tracks_to_remove):
    """
    Removes the specified tracks from a MIDI file.

    :param input_file: Path to the input MIDI file.
    :param output_file: Path to save the modified MIDI file.
    :param tracks_to_remove: List of track numbers (1-based) to remove.
    """
    # Load the MIDI file
    midi = mido.MidiFile(input_file)

    # Sort track indices in descending order to avoid index shifting
    tracks_to_remove = sorted([t - 1 for t in tracks_to_remove], reverse=True)

    # Validate and remove tracks
    for track_index in tracks_to_remove:
        if 0 <= track_index < len(midi.tracks):
            print(f"Removing track {track_index + 1}: {midi.tracks[track_index].name if midi.tracks[track_index].name else 'Unnamed Track'}")
            del midi.tracks[track_index]
        else:
            print(f"Track {track_index + 1} does not exist in the MIDI file.")

    # Save the modified MIDI file
    midi.save(output_file)
    print(f"Modified MIDI file saved as {output_file}")

def main():
    input_file = input("Enter the path to the input MIDI file: ").strip()
    output_file = input("Enter the path to save the modified MIDI file: ").strip()

    track_numbers = input("Enter the track numbers to remove (comma-separated, 1-based index): ")
    try:
        tracks_to_remove = [int(t.strip()) for t in track_numbers.split(",")]
    except ValueError:
        print("Invalid track numbers. Please enter valid integers separated by commas.")
        return

    remove_selected_tracks(input_file, output_file, tracks_to_remove)

if __name__ == "__main__":
    main()
