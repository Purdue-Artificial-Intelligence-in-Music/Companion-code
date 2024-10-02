import pyaudio
import numpy as np
import time
import librosa
import soundfile
from threading import Lock

class AudioBuffer:
    """Thread to save microphone audio to a buffer.

    Parameters
    ----------
    sample_rate : int
        Sample rate of the audio buffer
    channels : int, optional
        Number of channels
    frames_per_buffer : int, optional
        Number of frames per buffer for PyAudio stream : upper limit of frames the object could take before buffer reset
    max_duration: int, optional
        Maximum number of frames in buffer

    Attributes
    ----------
    sample_rate : int
        Sample rate of the audio buffer
    channels : int
        Number of channels
    frames_per_buffer : int
        Number of frames per buffer for PyAudio stream
    length : int
        Maximum number of frames in buffer
    buffer : np.ndarray
        Array containing audio frames
    write_index : int
        Index of the next element in which audio frames will be stored
    read_index : int
        Index of the next element from which audio frames will be read
    count : int
        Number of unread frames in the buffer
    p : pyaudio.PyAudio
        PyAudio object used to create the input stream
    stream : pyaudio.PyAudio.Stream
        Input stream to read audio from microphone
    paused : bool
        If True, read and write operations are paused
    """
    def __init__(self, source: str = None, max_duration: int = 600, sample_rate: int = 44100, channels: int = 1, frames_per_buffer: int = 1024):

        # Params
        self.sample_rate = sample_rate
        self.channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.length = max_duration * self.sample_rate

        self.audio = None
        self.audio_index = 0

        if source is not None:
            # Check for mono audio
            mono = self.channels == 1
            self.audio, _ = librosa.load(source, sr=self.sample_rate, mono=mono)
            # Reshape mono audio. Multi-channel audio should already be in the correct shape
            if mono:
                self.audio = self.audio.reshape((1, -1))
            
        # Create buffer
        self.buffer = np.empty(shape=(self.channels, self.length), dtype=np.float32)

        # Track buffer
        self.write_index = 0
        self.read_index = 0
        self.count = 0  # how much does read and write indeces differ (?)

        # PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.input_device = self.get_input_device()
        print(f'Using input device: {self.p.get_device_info_by_index(self.input_device)["name"]}')

        self.paused = False

        self.lock = Lock()

    def get_input_device(self):
        device_count = self.p.get_device_count()
        for i in range(device_count):
            device_info = self.p.get_device_info_by_index(i)
            channels = device_info['maxInputChannels']
            sample_rate = device_info['defaultSampleRate']
            if channels > 0 and sample_rate == self.sample_rate:
                return i
        return 0

    def write(self, frames: np.ndarray):
        """Write audio frames to buffer.

        Parameters
        ----------
        frames : np.ndarray
            Audio frames to write to the buffer.

        Returns
        -------
        None
        
        """
        # Get the number of frames to write
        num_frames = frames.shape[-1]

        # If the buffer will exceed its length, raise exception
        if self.write_index + num_frames > self.length:
            raise Exception('Error: Not enough space left in buffer')
        
        # Write frames
        with self.lock:
            self.buffer[:, self.write_index:self.write_index + num_frames] = frames
        
        # Increment the write index
        self.write_index += num_frames

        # Increase the count
        self.count += num_frames

    def read(self, num_frames: int) -> np.ndarray:
        """Returns the specified number of frames from the buffer starting at the read index.

        Parameters
        ----------
        num_frames : int
            Number of frames to read from the buffer
        num_frames: int :
            

        Returns
        -------
        np.ndarray
            Array of audio frames with shape (channels, num_frames)
        
        """
        if num_frames > self.count:
            print('AudioBuffer read error')
            raise Exception(f'Error: Attempted to read {num_frames} frames but count is {self.count}')
        
        frames = np.empty((self.channels, num_frames), dtype=np.float32)
        with self.lock:
            frames = self.buffer[:, self.read_index:self.read_index+num_frames]
        
        # Increment the read index
        self.read_index += num_frames

        # Reduce the count
        self.count -= num_frames

        # Return audio frames
        return frames

    def callback(self, in_data, frame_count, time_info, status):
        """Called whenever PyAudio stream receives a new batch of audio frames

        Parameters
        ----------
        in_data : bytes
            
        frame_count : int
            Number of frames that must be returned to keep the audio stream alive
        time_info :
            
        status :
            

        Returns
        -------
        np.ndarray, PortAudio Callback Return Code
            Audio frames that were just written to the buffer.
        
        """
        if self.paused:
            return np.zeros((self.channels, frame_count)), pyaudio.paContinue
        
        if self.audio is not None:
            audio = self.audio[:, self.audio_index:self.audio_index + frame_count]
            self.audio_index += frame_count
        else:
            audio = np.frombuffer(in_data, dtype=np.float32)

        # Reshape the audio into shape (channels, number of frames)
        audio = audio.reshape((self.channels, -1))

        # Write the audio to the buffer
        self.write(audio)

        # If the number of frames is not equal to frame _count, close the stream
        if audio.shape[-1] != frame_count:
            return audio, pyaudio.paComplete
        
        # Continue to the microphone audio stream
        return audio, pyaudio.paContinue
    
    def start(self):
        """Open a PyAudio input stream to read audio data from the microphone."""
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=True,
                                  output=False,
                                  stream_callback=self.callback,
                                  frames_per_buffer=self.frames_per_buffer,
                                  input_device_index=self.input_device)
        
    def is_active(self) -> bool:
        """Return True if the stream is active. False otherwise. """
        if self.stream is None:
            return False
        return self.stream.is_active()
    
    def get_time(self) -> int:
        """Get the length of the audio written to the buffer in seconds. """
        return self.write_index / self.sample_rate
    
    def pause(self):
        """Pause read and write operations"""
        self.paused = True

    def unpause(self):
        """Unpause read and write operations"""
        self.paused = False

    def stop(self):
        """Close the PyAudio stream and terminate the PyAudio object."""
        self.stream.close()
        self.p.terminate()

    def get_audio(self) -> np.ndarray:
        """Get all the audio written to the buffer so far. """
        return self.buffer[:, :self.write_index]

    def save(self, path):
        """

        Parameters
        ----------
        path : str
            Filepath to save the audio to.
            

        Returns
        -------
            None
        
        """
        audio = self.get_audio()
        audio = audio.reshape((-1, ))
        soundfile.write(path, audio, self.sample_rate)

        
if __name__ == '__main__':
    source = 'data/audio/bach/live/variable_tempo.wav'
    buffer = AudioBuffer(source=None,
                         max_duration=600,
                         sample_rate=44100,
                         channels=1,
                         frames_per_buffer=1024)
    buffer.start()

    while not buffer.is_active():
        time.sleep(0.01)

    print('Mic is active')
    try:
        while buffer.is_active():
            time.sleep(0.1)
    except KeyboardInterrupt:
        buffer.stop()

    buffer.save('mic_test.wav')
