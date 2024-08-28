
import numpy as np
import librosa
import soundfile
from librosa import core
from librosa.core import convert
import matplotlib.pyplot as plt

class PhaseVocoder:
    def __init__(self, audio, n_fft, win_length, hop_length):
        self.audio = audio
        self.n_fft = n_fft
        self.win_length = win_length
        self.hop_length = hop_length

        self.audio /= np.max(np.abs(self.audio))
        self.audio = self.audio.reshape((1, -1))

        # calculate stft
        self.stft = librosa.core.stft(y=self.audio, n_fft=n_fft, hop_length=hop_length, win_length=win_length)

        # Expected phase advance in each bin
        self.phi_advance = hop_length * convert.fft_frequencies(sr=2 * np.pi, n_fft=n_fft)

        self.phase_accumulator = np.angle(self.stft[..., 0])
        self.k = 0
        self.omega = hop_length / win_length

        shape = list(self.stft.shape)
        shape[-1] *= 3
        self.stft_stretch = np.zeros(shape, dtype='complex_')
        self.t = 0

        self.output_signal = np.zeros((self.audio.shape[0], self.audio.shape[-1] * 4))
        self.output_index = 0

    def step(self, rate):
        if self.k >= self.stft.shape[-1] - 1:
            return False

        # Get the next two frames from the STFT
        columns = self.stft[..., int(self.k) : int(self.k + 2)]

        # Weighting for linear magnitude interpolation
        alpha = np.mod(self.k, 1.0)
        
        # Interpolate between the two frames based on the value of k
        mag = (1.0 - alpha) * np.abs(columns[..., 0]) + alpha * np.abs(columns[..., 1])

        # Construct new phasor using the interpolated magnitude and accumulated phase
        phasor = mag * np.exp(1j * self.phase_accumulator)
        self.stft_stretch[..., self.t] = phasor
        self.t += 1

        # Accumulate the phase for the next iteration
        dphase = np.angle(columns[..., 1]) - np.angle(columns[..., 0]) - self.phi_advance
        dphase = dphase - 2.0 * np.pi * np.round(dphase / (2.0 * np.pi))
        self.phase_accumulator += self.phi_advance + dphase

        self.k += rate

        # Convert phasor to time domain signal
        # len_stretch = int(round(3 * self.hop_length / rate))
        if self.t >= 3:
            stretched_audio = librosa.core.istft(self.stft_stretch[..., self.t-3:self.t],
                                                hop_length=self.hop_length,
                                                win_length=self.win_length,
                                                n_fft=self.n_fft,
                                                dtype=self.audio.dtype)
            
            # plt.plot(stretched_audio.reshape((-1, )))
            # plt.show()
            segment = stretched_audio[..., -self.hop_length:]
            
            start = self.output_index
            end = start + segment.shape[-1]

            self.output_signal[..., start:end] += segment
            self.output_index += self.hop_length

        return True


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    audio, sr = librosa.load('audio/moonlight_sonata.wav', sr=22050)
    print('audio shape:', audio.shape)
    pv = PhaseVocoder(audio=audio, n_fft=2048, win_length=2048, hop_length=512)

    rate = 0.5
    while pv.step(rate):
       continue

    output = pv.output_signal.reshape((-1, ))[..., :pv.output_index]

    # print(pv.stft_stretch[..., :pv.t].shape)
    # length = int(pv.t * pv.hop_length / rate)
    # print('length:', length)
    # output = librosa.core.istft(pv.stft_stretch[..., :pv.t],
    #                             hop_length=pv.hop_length,
    #                             win_length=pv.win_length,
    #                             n_fft=pv.n_fft,
    #                             dtype=pv.audio.dtype)
    # print(output.shape)
    # output = output.reshape((-1, ))
    # plt.plot(output)
    # plt.show()
    soundfile.write('test.wav', output, 22050)
    