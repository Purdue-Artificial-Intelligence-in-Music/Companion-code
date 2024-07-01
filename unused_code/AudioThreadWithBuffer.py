import pyaudio
import numpy as np
import threading
import time
import wavio
import wave

'''
This class is a template class for a thread that reads in audio from PyAudio and stores it in a buffer.
'''


class AudioThreadWithBuffer(threading.Thread):
    def __init__(self, name, starting_chunk_size, process_func, wav_file, args_before=(), args_after=()):
        """
        Initializes an AudioThreadWithBuffer object (a thread that takes audio, stores it in a buffer,
        optionally processes it, and returns new audio to play back).
        Parameters:
            name: the name of the thread
            starting_chunk_size: an integer representing the chunk size in samples
            process_func: the function to be called as a callback when new audio is received from PyAudio
            wav_file: path to a wav file to pass to process_func
            args_before: a tuple of arguments for process_func to be put before the sound array
            args_after: a tuple of arguments for process_func to be put after the sound array
        Returns: nothing
        """
        super(AudioThreadWithBuffer, self).__init__()
        self.name = name  # General imports
        self.process_func = process_func
        self.args_before = args_before
        self.args_after = args_after

        # User-editable parameters
        self.dtype = np.int16
        self.FORMAT = pyaudio.paInt16  # Leave on paInt16 if no good reason to change it
        self.CHANNELS = 1  # Leave set to 1 (currently broken if set to 2)
        self.RATE = wave.open(wav_file, 'rb').getframerate()  # Sample rate of both the input and output audio, set to sample rate of the wav you feed in
        self.starting_chunk_size = starting_chunk_size  # Set this in constructor
        self.CHUNK = self.starting_chunk_size * self.CHANNELS
        self.buffer_elements = 30  # number of buffer chunks to store
        self.wav_data_obj = wavio.read(wav_file)  # Source
        self.on_threshold = 0.5  # RMS threshold for audio_on

        # PyAudio
        self.p = None  # PyAudio vals
        self.stream = None

        # Instance vals
        self.data = None
        self.input_on = False
        self.stop_request = False

        # input wav
        self.wav_data = self.wav_data_obj.data[:, 0]
        self.wav_index = 0

        # basic bit conversion for wav
        self.wav_data = self.wav_data.astype(np.float64)
        x = self.wav_data[0:1000000].max()
        mult = np.float64(1)
        while x < 2 ** 7:
            x *= 2 ** 8
            mult *= 2 ** 8
        while x > 2 ** 15:
            x /= 2 ** 8
            mult /= 2 ** 8
        self.wav_data *= mult
        self.wav_data = self.wav_data.astype(np.int16)


        # set buffer
        self.pred_length = 4  # number of seconds of audio the buffer should store
        self.desired_buffer_size = self.pred_length * self.RATE * self.CHANNELS  # desired buffer size in samples
        # round to nearest multiple of self.CHUNK
        self.buffer_size = self.desired_buffer_size + self.CHUNK - (self.desired_buffer_size % self.CHUNK)
        self.audio_buffer = np.zeros(self.buffer_size, dtype=self.dtype)  # set a zero array
        self.buffer_index = 0  # current last sample stored in buffer

        # hysteresis for gain control
        self.last_gain = 0.0
        self.last_time_updated = time.time()

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
                                  output=True,  # output audio
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
        audio = audio.astype(np.float64)
        val_sum = 0.0
        for val in audio:
            val_sum += val * val
        val_sum /= len(audio)
        if val_sum > self.on_threshold:
            self.input_on = True
        else:
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
        Returns: new audio for PyAudio to play through speakers.
        """
        numpy_array = np.frombuffer(in_data, dtype=self.dtype)
        data = np.zeros(self.starting_chunk_size, dtype=np.float64)
        for i in range(0, self.CHANNELS):
            data += numpy_array[i:self.CHUNK:self.CHANNELS]
        data /= np.float64(self.CHANNELS)
        self.audio_on(data / np.float64(2 ** 15))
        data = self.dtype(data)
        self.audio_on(numpy_array)
        # print(numpy_array[0:10])
        data = numpy_array
        # Add audio to buffer
        if not self.buffer_index + len(data) <= self.buffer_size:
            # Overflow: Reset or handle as per your requirement
            # self.buffer_index = 0
            self.audio_buffer[:self.buffer_size - len(data)] = self.audio_buffer[len(data):self.buffer_size]
            self.buffer_index -= len(data)
        self.audio_buffer[self.buffer_index:self.buffer_index + len(data)] = data
        self.buffer_index += len(data)

        # This is where process_func in threaded_parent_with_buffer.py is called from
        if self.wav_index + self.CHUNK <= len(self.wav_data):
            self.data = self.process_func(self, data, self.wav_data[self.wav_index:self.wav_index + self.CHUNK])
            self.wav_index += self.CHUNK
        else:
            self.wav_index = 0
            self.data = self.process_func(self, data, self.wav_data[self.wav_index:self.wav_index + self.CHUNK])
        if self.stop_request:
            return self.data, None
        return self.data, pyaudio.paContinue
