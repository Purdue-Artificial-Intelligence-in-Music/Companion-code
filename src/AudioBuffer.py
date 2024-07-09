from threading import Thread
import pyaudio
import numpy as np
import time


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
    paused : bool
        If True, read and write operations are paused

    """
    def __init__(self, sample_rate: int = 22050, channels: int = 1, frames_per_buffer: int = 1024, num_chunks: int = 100):
        # Initialize parent class
        super(AudioBuffer, self).__init__(daemon=True)

        # Params
        self.sample_rate = sample_rate 
        self.channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.num_chunks = num_chunks

        # Create buffer
        self.length = num_chunks * frames_per_buffer
        self.buffer = np.zeros((channels, self.length))

        # Track buffer
        self.write_index = 0
        self.read_index = 0
        self.count = 0

        # PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None

        self.paused = False

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

        # If the buffer will overflow
        if self.write_index + num_frames > self.length:
            # Write frames to the end of the buffer
            self.buffer[:, self.write_index:] = frames[:, :self.length-self.write_index]
            # Wrap around to the front of the buffer 
            self.buffer[:, :num_frames-(self.length-self.write_index)] = frames[:, self.length-self.write_index:]
        # If the buffer will not overflow
        else:
            # Write all frames at once
            self.buffer[:, self.write_index:self.write_index + num_frames] = frames
            
        # Increment the write index
        self.write_index = (self.write_index + num_frames) % self.length

        # Increase the count. The count can never be greater than the length of the buffer
        self.count = min(self.count + num_frames, self.length)

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
        
        # If reading past the end of the buffer
        if self.read_index + num_frames > self.length:
            # Read frames until the end of the buffer is reached
            temp = self.read_index
            frames_from_end = self.buffer[:, temp:]
            temp = (self.read_index + num_frames) % self.length

            # Wrap around to the front of the buffer
            frames_from_start = self.buffer[:, :temp]

            # Concatenate frames from end and start of buffer
            frames = np.concatenate((frames_from_end, frames_from_start), axis=1)
        else:
            # Read frames all at once
            frames = self.buffer[:, self.read_index:self.read_index+num_frames]
        
        # Increment the read index
        self.read_index = (self.read_index + num_frames) % self.length

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
            Microphone audio frames

        """
        if self.paused:
            return np.zeros((self.channels, frame_count)), pyaudio.paContinue
        
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
    
    def run(self):
        """Open a PyAudio input stream to read audio data from the microphone. """
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
    
    def audio_on(self, audio: np.array):
        """Takes an audio input array and sets an instance variable saying whether the input is playing or not.

        Parameters
        ----------
        audio : np.array
            An array containing audio data
        
        Returns
        -------
        None
            
        """
        audio = audio.astype(np.float64)
        val_sum = 0.0
        for col in audio.T:
            val = np.dot(col, col)
            val_sum += val
        val_sum /= len(audio)
        return val_sum > self.on_threshold
    
    def pause(self):
        """Pause read and write operations"""
        self.paused = True

    def unpause(self):
        """Unpause read and write operations"""
        self.paused = False

    def stop(self):
        """Close the PyAudio stream and terminate the PyAudio object. """
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
