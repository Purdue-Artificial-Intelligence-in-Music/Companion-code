from midi_ddsp import load_pretrained_model, synthesize_midi
from ddsp_funcs import generate_audio_from_midi
from midi_ddsp.utils.midi_synthesis_utils import synthesize_mono_midi
from midi_ddsp.utils.audio_io import save_wav
from xml2midi_conversion import process_score
import os
import pretty_midi


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
    def __init__(self, path):
        if path.endswith('.musicxml'):
            title = os.path.basename(path)[:-9]
            output_path = os.path.join('midi', title + '.mid')
            if not os.path.exists('midi'):
                os.makedirs('midi')
            self.midi_file = process_score(input_path=path, output_path=output_path)
        elif path.endswith('.mid'):
            self.midi_file = path
        else:
            raise Exception('Error: AudioGenerator path must be to MusicXML or MIDI file')
        
        self.synthesis_generator, self.expression_generator = load_pretrained_model()

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
            midi_length = pretty_midi.PrettyMIDI(self.midi_file).get_end_time()
            speed_rate = midi_length / target_length

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output = synthesize_midi(synthesis_generator=self.synthesis_generator, 
                                 expression_generator=self.expression_generator, 
                                 midi_file=self.midi_file,
                                 speed_rate=speed_rate)
        
        for key in output['stem_audio'].keys():
            audio = output['stem_audio'][key]
            output_path = os.path.join(output_dir, f'track{key}.wav')
            save_wav(audio, output_path, 16000)


if __name__ == '__main__':
    generator = AudioGenerator(path='scores/Air_on_the_G_String.musicxml')
    generator.generate_audio(output_dir='audio/Air_on_the_G_String', speed_rate=0.5)
