from midi_ddsp import load_pretrained_model
from midi_ddsp.utils.midi_synthesis_utils import synthesize_mono_midi
from midi_ddsp.utils.audio_io import save_wav
from xml2midi_conversion import process_score
import os


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
            self.midi_file = process_score(input_path=path, output_path=f'midi/{title}.mid')
        elif path.endswith('.mid'):
            self.midi_file = path
        else:
            raise Exception('Error: AudioGenerator path must be to MusicXML or MIDI file')

        self.synthesis_generator, self.expression_generator = load_pretrained_model()

    def generate_audio(self, output_path, midi_program=41, instrument_id=0):
        """

        Parameters
        ----------
        output_path : str
            Path for generated audio file
        midi_program : int
            MIDI program number
             (Default value = 41)
        instrument_id : int
            Select instrument in MIDI file
             (Default value = 0) 

        Returns
        -------
        None
        
        """
        output_dir = os.path.dirname(output_path)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        midi_audio, midi_control_params, midi_synth_params, conditioning_df = synthesize_mono_midi(synthesis_generator=self.synthesis_generator,
                                                                                                   expression_generator=self.expression_generator,
                                                                                                   midi_file=self.midi_file,
                                                                                                   instrument_id=instrument_id,
                                                                                                   output_dir=None,
                                                                                                   pitch_offset=0,
                                                                                                   display_progressbar=True)
        save_wav(midi_audio[0].numpy(), output_path, 16000)


if __name__ == '__main__':
    generator = AudioGenerator(path='ode_to_joy.musicxml')
    generator.generate_audio(output_path='audio/ode_to_joy/solist.wav', midi_program=41, instrument_id=0)
    generator.generate_audio(output_path='audio/ode_to_joy/accompanist.wav', midi_program=42, instrument_id=1)
