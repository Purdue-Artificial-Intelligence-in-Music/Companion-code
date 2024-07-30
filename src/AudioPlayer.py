import librosa
import pyaudio
import time
import numpy as np
from librosa import core
from librosa.core import convert


def normalize_angle(angle):
    """
    Normalize the given angle to be between -pi and pi.

    Parameters:
    angle (float): The angle in radians to be normalized.

    Returns:
    float: The normalized angle in radians between -pi and pi.
    """
    return np.arctan2(np.sin(angle), np.cos(angle))

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
    def __init__(self, path, sample_rate=16000, channels=1, frames_per_buffer=1024, playback_rate=1.0, n_fft=2048, window_length=2048, hop_length=512):
        
        # AUDIO
        self.path = path
        self.sample_rate = sample_rate
        self.channels = channels

        # Check for mono audio
        mono = channels == 1

        # Load the audio
        self.audio, self.sample_rate = librosa.load(path, sr=sample_rate, mono=mono)

        # Reshape mono audio. Multi-channel audio should already be in the correct shape
        if mono:
            self.audio = self.audio.reshape((1, -1))

        self.audio_len = self.audio.shape[-1]

        # Phase Vocoder
        self.n_fft = n_fft
        self.window_length = window_length
        self.hop_length = hop_length

        # Calculate the Short-Time Fourier Transform 
        self.D = core.stft(self.audio, 
                           n_fft=n_fft,
                           hop_length=hop_length,
                           win_length=window_length)

        if hop_length is None:
            hop_length = int(n_fft // 4)

        # Expected phase advance in each bin per frame
        self.phi_advance = hop_length * convert.fft_frequencies(sr=2 * np.pi, n_fft=n_fft)

        # Magnitude of each frame in the STFT
        self.magnitudes = np.abs(self.D)

        # Phase of each frame in the STFT
        self.phases = np.angle(self.D)

        # Phase accumulator; initialize to the phase of the first frame of the STFT
        self.phase_acc = self.phases[..., 0]

        self.previous_phase = self.phase_acc

        # Phse differnce between frames in the STFT
        self.phase_differences = np.diff(self.phases, axis=-1)

        # Index of current phrame in the STFT
        self.k = 0

        # PYAUDIO
        self.p = pyaudio.PyAudio()

        # Open an output stream
        self.stream = None
        
        self.index = 0
        self.frames_per_buffer = frames_per_buffer
        self.playback_rate = playback_rate
        self.paused = False

        self.output_log = np.empty((channels, 0))

    def fade_in(self, audio, num_frames):
        """Fades in an audio segment.

        Parameters
        ----------
        audio : np.ndarray
            Audio to fade in.
        num_frames : int
            Number of frames to fade in.

        Returns
        -------
        None
        
        """
        num_frames = min(audio.shape[1], num_frames)
        fade_curve = np.log(np.linspace(1, np.e, num_frames))

        for channel in audio[:, :num_frames]:
            channel *= fade_curve

    def fade_out(self, audio, num_frames):
        """Fades out an audio segment.

        Parameters
        ----------
        audio : np.ndarray
            Audio to fade in.
        num_frames : int
            Number of frames to fade in.

        Returns
        -------
        None
        
        """
        num_frames = min(audio.shape[1], num_frames)
        start = audio.shape[1] - num_frames
        fade_curve = np.log(np.linspace(np.e, 1, num_frames))

        for channel in audio[:, start:]:
            channel *= fade_curve

    def get_next_frames(self, rate):
        if self.k >= self.D.shape[-1]:
            return None
        
        # Get the magnitude of the next frame in the stft
        mag = self.magnitudes[..., int(self.k)]
        # Use the magnitude and accumulated phase to 
        # stft_stretch = util.phasor(self.phase_acc, mag=mag)

        d_stretch = mag * np.exp(1j * self.phase_acc)
        d_stretch = d_stretch[..., np.newaxis]

        # Accumulate the phase
        if self.k < self.phase_differences.shape[-1]:
            self.phase_acc += self.phase_differences[..., self.k]
            self.phase_acc = normalize_angle(self.phase_acc)
        self.k += rate

        len_stretch = int(self.window_length / rate)
        y_stretch = core.istft(d_stretch, 
                               hop_length=self.hop_length,
                               win_length=self.window_length,
                               n_fft=self.n_fft,
                               dtype=self.audio.dtype, 
                               length=len_stretch)

        return y_stretch

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
        
        # start = max(0, self.index)
        # end = min(self.index + 5 * self.playback_rate * frame_count, self.audio_len)

        # # Increment the wav_index based on the playback rate
        # self.index += self.playback_rate * frame_count
        # audio = self.audio[:, int(start):int(end)]
        
        # Time stretch the audio based on the playback rate
        # stretched_audio = librosa.effects.time_stretch(y=audio, rate=self.playback_rate, n_fft=int(self.playback_rate * frame_count))  # get audio
        stretched_audio = self.get_next_frames(self.playback_rate)

        if stretched_audio is None:
            return np.zeros((self.channels, frame_count)), pyaudio.paComplete
        
        # Reshaped the stretched audio (necessary if there is only one channel)
        # stretched_audio = stretched_audio.reshape((self.channels, -1))

        # Get exactly enough frames to fill the PyAudio buffer
        audio_segment = stretched_audio[:, :frame_count]
        
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

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import soundfile

    player = AudioPlayer(path='audio/ode_to_joy/track0.wav', 
                         sample_rate=22050,
                         channels=1,
                         frames_per_buffer=1024,
                         playback_rate=1,
                         n_fft=2048,
                         window_length=2048,
                         hop_length=1024)
    player.start()
    
    while not player.is_active():
        time.sleep(0.01)

    try:
        while player.is_active():
            time.sleep(0.1)
    except KeyboardInterrupt:
        player.stop()

    print(player.audio.shape)
    print(player.output_log.shape)
    audio = player.output_log.reshape((-1, ))
    soundfile.write('test.wav', audio, 22050)

    plt.plot(audio)
    plt.show()