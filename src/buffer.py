from threading import Thread
import pyaudio
import numpy as np
import time
import librosa


mic_audio, sr = librosa.load('soloist.wav', sr=22050, mono=True)
mic_audio = librosa.effects.time_stretch(y=mic_audio, rate=0.5)
mic_audio = mic_audio.reshape((1, -1))
index = 0


class AudioBuffer(Thread):
    """Thread to save microphone audio to a circular buffer.

    Parameters
    ----------
    sample_rate : int
        Sample rate of the audio buffer
    channels : int, optional
        Number of channels
    frames_per_buffer : int, optional
        Number of frames per buffer for PyAudio stream
    num_chunks : int, optional
        Number of audio chunks in audio buffer. Each chunk is of size frames_per_buffer

    Attributes
    ----------
    sample_rate : int
        Sample rate of the audio buffer
    channels : int
        Number of channels
    frames_per_buffer : int
        Number of frames per buffer for PyAudio stream
    num_chunks : int
        Number of audio chunks in audio buffer. Each chunk is of size frames_per_buffer
    length : int
        Number of frames in the buffer. Equal to num_chunks * frames_per_buffer
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
    filled : bool
        True if the buffer has been completely filled at least once

    """
    def __init__(self, sample_rate: int = 22050, channels: int = 1, frames_per_buffer: int = 1024, num_chunks: int = 100):
        super(AudioBuffer, self).__init__()
        self.daemon = True

        self.sample_rate = sample_rate 
        self.channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.num_chunks = num_chunks
        self.length = num_chunks * frames_per_buffer
        self.buffer = np.zeros((channels, self.length))
        self.write_index = 0
        self.read_index = 0
        self.count = 0

        self.p = pyaudio.PyAudio()
        self.stream = None

    def write(self, frames: np.ndarray):
        """

        Parameters
        ----------
        frames : np.ndarray
            Audio frames to write to the buffer.

        Returns
        -------
        None

        """
        L = frames.shape[-1]

        # If buffer will overflow
        if self.write_index + L > self.length:
            # Add the first portion to the end
            self.buffer[:, self.write_index:] = frames[:, :self.length-self.write_index]
            # Add the rest at the front
            self.buffer[:, :L-(self.length-self.write_index)] = frames[:, self.length-self.write_index:]
        # If the buffer will not overflow
        else:
            # Add it all at once
            self.buffer[:, self.write_index:self.write_index + L] = frames
            
        # Increment the write index
        self.write_index = (self.write_index + L) % self.length

        # Increment the count
        self.count = min(self.count + L, self.length)

    def read(self, num_frames: int) -> np.ndarray:
        """Returns the specified number of frames from the buffer starting at the read index.

        Parameters
        ----------
        num_frames : int
            Number of frames to read from the buffer

        Returns
        -------
        np.ndarray
            Audio frames from the buffer

        """
        if num_frames > self.count:
            raise Exception(f'Error: Attempted to read {num_frames} frames but count is {self.count}')
        
        if self.read_index + num_frames > self.length:
            temp = self.read_index
            frames_from_end = self.buffer[:, temp:]
            temp = (self.read_index + num_frames) % self.length
            frames_from_start = self.buffer[: :temp]
            frames = np.concatenate((frames_from_end, frames_from_start), axis=1)
        else:
            frames = self.buffer[:, self.read_index:self.read_index+num_frames]
        
        self.read_index = (self.read_index + num_frames) % self.length
        self.count -= num_frames
        return frames

    def callback(self, in_data, frame_count, time_info, status):
        """Called whenever PyAudio stream

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
            Microphone audio frames

        """
        # audio = np.frombuffer(in_data, dtype=np.float32)

        global mic_audio, index
        audio = mic_audio[:, index:index+frame_count]
        index += frame_count
        audio = audio.reshape((self.channels, -1))
        self.write(audio)
        if audio.shape[-1] != frame_count:
            return audio, pyaudio.paComplete
        return audio, pyaudio.paContinue

    def run(self):
        """Open a PyAudio input stream to read audio data from the microphone"""
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=True,
                                  output=False,
                                  stream_callback=self.callback,
                                  frames_per_buffer=self.frames_per_buffer)
        
    def is_active(self):
        """Return True if the PyAudio stream is active. Otherwise, return False. """
        if self.stream is None:
            return False
        return self.stream.is_active()
    
    def stop(self):
        """Close the PyAudio stream and terminate the PyAudio object """
        self.stream.close()
        self.p.terminate()

        
if __name__ == '__main__':
    buffer = AudioBuffer(sample_rate=22050,
                         channels=1,
                         frames_per_buffer=1024,
                         num_chunks=100)
    buffer.start()

    while not buffer.is_active():
        time.sleep(0.01)

    try:
        while buffer.is_active():
            time.sleep(0.1)
    except KeyboardInterrupt:
        buffer.stop()
        buffer.join()
