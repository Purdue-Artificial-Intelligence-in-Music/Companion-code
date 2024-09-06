import subprocess
import pretty_midi
import os

def check_fluidsynth_installed():
    try:
        subprocess.check_output(['fluidsynth', '--version'])
    except (FileNotFoundError, subprocess.CalledProcessError):
        raise RuntimeError("FluidSynth is not installed. Please install it before using this package.")

def check_soundfont_installed():
    if not os.path.exists('soundfonts/FluidR3_GM/FluidR3_GM.sf2'):
        raise RuntimeError("FluidR3_GM soundfont is not installed. Please install it before using this package.")

def synthesize(midi_file: str, output_dir: str, sample_rate: int = 44100):
    '''
    Synthesize the audio data from a midi file and save it to the output directory
    
    Parameters
    ----------
    midi_file : str
        Path to the midi file
    output_dir : str
        Path to the output directory
    sample_rate : int
        Sample rate of the synthesized audio data
    '''

    if not os.path.exists(output_dir):  # If the output directory does not exist, create it
        os.makedirs(output_dir)

    midi_data = pretty_midi.PrettyMIDI(midi_file)  # load the midi file
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
            "C:\ProgramData\soundfonts\FluidR3_GM\FluidR3_GM.sf2",
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

check_fluidsynth_installed()
# check_soundfont_installed()
synthesize(midi_file='midi/Twelve_Duets.mid', output_dir='audio/Twelve_Duets')
