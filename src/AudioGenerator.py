from midi_ddsp import load_pretrained_model, synthesize_midi
from midi_ddsp_local.utils.training_utils import set_seed
from midi_ddsp.utils.audio_io import save_wav
import os
import pretty_midi
from music21 import *
import numpy as np


class AudioGenerator:
    """Class to generate audio from MusicXML and MIDI scores

    Parameters
    ----------
    path : str
        Path to MusicXML or MIDI score

    Attributes
    ----------
    midi_file : str
        Path to MIDI file
    synthesis_generator : MIDIExpressionAE
        MIDI-DDSP synthesis generator object
    expression_generator : ExpressionGenerator
        MIDI-DDSP expression generator object
        
    """
    def __init__(self, path: str):

        # If the input is a MusicXML file, convert to MIDI
        if path.endswith('.musicxml'):
            # Get the title of the MusicXML file without the extension
            title = os.path.basename(path)[:-9]

            # Get the directory of the MusicXML file
            dir = os.path.dirname(path)

            # Construct output path for MIDI file
            output_path = os.path.join(dir, title + '.mid')

            # Convert MusicXML to MIDI
            self.midi_file = self.xml_to_midi(input_path=path, output_path=output_path)
        
        # If it is a MIDI file, no conversion is necessary
        elif path.endswith('.mid'):
            self.midi_file = path

        # If the input file is neither MusicXML or MIDI, raise an exception.
        else:
            raise Exception('Error: AudioGenerator path must be to MusicXML or MIDI file')
        
        # set the MIDI-DDSP seed
        set_seed(3)

        # Load the model
        self.synthesis_generator, self.expression_generator = load_pretrained_model()

    def xml_to_midi(self, input_path, output_path):
        score = converter.parse(input_path)
        mf = midi.translate.streamToMidiFile(score)
        mf.open(output_path, "wb")
        mf.write()
        mf.close()
        return output_path

    def generate_audio(self, output_dir, target_length=None):
        """

        Parameters
        ----------
        output_path : str
            Path for generated audio file

        Returns
        -------
        None
        
        """

        if target_length is None:
            speed_rate = 1.0
        else:
            mf = pretty_midi.PrettyMIDI(self.midi_file)
            midi_length = mf.get_end_time()
            speed_rate = midi_length / target_length

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output = synthesize_midi(synthesis_generator=self.synthesis_generator, 
                                 expression_generator=self.expression_generator, 
                                 midi_file=self.midi_file,
                                 speed_rate=speed_rate,
                                 use_fluidsynth=False)
        
        for key in output['stem_audio'].keys():
            audio = output['stem_audio'][key]
            audio /= np.max(audio)
            output_path = os.path.join(output_dir, f'track{key}.wav')
            save_wav(audio, output_path, 16000)


if __name__ == '__main__':

    SCORE = 'data/c_major/tempo_variation.mid'
    SOURCE = 'data/bach/live/constant_tempo.wav'
    OUTPUT_DIR = 'data/c_major/live'
    SAMPLE_RATE = 16000

    # y, _ = librosa.load(path=SOURCE, sr=SAMPLE_RATE, mono=True)
    # target_length = len(y) / SAMPLE_RATE
    target_length = 12
    generator = AudioGenerator(path=SCORE)
    generator.generate_audio(output_dir=OUTPUT_DIR, target_length=target_length)
