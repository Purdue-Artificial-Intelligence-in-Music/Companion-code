from midi_ddsp import load_pretrained_model
from midi_ddsp.utils.training_utils import set_seed
from ddsp_funcs import *
import scipy


class AudioGenerator:
    def __init__(self, midi_file):
        self.midi_file = midi_file

        set_seed(1)
        self.synthesis_generator, self.expression_generator = load_pretrained_model()
        self.sample_rate = 16000

    def save_as_wav(self, filepath, sample_rate, audio):
        audio = audio.reshape((-1,))
        audio = (audio/np.max(audio) * (2 ** 31 - 1))

        audio = audio.astype(np.int32)
        scipy.io.wavfile.write(filepath, sample_rate, audio)

    def generate_audio(self, output_path, instrument='violin', inst_num=0):
        audio, conditioning_df, midi_synth_params = generate_audio_from_midi(self.synthesis_generator, 
                                                                             self.expression_generator, 
                                                                             self.midi_file, 
                                                                             instrument, 
                                                                             inst_num=inst_num)
        audio = audio.numpy()
        self.save_as_wav(output_path, self.sample_rate, audio)



if __name__ == '__main__':
    generator = AudioGenerator(midi_file='buns.mid')
    generator.generate_audio(output_path='buns_violin.wav', instrument='violin', inst_num=0)
    generator.generate_audio(output_path='buns_viola.wav', instrument='viola', inst_num=1)
