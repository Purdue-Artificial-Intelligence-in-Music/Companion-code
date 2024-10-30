import librosa
import numpy as np
from librosa import core
from librosa.core import convert


def normalize_audio(audio):
    """Normalize audio data to the range [-1, 1].

    Parameters
    ----------
    audio : np.ndarray
        Array containing audio data.

    Returns
    -------
    np.ndarray
        The normalized audio data.

    """
    return audio / np.max(np.abs(audio))


class PhaseVocoder:
    """Class to time scale audio using the Phase Vocoder algorithm.

    Parameters
    ----------
    path : str
        Path to audio file.
    playback_rate : int, optional
        Speed multiplier for audio playback.
    sample_rate : int, optional
        Sample rate for audio file.
    channels : int, optional
        Number of channels for audio file.
    n_fft : int, optional
        Length of the windowed signal after padding with zeros.
    win_length : int, optional
        Length of the windowed signal before padding with zeros.
    hop_length : int, optional
        Number of audio samples between adjacent windows.
    frames_per_buffer : int, optional
        Number of frames per buffer

    Attributes
    ----------
    path : str
        Path to audio file
    playback_rate : float
        Multiplier for playback speed of audio file
    sample_rate : int
        Sample rate for audio file
    channels : int
        Number of channels for audio file
    n_fft : int
        Length of the windowed signal after padding with zeros.
    win_length : int
        Length of the windowed signal before padding with zeros.
    hop_length : int
        Number of audio samples between adjacent windows.
    audio : np.ndarray
        Numpy array containing audio frames of shape (channels, number of frames)
    stream : pyaudio.Stream
        PyAudio stream
    index : int
        Index of next audio frame to play
    """

    def __init__(self, path: str, playback_rate: int = 1.0, sample_rate: int = 44100, channels: int = 1,
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

        # Phase Vocoder
        # The audio is windowed to create overlapping frames of size window_length
        # The degree of overlap is determined by hop_length
        # These frames are then padded with zeros to reach a length of n_fft

        # Calculate the Short-Time Fourier Transform
        self.stft = core.stft(self.audio,
                              n_fft=n_fft,
                              hop_length=hop_length,
                              win_length=win_length)

        # Index of current frame in the STFT
        self.stft_index = 0

        shape = list(self.stft.shape)
        shape[-1] *= 3  # Support up to 3x time stretching
        self.stft_stretch = np.zeros(shape, dtype='complex_')
        self.stretch_index = 0  # index in stft_stretch

        # Expected phase advance in each bin per frame
        self.phi_advance = hop_length * \
            convert.fft_frequencies(sr=2 * np.pi, n_fft=n_fft)

        # Phase accumulator - initialize to the phase of the first frame of the STFT
        self.phase_acc = np.angle(self.stft[..., 0])

        # Index in the audio
        self.audio_index = 0

    def get_next_frames(self) -> np.ndarray:
        """ Time scales audio frames according to the playback rate

        Returns
        -------
            Array of audio frames with shape (channels, hop_length)
        """
        if self.stft_index >= self.stft.shape[-1]-1:
            return None

        # Get the next 2 columns of the STFT
        columns = self.stft[..., int(
            self.stft_index): int(self.stft_index + 2)]

        # Weighting for linear magnitude interpolation
        alpha = np.mod(self.stft_index, 1.0)
        mag = (1.0 - alpha) * \
            np.abs(columns[..., 0]) + alpha * np.abs(columns[..., 1])

        # Use the magnitude and accumulated phase to generate a phasor
        # Store that phasor in the stretched STFT
        self.stft_stretch[..., self.stretch_index] = mag * \
            np.exp(1j * self.phase_acc)
        self.stretch_index += 1

        # Accumulate the phase
        dphase = np.angle(columns[..., 1]) - \
            np.angle(columns[..., 0]) - self.phi_advance
        dphase = dphase - 2.0 * np.pi * np.round(dphase / (2.0 * np.pi))
        self.phase_acc += self.phi_advance + dphase

        # Convert back to time domain
        num_hops = 10
        if self.playback_rate >= 1:
            length = int(
                round(num_hops * self.hop_length / self.playback_rate))
        else:
            length = None

        if self.stretch_index >= num_hops:
            stretched_audio = librosa.core.istft(self.stft_stretch[..., self.stretch_index-num_hops:self.stretch_index],
                                                 hop_length=self.hop_length,
                                                 win_length=self.win_length,
                                                 n_fft=self.n_fft,
                                                 dtype=self.audio.dtype,
                                                 length=length)

            segment = stretched_audio[..., :self.hop_length]
        else:
            segment = np.zeros((self.channels, self.hop_length))

        # Increment the frame index
        self.stft_index += self.playback_rate
        self.audio_index = self.stft_index * self.hop_length

        # Return time-stretched audio
        return segment

    def get_time(self) -> int:
        """Get the timestamp in the audio being played."""
        return self.audio_index / self.sample_rate

    def set_playback_rate(self, playback_rate: float):
        """Set the playback rate of the audio."""
        self.playback_rate = playback_rate


if __name__ == '__main__':
    import os
    from audio_buffer import AudioBuffer

    reference = os.path.join('data', 'audio', 'bach',
                             'synthesized', 'solo.wav')

    # n_fft and window_length need to be at least double that
    # n_fft must be greater than or equal to window_length

    phase_vocoder = PhaseVocoder(path=reference,
                                 sample_rate=44100,
                                 channels=1,
                                 playback_rate=1,
                                 n_fft=8192,
                                 win_length=8192,
                                 hop_length=2048)

    buffer = AudioBuffer(sample_rate=44100, channels=1)

    while True:
        phase_vocoder.set_playback_rate(2)
        frames = phase_vocoder.get_next_frames()
        if frames is None:
            break
        buffer.write(frames)

    buffer.save('phase_vocoder_output.wav')
