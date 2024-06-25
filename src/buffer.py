from threading import Thread
import pyaudio
import numpy as np
import time

class AudioBuffer(Thread):
    def __init__(self, sample_rate=22050, channels=1, frames_per_buffer=1024, num_chunks=50):
        super(AudioBuffer, self).__init__()

        self.sample_rate = sample_rate
        self.channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.num_chunks = num_chunks
        self.length = num_chunks * frames_per_buffer
        self.buffer = np.zeros((channels, self.length))
        self.index = 0
        self.filled = False
        self.stop_request = False

        self.p = None
        self.stream = None

    def insert(self, frames):
        L = frames.shape[-1]

        # If buffer will overflow
        if self.index + L > self.length:
            # Add the first portion to the end
            self.buffer[:, self.index:] = frames[:, :self.length-self.index]
            # Add the rest at the front
            self.buffer[:, :L-(self.length-self.index)] = frames[:, self.length-self.index:]
            self.filled = True
        # If the buffer will not overflow
        else:
            # Add it all at once
            self.buffer[:, self.index:self.index + L] = frames

        # Increment the index
        self.index = (self.index + L) % self.length

    def get_last_frames(self, num_frames: int):
        """Returns the last n frames from the buffer, or the maximum possible elements if there aren't enough recorded yet.

        Parameters
        ----------
        num_frames: int
            Number of frames to get from the buffer

        Returns
        -------
        np.ndarray
            Array containing the n most recent frames from the audio buffer.

        """

        # n cannot be greater than the size of the buffer
        num_frames = min(num_frames, self.length)

        # if n is greater than the buffer index
        if num_frames > self.index:
            # If the buffer has been filled, wrap around to the end of the array
            if self.filled:
                # calculate the number of frames needed from the end of the array
                frames_from_end = num_frames - self.index
                # concatenate the fromaes from the end with the frames from the start to the buffer index
                return np.concatenate((self.buffer[:, -frames_from_end:], self.buffer[:, :self.index]), axis=1)
            # if the buffer has not been filled at least once, the frames on the end are not valid
            return self.buffer[:, :self.index]
        
        # if n is less than the buffer index
        return self.buffer[:, self.index - num_frames:self.index]

    def callback(self, in_data, frame_count, time_info, status):
        audio = np.frombuffer(in_data)
        self.insert(audio)
        return audio, pyaudio.paContinue

    def run(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                 channels=self.channels,
                                 rate=44100,
                                 input=True,
                                 output=False,
                                 stream_callback=self.callback,
                                 frames_per_buffer=1024)
        
        while not self.stop_request:
            time.sleep(0.1)
        
    def stop(self):
        self.stream.close()
        self.p.terminate()
        self.stop_request = True
        
if __name__ == '__main__':
    buffer = AudioBuffer()
    buffer.start()

    try:
        while not buffer.stop_request:
            time.sleep(0.1)
    except KeyboardInterrupt:
        buffer.stop()
        buffer.join()
