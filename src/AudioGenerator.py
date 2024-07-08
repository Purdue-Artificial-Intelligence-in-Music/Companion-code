from midi_ddsp import load_pretrained_model
from midi_ddsp.utils.training_utils import set_seed
from ddsp_funcs import *
import scipy
import os
from xml2midi_conversion import process_score


class AudioGenerator:
    def __init__(self, path):
        if path.endswith('.musicxml'):
            self.midi_file = process_score(path)
        elif path.endswith('.mid'):
            self.midi_file = path
        else:
            raise Exception('Error: AudioGenerator path must be to MusicXML or MIDI file')

        set_seed(1)
        self.synthesis_generator, self.expression_generator = load_pretrained_model()
        self.sample_rate = 16000

    def save_as_wav(self, filepath, sample_rate, audio):
        audio = audio.reshape((-1,))
        audio = (audio/np.max(audio) * (2 ** 31 - 1))

        audio = audio.astype(np.int32)
        scipy.io.wavfile.write(filepath, sample_rate, audio)

    def generate_audio(self, output_path, midi_program=41, inst_num=0):
        output_dir = os.path.dirname(output_path)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        audio, conditioning_df, midi_synth_params = generate_audio_from_midi(self.synthesis_generator, 
                                                                             self.expression_generator, 
                                                                             self.midi_file, 
                                                                             midi_program, 
                                                                             inst_num)
        audio = audio.numpy()
        self.save_as_wav(output_path, self.sample_rate, audio)



if __name__ == '__main__':
    generator = AudioGenerator(path='ode_to_joy.musicxml')
    generator.generate_audio(output_path='audio_files/ode_to_joy/solist.wav', midi_program=41, inst_num=0)
    generator.generate_audio(output_path='audio_files/ode_to_joy/accompanist.wav', midi_program=42, inst_num=1)
