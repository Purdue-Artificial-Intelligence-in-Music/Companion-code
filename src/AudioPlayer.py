import librosa
import pyaudio
import time
import numpy as np
from librosa import core
from librosa.core import convert

def normalize_audio(audio):
    """
    Normalize audio data to the range [-1, 1].

    Parameters:
    audio (np.ndarray): The audio data to be normalized.

    Returns:
    np.ndarray: The normalized audio data.
    """
    return audio / np.max(np.abs(audio))

class AudioPlayer:
    """Class to play audio file

    Parameters
    ----------
    path : str
        Path to audio file
    sample_rate : int, optional
        Sample rate for audio file
    channels : int, optional
        Number of channels for audio file
    frames_per_buffer : int, optional
        Number of frames per buffer for PyAudio stream
    playback_rate : float, optional
        Multiplier for playback speed of audio file
    
    Attributes
    ----------
    path : str
        Path to audio file
    sample_rate : int
        Sample rate for audio file
    channels : int
        Number of channels for audio file
    frames_per_buffer : int
        Number of frames per buffer for PyAudio stream
    playback_rate : float
        Multiplier for playback speed of audio file
    audio : np.ndarray
        Numpy array containing audio frames of shape (channels, number of frames)
    audio_len : int
        Number of audio frames in audio
    p : 
        PyAudio object
    stream :
        PyAudio stream
    index : int
        Index of next audio frame to play
    paused : bool
        True if audio playback is paused. False otherwise.
    
    """
    def __init__(self, path: str, playback_rate: int = 1.0, sample_rate: int = 16000, channels: int = 1, 
                 n_fft: int = 4096, win_length: int = 4096, hop_length: int = 1024, frames_per_buffer: int = 1024):
        
        # AUDIO
        self.path = path
        self.sample_rate = sample_rate
        self.channels = channels
        self.n_fft = n_fft  # length of signal after padding with zeros
        self.win_length = win_length
        self.hop_length = hop_length
        self.frames_per_buffer = frames_per_buffer

        # Check for mono audio
        mono = channels == 1

        # Load the audio
        self.audio, self.sample_rate = librosa.load(path, sr=sample_rate, mono=mono)

        # Normalize audio
        self.audio = normalize_audio(self.audio)

        # Reshape mono audio. Multi-channel audio should already be in the correct shape
        if mono:
            self.audio = self.audio.reshape((1, -1))

        # Get number of frames in audio
        self.audio_len = self.audio.shape[-1]

        # Phase Vocoder
        # The audio is windowed to create overlapping frames of size window_length
        # The degree of overlap is determined by hop_length
        # These frames are then padded with zeros to reach a length of n_fft

        # Calculate the Short-Time Fourier Transform 
        self.stft = core.stft(self.audio, 
                              n_fft=n_fft,
                              hop_length=hop_length,
                              win_length=win_length)
        
        shape = list(self.stft.shape)
        shape[-1] *= 3
        self.stft_stretch = np.zeros(shape, dtype='complex_')
        self.t = 0  # index in stft_stretch

        # Expected phase advance in each bin per frame
        self.phi_advance = hop_length * convert.fft_frequencies(sr=2 * np.pi, n_fft=n_fft)

        # Phase accumulator; initialize to the phase of the first frame of the STFT
        self.phase_acc = np.angle(self.stft[..., 0])

        # Index of current phrame in the STFT
        self.k = 0

        # PYAUDIO
        self.p = pyaudio.PyAudio()

        # Open an output stream
        self.stream = None
        
        self.index = 0
        self.playback_rate = playback_rate
        self.paused = False

        self.output_log = np.empty((channels, 0))

        self.omega = hop_length / win_length

    def get_next_frames(self):
        if self.k >= self.stft.shape[-1]-1:
            return None

        columns = self.stft[..., int(self.k) : int(self.k + 2)]

        # Weighting for linear magnitude interpolation
        alpha = np.mod(self.k, 1.0)
        mag = (1.0 - alpha) * np.abs(columns[..., 0]) + alpha * np.abs(columns[..., 1])
        # Use the magnitude and accumulated phase to generate a phasor
        self.stft_stretch[..., self.t] = mag * np.exp(1j * self.phase_acc)
        self.t += 1

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

        if self.t >= num_hops:
            stretched_audio = librosa.core.istft(self.stft_stretch[..., self.t-num_hops:self.t],
                                                 hop_length=self.hop_length,
                                                 win_length=self.win_length,
                                                 n_fft=self.n_fft,
                                                 dtype=self.audio.dtype, 
                                                 length=length)
            
            segment = stretched_audio[..., :self.frames_per_buffer]
        else:
            segment = np.zeros((self.channels, self.frames_per_buffer))


        # Increment the frame index
        self.k += self.playback_rate
        self.index = self.k * self.hop_length

        # Return time-stretched audio
        return segment

    def callback(self, in_data, frame_count, time_info, status):
        """Called when PyAudio stream needs audio frames to play

        Parameters
        ----------
        in_data : 
            
        frame_count : int
            Number of audio frames that must be returned
        time_info :
            
        status :
            

        Returns
        -------
        np.ndarray, PortAudio Callback Return Code
            Audio frames to be played by PyAudio stream
        """
        # If len(data) is less than requested frame_count, PyAudio automatically
        # assumes the stream is finished, and the stream stops.
        
        if self.paused:
            return np.zeros((self.channels, frame_count)), pyaudio.paContinue

        # Time stretch the audio based on the playback rate
        audio_segment = self.get_next_frames()

        if audio_segment is None:
            return np.zeros((self.channels, frame_count)), pyaudio.paComplete
        
        self.output_log = np.append(self.output_log, audio_segment, axis=1)
        
        # no more audio to read
        if audio_segment.shape[-1] < frame_count:
            return audio_segment, pyaudio.paComplete
        
        return audio_segment, pyaudio.paContinue
    
    def start(self):
        """Open a PyAudio output stream. """

        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=False,
                                  output=True,
                                  stream_callback=self.callback,
                                  frames_per_buffer=self.frames_per_buffer)
        
    def is_active(self):
        """Return True if the PyAudio stream is active. False otherwise. """
        if self.stream is None:
            return False
        return self.stream.is_active()
    
    def pause(self):
        """Pause but do not kill the thread."""
        self.paused = True

    def unpause(self):
        """Unpause the thread."""
        self.paused = False

    def stop(self):
        """Close the PyAudio stream and terminate the PyAudio object. """
        self.stream.close()
        self.p.terminate()

    def get_time(self):
        return self.k * self.hop_length / self.sample_rate

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import soundfile

    player = AudioPlayer(path='data/bach/synthesized/track1.wav', 
                         sample_rate=16000,
                         channels=1,
                         frames_per_buffer=1024,
                         playback_rate=1,
                         n_fft=4096,
                         win_length=4096,
                         hop_length=1024)
    player.start()

    # the hop_length needs to match the frames_per_buffer
    # n_fft and window_length need to be at least double that
    # n_fft must be greater than or equal to window_length
    
    while not player.is_active():
        time.sleep(0.01)

    try:
        while player.is_active():
            # player.playback_rate = 1 + 0.5 * np.sin(time.time())
            time.sleep(0.1)
    except KeyboardInterrupt:
        player.stop()

    audio = player.output_log.reshape((-1, ))
    plt.plot(audio)
    plt.show()
    soundfile.write('test.wav', audio, 16000)