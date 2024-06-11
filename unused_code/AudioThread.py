import pyaudio
import numpy as np
import threading
import time

'''
This class is a template class for a thread that reads in audio from PyAudio.
'''


class AudioThread(threading.Thread):
    def __init__(self, name, starting_chunk_size, process_func, args_before=(), args_after=()):
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
        super(AudioThread, self).__init__()
        self.name = name  # General imports
        self.process_func = process_func
        self.args_before = args_before
        self.args_after = args_after

        self.p = None  # PyAudio vals
        self.stream = None
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.starting_chunk_size = starting_chunk_size
        self.CHUNK = self.starting_chunk_size * self.CHANNELS

        self.on_threshold = 0.3
        self.input_on = False

        self.stop_request = False

        self.data = None

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
                                  frames_per_buffer=self.CHUNK)
        while not self.stop_request:
            time.sleep(1.0)
        self.stop()

    def stop(self):
        """
        When the thread is stopped, this function is called which closes the PyAudio object
        Parameters: nothing
        Returns: nothing
        """
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
            self.input_on = True
        else:
            self.input_on = False

    def callback(self, in_data, frame_count, time_info, flag):
        """
        This function is called whenever PyAudio recieves new audio. It calls process_func to process the sound data
        and stores the result in the field "data".
        This function should never be called directly.
        Parameters: none user-exposed
        Returns: nothing of importance to the user
        """
        numpy_array = np.frombuffer(in_data, dtype=np.float32)
        data = np.zeros(self.starting_chunk_size)
        for i in range(0, self.CHANNELS):
            data += numpy_array[i:self.CHUNK:self.CHANNELS]
        data /= float(self.CHANNELS)
        self.audio_on(data)
        self.data = self.process_func(*self.args_before, data, *self.args_after)
        return None, pyaudio.paContinue
