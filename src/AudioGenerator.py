from midi_ddsp import load_pretrained_model
from midi_ddsp.utils.training_utils import set_seed
import midi_ddsp
from ddsp_funcs import *
import scipy
import os

class AudioGenerator:
    def __init__(self, midi_file):
        self.midi_file = midi_file

        set_seed(1)
        package_dir = os.path.dirname(os.path.realpath(midi_ddsp.__file__))
        print(package_dir)
        self.synthesis_generator, self.expression_generator = load_pretrained_model()
        self.sample_rate = 16000

    def save_as_wav(self, filepath, sample_rate, audio):
        audio = audio.reshape((-1,))
        audio = (audio/np.max(audio) * (2 ** 31 - 1))

        audio = audio.astype(np.int32)
        scipy.io.wavfile.write(filepath, sample_rate, audio)

    def generate_audio(self, output_path, midi_program=41, inst_num=0):
        audio, conditioning_df, midi_synth_params = generate_audio_from_midi(self.synthesis_generator, 
                                                                             self.expression_generator, 
                                                                             self.midi_file, 
                                                                             midi_program, 
                                                                             inst_num)
        audio = audio.numpy()
        self.save_as_wav(output_path, self.sample_rate, audio)



if __name__ == '__main__':
    generator = AudioGenerator(midi_file='midi_files/buns.mid')
    generator.generate_audio(output_path='audio_files/buns_violin.wav', midi_program=41, inst_num=0)
    generator.generate_audio(output_path='audio_fiels/buns_viola.wav', midi_program=42, inst_num=1)
