import os
import pretty_midi
from music21 import converter, midi
import subprocess
import mido

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def check_fluidsynth_installed():
    '''Check if FluidSynth is installed'''
    try:
        subprocess.check_output(['fluidsynth', '--version'])
    except (FileNotFoundError, subprocess.CalledProcessError):
        raise RuntimeError(
            "FluidSynth is not installed. Please install it before using this package.")


def check_soundfont_installed():
    '''Check if the FluidR3_GM soundfont is installed'''
    if not os.path.exists(os.path.join(BASE_DIR, 'soundfonts', 'FluidR3_GM.sf2')):
        raise RuntimeError(
            "FluidR3_GM soundfont is not installed. Please install it before using this package.")


def musicxml_to_midi(input_path, output_path):
    score = converter.parse(input_path)
    midi_file = midi.translate.streamToMidiFile(score)
    # make sure the output directory exists
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    midi_file.open(output_path, "wb")
    midi_file.write()
    midi_file.close()
    return output_path


def change_midi_tempo(midi_file_path, new_tempo_bpm):
    """
    Change the tempo of a MIDI file and save it to the same file.

    Parameters:
    midi_file_path (str): Path to the original MIDI file.
    new_tempo_bpm (int or float): The new tempo in beats per minute (BPM).

    Returns:
    None
    """
    # Convert BPM to microseconds per beat (MIDI uses microseconds per quarter note)
    microseconds_per_beat = mido.bpm2tempo(new_tempo_bpm)

    # Load the MIDI file
    mid = mido.MidiFile(midi_file_path)

    # Create a new track list
    new_tracks = []

    for track in mid.tracks:
        new_track = mido.MidiTrack()

        # Have the tempo message at the beginning of the track
        new_track.append(mido.MetaMessage(
            'set_tempo', tempo=microseconds_per_beat, time=0))

        for msg in track:
            # Skip other 'set_tempo' messages in the track to avoid conflicts
            if msg.type != 'set_tempo':
                new_track.append(msg)
        new_tracks.append(new_track)

    # Create a new MIDI file with the updated tempo
    new_mid = mido.MidiFile()
    for new_track in new_tracks:
        new_mid.tracks.append(new_track)

    # Save the modified MIDI file
    new_mid.save(midi_file_path)
    print(
        f"Tempo changed to {new_tempo_bpm} BPM and saved to {midi_file_path}")


class AudioGenerator:
    """Class to generate audio from MusicXML and MIDI scores

    Parameters
    ----------
    path : str
        Path to MusicXML or MIDI score

    Attributes
    ----------
    score_path : str
        Path to MusicXML file

    """

    def __init__(self, score_path: str):
        if not os.path.exists(score_path):
            raise FileNotFoundError(f"File not found: {score_path}")
        if not (score_path.endswith('.musicxml') or score_path.endswith('.mid')):
            raise ValueError("Input file must be a MusicXML or MIDI file")

        title = os.path.basename(score_path)
        if score_path.endswith('.musicxml'):
            mid_path = score_path.replace('.musicxml', '.mid')
            mid_path = mid_path.replace('musicxml', 'midi')
            print("mid_path: ", mid_path)
            self.score_path = musicxml_to_midi(score_path, mid_path)
        else:
            self.score_path = score_path

    def generate_audio(self, output_dir: str, tempo: int = 120, sample_rate: int = 44100):
        """

        Parameters
        ----------
        output_path : str
            Path for generated audio file

        Returns
        -------
        None

        """

        # If the output directory does not exist, create it
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        change_midi_tempo(self.score_path, tempo)

        midi_data = pretty_midi.PrettyMIDI(self.score_path)  # load the midi file

        for i, instrument in enumerate(midi_data.instruments):  # iterate over each instrument in the midi file
            # Create a new PrettyMIDI object for the instrument
            instrument_midi = pretty_midi.PrettyMIDI()

            # Add the instrument to the new PrettyMIDI object
            instrument_midi.instruments.append(instrument)

            # Save the instrument's MIDI data to a temporary file
            temp_midi_file = os.path.join(output_dir, f"instrument_{i}.mid")
            instrument_midi.write(temp_midi_file)

            # Generate the corresponding audio file using Fluidsynth
            output_audio_file = os.path.join(output_dir, f"instrument_{i}.wav")
            fluidsynth_command = [
                "fluidsynth",
                "-ni",
                os.path.join("soundfonts", "FluidR3_GM.sf2"),
                temp_midi_file,
                "-F",
                output_audio_file,
                "-r",
                str(sample_rate)
            ]

            # Run the Fluidsynth command
            subprocess.run(fluidsynth_command, check=True)

            # Optional: Remove the temporary MIDI file
            os.remove(temp_midi_file)

            print(f"Generated {output_audio_file}")


if __name__ == '__main__':

    SCORE = os.path.join('data', 'musicxml', 'air_on_the_g_string.musicxml')
    OUTPUT_DIR = os.path.join('data', 'audio', 'air_on_the_g_string', '130bpm')
    SAMPLE_RATE = 44100
    TEMPO = 130

    generator = AudioGenerator(score_path=SCORE)
    generator.generate_audio(output_dir=OUTPUT_DIR, tempo=TEMPO)
    
