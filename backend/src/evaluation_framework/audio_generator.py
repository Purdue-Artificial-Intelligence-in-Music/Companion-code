import os
import subprocess
import logging
import tempfile
import shutil
from pathlib import Path

import pretty_midi
import mido
from music21 import converter, midi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioGenerator:
    """
    Class to generate audio from MusicXML and MIDI scores using FluidSynth.

    Parameters
    ----------
    score_path : Path or str
        Path to a MusicXML or MIDI file.
    soundfont_path : Path or str, optional
        Path to the soundfont file. Defaults to a bundled 'FluidR3_GM.sf2' in a 'soundfonts'
        subdirectory relative to this file.

    Raises
    ------
    FileNotFoundError
        If the input score or the soundfont file cannot be found.
    RuntimeError
        If FluidSynth is not installed.
    ValueError
        If the score file does not have a supported extension.
    """

    def __init__(self, score_path, soundfont_path=None):
        self.score_path = Path(score_path)
        if not os.path.exists(self.score_path):
            raise FileNotFoundError(f"Score file not found: {self.score_path}")

        if self.score_path.suffix.lower() not in ['.musicxml', '.mid', '.midi']:
            raise ValueError("Input file must be a MusicXML or MIDI file")

        # Determine soundfont path
        if soundfont_path is None:
            # Assume the soundfont is in a subdirectory called 'soundfonts'
            self.soundfont_path = os.path.join('soundfonts', 'FluidR3_GM.sf2')
        else:
            self.soundfont_path = Path(soundfont_path)
        if not os.path.exists(self.soundfont_path):
            raise FileNotFoundError(f"Soundfont not found: {self.soundfont_path}")

        # Ensure FluidSynth is installed
        self.check_fluidsynth_installed()

        # Convert MusicXML to MIDI if necessary
        if self.score_path.suffix.lower() == '.musicxml':
            midi_path = self.score_path.with_suffix('.mid')
            self.score_path = self.musicxml_to_midi(self.score_path, midi_path)
            logger.info(f"Converted MusicXML to MIDI: {self.score_path}")

    @staticmethod
    def check_fluidsynth_installed():
        """Raise an error if FluidSynth is not installed."""
        try:
            subprocess.check_output(['fluidsynth', '--version'])
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise RuntimeError("FluidSynth is not installed. Please install it before using this package.")

    @staticmethod
    def musicxml_to_midi(input_path: Path, output_path: Path) -> Path:
        """
        Convert a MusicXML file to MIDI using music21.

        Parameters
        ----------
        input_path : Path
            Path to the MusicXML file.
        output_path : Path
            Path where the MIDI file will be written.

        Returns
        -------
        Path
            The path to the generated MIDI file.
        """
        logger.info("Converting MusicXML to MIDI...")
        score = converter.parse(str(input_path))
        midi_file = midi.translate.streamToMidiFile(score)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # Write the MIDI file to disk
        with output_path.open('wb') as f:
            midi_file.writeFile(f)
        return output_path

    @staticmethod
    def change_midi_tempo(midi_file_path: Path, new_tempo_bpm: float) -> None:
        """
        Change the tempo of a MIDI file in-place.

        Parameters
        ----------
        midi_file_path : Path
            Path to the MIDI file to modify.
        new_tempo_bpm : float
            New tempo in beats per minute (BPM).
        """
        logger.info(f"Changing tempo to {new_tempo_bpm} BPM in {midi_file_path}...")
        microseconds_per_beat = mido.bpm2tempo(new_tempo_bpm)
        mid = mido.MidiFile(str(midi_file_path))
        # Process each track: remove existing tempo messages and insert the new one at the start
        for track in mid.tracks:
            track[:] = [msg for msg in track if msg.type != 'set_tempo']
            track.insert(0, mido.MetaMessage('set_tempo', tempo=microseconds_per_beat, time=0))
        mid.save(str(midi_file_path))
        logger.info(f"Tempo updated and saved to {midi_file_path}")

    def generate_audio(self, output_dir, tempo: float = None, sample_rate: int = 22050) -> None:
        """
        Generate audio files for each instrument in the MIDI score.

        Parameters
        ----------
        output_dir : Path or str
            Directory where the generated audio files will be saved.
        tempo : float, optional
            The tempo (BPM) to set for the MIDI file, by default 120 BPM.
        sample_rate : int, optional
            The sample rate for the generated audio, by default 44100.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create a temporary copy of the MIDI file so that the original file is not modified.
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tempo_temp:
            temp_full_midi = Path(tempo_temp.name)
        shutil.copy(self.score_path, temp_full_midi)
        if tempo is not None:
            # Change the tempo of the temporary MIDI file
            logger.info(f"Setting tempo to {tempo} BPM")
            # Use the change_midi_tempo method to modify the tempo
            self.change_midi_tempo(temp_full_midi, tempo)

        # Load the tempo-modified MIDI file using pretty_midi
        midi_data = pretty_midi.PrettyMIDI(str(temp_full_midi))
        logger.info(f"Loaded MIDI file with {len(midi_data.instruments)} instrument(s)")

        # Process each instrument separately
        for i, instrument in enumerate(midi_data.instruments):
            logger.info(f"Processing instrument {i}...")
            # Create a new MIDI object for this instrument
            instrument_midi = pretty_midi.PrettyMIDI()
            instrument_midi.instruments.append(instrument)
            
            # Use a temporary file for the instrument MIDI
            with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp_file:
                temp_midi_path = Path(tmp_file.name)
            instrument_midi.write(str(temp_midi_path))
            
            # Define the output audio file
            output_audio_file = output_dir / f"instrument_{i}.wav"
            fluidsynth_command = [
                "fluidsynth",
                "-ni",
                str(self.soundfont_path),
                str(temp_midi_path),
                "-F",
                str(output_audio_file),
                "-r",
                str(sample_rate)
            ]
            try:
                subprocess.run(fluidsynth_command, check=True)
                logger.info(f"Generated audio file: {output_audio_file}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error generating audio for instrument {i}: {e}")
            finally:
                # Clean up the temporary instrument MIDI file
                if os.path.exists(temp_midi_path):
                    temp_midi_path.unlink()

        # Clean up the temporary full MIDI file with updated tempo
        if os.path.exists(temp_full_midi):
            temp_full_midi.unlink()


if __name__ == '__main__':
    # Example usage:
    base_dir = Path(__file__).parent
    score = os.path.join('data', 'midi', 'twinkle_twinkle.mid')
    output_dir = os.path.join('data', 'audio', 'twinkle_twinkle', '100bpm')
    SAMPLE_RATE = 44100
    TEMPO = 100

    try:
        generator = AudioGenerator(score_path=score)
        generator.generate_audio(output_dir=output_dir, tempo=TEMPO, sample_rate=SAMPLE_RATE)
    except Exception as e:
        logger.error(e)
