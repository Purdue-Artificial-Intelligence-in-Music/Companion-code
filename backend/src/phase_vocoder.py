import librosa
import numpy as np
from librosa import core
from librosa.core import convert


def normalize_audio(audio):
    """Normalize audio data to the range [-1, 1]."""
    return audio / np.max(np.abs(audio))


class PhaseVocoder:
    def __init__(self, path: str, playback_rate: float = 1.0, sample_rate: int = 44100, channels: int = 1,
                 n_fft: int = 8192, win_length: int = 8192, hop_length: int = 2048):

        # AUDIO
        self.path = path
        self.playback_rate = playback_rate
        self.sample_rate = sample_rate
        self.channels = channels
        self.n_fft = n_fft
        self.win_length = win_length
        self.hop_length = hop_length

        # Check for mono audio
        mono = channels == 1

        # Load the audio
        self.audio, self.sample_rate = librosa.load(
            path, sr=sample_rate, mono=mono)

        # Normalize audio
        self.audio = normalize_audio(self.audio)

        # Reshape mono audio. Multi-channel audio should already be in the correct shape
        if mono:
            self.audio = self.audio.reshape((1, -1))

        # Calculate the Short-Time Fourier Transform
        self.stft = core.stft(self.audio,
                              n_fft=n_fft,
                              hop_length=hop_length,
                              win_length=win_length,
                              window='hann')

        # Index of current frame in the STFT
        self.stft_index = 0

        shape = list(self.stft.shape)
        shape[-1] *= 3  # Support up to 3x time stretching
        self.stft_stretch = np.zeros(shape, dtype='complex_')
        self.stretch_index = 0  # index in stft_stretch

        # Expected phase advance in each bin per frame
        self.phi_advance = hop_length * convert.fft_frequencies(sr=sample_rate, n_fft=n_fft)

        # Phase accumulator - initialize to the phase of the first frame of the STFT
        self.phase_acc = np.angle(self.stft[..., 0])

        # Index in the audio
        self.audio_index = 0

    def get_next_frames(self) -> np.ndarray:
        """ Time scales audio frames according to the playback rate."""
        if self.stft_index >= self.stft.shape[-1] - 1:
            return None

        # Get the next 2 columns of the STFT
        columns = self.stft[..., int(self.stft_index): int(self.stft_index + 2)]

        # Weighted Magnitude Interpolation
        alpha = np.mod(self.stft_index, 1.0)
        mag = (1.0 - alpha) * np.abs(columns[..., 0]) + alpha * np.abs(columns[..., 1])

        # Use the magnitude and accumulated phase to generate a phasor
        self.stft_stretch[..., self.stretch_index] = mag * np.exp(1j * self.phase_acc)
        self.stretch_index += 1

        # Accumulate the phase
        dphase = np.angle(columns[..., 1]) - np.angle(columns[..., 0]) - self.phi_advance
        dphase = dphase - 2.0 * np.pi * np.round(dphase / (2.0 * np.pi))
        self.phase_acc += self.phi_advance + dphase

        # Convert back to time domain
        num_hops = 10
        if self.playback_rate >= 1:
            length = int(round(num_hops * self.hop_length / self.playback_rate))
        else:
            length = None

        if self.stretch_index >= num_hops:
            # Perform ISTFT on a segment of the stretched STFT
            stretched_audio = librosa.core.istft(self.stft_stretch[..., self.stretch_index - num_hops:self.stretch_index],
                                                 hop_length=self.hop_length,
                                                 win_length=self.win_length,
                                                 window='hann',
                                                 length=length)

            segment = stretched_audio[..., :self.hop_length]
        else:
            segment = np.zeros((self.channels, self.hop_length))

        # Increment the frame index
        self.stft_index += self.playback_rate
        self.audio_index += int(self.hop_length * self.playback_rate)

        # Return time-stretched audio
        return segment

    def get_time(self) -> float:
        """Get the timestamp in the audio being played."""
        return self.audio_index / self.sample_rate

    def set_playback_rate(self, playback_rate: float):
        """Set the playback rate of the audio."""
        self.playback_rate = playback_rate


if __name__ == '__main__':
    import os
    from audio_buffer import AudioBuffer

    reference = os.path.join('data', 'audio', 'air_on_the_g_string',
                             'synthesized', 'solo.wav')

    phase_vocoder = PhaseVocoder(path=reference,
                                 sample_rate=44100,
                                 channels=1,
                                 playback_rate=1,
                                 n_fft=8192,
                                 win_length=8192,
                                 hop_length=2048)

    buffer = AudioBuffer(sample_rate=44100, channels=1)

    while True:
        phase_vocoder.set_playback_rate(1)
        frames = phase_vocoder.get_next_frames()
        print(phase_vocoder.get_time())
        if frames is None:
            break
        buffer.write(frames)

    buffer.save('phase_vocoder_output.wav')
