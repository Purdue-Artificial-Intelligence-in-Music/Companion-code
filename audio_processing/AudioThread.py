import pyaudio
import numpy as np
import threading
import time

'''
This class is a template class for a thread that reads in audio from PyAudio.
'''


class AudioThreadWithBufferPorted(threading.Thread):
    def __init__(self, name, rate, starting_chunk_size, process_func, args_before=(), args_after=()):
        """
        Initializes an AudioThread.
        Parameters:
            name: the name of the thread
            starting_chunk_size: an integer representing the chunk size in samples
            process_func: the function to be called as a callback when new audio is received from PyAudio
            args_before: a tuple of arguments for process_func to be put before the sound array
            args_after: a tuple of arguments for process_func to be put after the sound array
        Returns: nothing
        """
        super(AudioThreadWithBufferPorted, self).__init__()
        self.name = name  # General imports
        self.process_func = process_func
        self.args_before = args_before
        self.args_after = args_after
        self.dtype = np.float32
        self.p = None  # PyAudio vals
        self.stream = None
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = rate
        self.starting_chunk_size = starting_chunk_size
        self.CHUNK = self.starting_chunk_size * self.CHANNELS

        self.on_threshold = 0.001
        self.input_on = False
        self.last_time_on = 0.0

        self.stop_request = False
        self.data = None

        self.pred_length = 8
        self.desired_buffer_size = self.pred_length * self.RATE * self.CHANNELS
        self.buffer_size = self.desired_buffer_size + self.CHUNK - (self.desired_buffer_size % self.CHUNK)
        self.audio_buffer = np.zeros(self.buffer_size, dtype=self.dtype)  # set a zero array
        self.buffer_index = 0
        self.input_device_index = 1

    def set_args_before(self, a):
        """
        Changes the arguments before the sound array when process_func is called.
        Parameters: a: the arguments
        Returns: nothing
        """
        self.args_before = a

    def set_args_after(self, a):
        """
        Changes the arguments after the sound array when process_func is called.
        Parameters: a: the arguments
        Returns: nothing
        """
        self.args_after = a

    def run(self):
        """
        When the thread is started, this function is called which opens the PyAudio object
        and keeps the thread alive.
        Parameters: nothing
        Returns: nothing
        """
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  output=False,
                                  stream_callback=self.callback,
                                  frames_per_buffer=self.CHUNK,
                                  )
        while not self.stop_request:
            #continue
            time.sleep(1.0)
        self.stop()

    def stop(self):
        """
        When the thread is stopped, this function is called which closes the PyAudio object
        Parameters: nothing
        Returns: nothing
        """
        self.stop_request = True #In case you call stop()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def audio_on(self, audio):
        """
        Takes an audio input array and sets an instance variable saying whether the input is playing or not.
        Parameters: audio: the audio input
        Returns: nothing
        """
        val_sum = 0.0
        for val in audio:
            val_sum += val * val
        val_sum /= len(audio)
        if val_sum > self.on_threshold:
            self.last_time_on = time.time()
            self.input_on = True
        else:
            if time.time() - self.last_time_on > 5.0:
                self.input_on = False

    def get_last_samples(self, n):
        """
        Returns the last n samples from the buffer.
        Parameters: n: number of samples
        Returns: the last n samples from the buffer (as a numpy array)
        """
        return self.audio_buffer[max(self.buffer_index - n, 0):self.buffer_index]

    def callback(self, in_data, frame_count, time_info, flag):
        """
        This function is called whenever PyAudio recieves new audio. It calls process_func to process the sound data
        and stores the result in the field "data".
        This function should never be called directly.
        Parameters: none user-exposed
        Returns: nothing of importance to the user
        """
        numpy_array = np.frombuffer(in_data, dtype=self.dtype)
        data = np.zeros(self.starting_chunk_size, dtype=self.dtype)
        for i in range(0, self.CHANNELS):
            data += numpy_array[i:self.CHUNK:self.CHANNELS]
        data /= np.float64(self.CHANNELS)
        self.audio_on(data/np.float64(2**15))
        data = self.dtype(data)
        # self.data = self.process_func(*self.args_before, data, *self.args_after)

        if not self.buffer_index + len(data) <= self.buffer_size:
            # Overflow: Reset or handle as per your requirement
            # self.buffer_index = 0
            self.audio_buffer[:self.buffer_size - len(data)] = self.audio_buffer[len(data):self.buffer_size]
            self.buffer_index -= len(data)
            # print("shifting buffer")

        self.audio_buffer[self.buffer_index:self.buffer_index + len(data)] = data
        self.buffer_index += len(data)

        #print(self.buffer_index)

        #print("Added data")
        # self.get_last_samples(self.pred_length * self.RATE)
        #if self.input_on:
        # self.data = self.process_func(*self.args_before, self.get_last_samples(self.pred_length * self.RATE),
        #                               *self.args_after)
        self.data = self.process_func(*self.args_before, data, *self.args_after) #this seems to work better?
        
        # This is where process_func in threaded_parent_with_buffer.py is called from
        # if self.wav_index + self.CHUNK <= len(self.wav_data):
        # self.data = self.process_func(self, data, self.wav_data[self.wav_index:self.wav_index + self.CHUNK])
        #    self.wav_index += self.CHUNK
        # else:
        #    self.wav_index = 0
        # self.data = self.process_func(self, data, self.wav_data[self.wav_index:self.wav_index + self.CHUNK])
        return None, pyaudio.paContinue