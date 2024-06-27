from threading import Thread
import pyaudio
import numpy as np
import time
import librosa


mic_audio, sr = librosa.load('audio_files/buns_violin.wav', sr=22050, mono=True)
# mic_audio = librosa.effects.time_stretch(y=mic_audio, rate=0.5)
mic_audio = mic_audio.reshape((1, -1))
index = 0
    

class AudioBuffer(Thread):
    def __init__(self, sample_rate=22050, channels=1, frames_per_buffer=1024, num_chunks=100):
        super(AudioBuffer, self).__init__()

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

        self.daemon=True
        self.filled = False

    def insert(self, frames):
        L = frames.shape[-1]

        # If buffer will overflow
        if self.write_index + L > self.length:
            # Add the first portion to the end
            self.buffer[:, self.write_index:] = frames[:, :self.length-self.write_index]
            # Add the rest at the front
            self.buffer[:, :L-(self.length-self.write_index)] = frames[:, self.length-self.write_index:]
            self.filled = True
        # If the buffer will not overflow
        else:
            # Add it all at once
            self.buffer[:, self.write_index:self.write_index + L] = frames

        if self.write_index == self.length:
            self.filled = True
            
        # Increment the write index
        self.write_index = (self.write_index + L) % self.length

        # Increment the count
        self.count = min(self.count + L, self.length)

    def read(self, num_frames):
        if num_frames > self.length:
            raise Exception(f'Error: Attempted to read {num_frames} frames from buffer of length {self.length}')
        
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
        if num_frames > self.write_index:
            # If the buffer has been filled, wrap around to the end of the array
            if self.filled:
                # calculate the number of frames needed from the end of the array
                frames_from_end = num_frames - self.write_index
                # concatenate the fromaes from the end with the frames from the start to the buffer index
                return np.concatenate((self.buffer[:, -frames_from_end:], self.buffer[:, :self.write_index]), axis=1)
            # if the buffer has not been filled at least once, the frames on the end are not valid
            return self.buffer[:, :self.write_index]
        
        # if n is less than the buffer index
        return self.buffer[:, self.write_index - num_frames:self.write_index]

    def callback(self, in_data, frame_count, time_info, status):
        audio = np.frombuffer(in_data, dtype=np.float32)

        global mic_audio, index
        audio = mic_audio[:, index:index+self.frames_per_buffer]
        index += self.frames_per_buffer
        audio = audio.reshape((self.channels, -1))
        self.insert(audio)
        if audio.shape[-1] != frame_count:
            return audio, pyaudio.paComplete
        return audio, pyaudio.paContinue

    def run(self):
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=True,
                                  output=False,
                                  stream_callback=self.callback,
                                  frames_per_buffer=self.frames_per_buffer)
        
    def is_active(self):
        if self.stream is None:
            return False
        return self.stream.is_active()
    
    def stop(self):
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
