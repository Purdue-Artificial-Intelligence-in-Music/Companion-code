import pyaudio
import numpy as np
import threading
import time
import librosa
from typing import Callable

from Counter import *

'''
This class is a template class for a thread that reads in audio fromxPyAudio and stores it in a buffer.

This is version 2 of the code.
'''


class AudioBuffer(threading.Thread):
    def __init__(self, name, frames_per_buffer: int, wav_file: str, process_func: Callable, process_func_args=(), debug_prints = False):
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

        All params directly passed to PyAudio are in ALL CAPS.
        """
        super(AudioBuffer, self).__init__()
        self.name = name  # General imports
        self.process_func = process_func
        self.process_func_args = process_func_args

        # User-editable parameters for the audio system
        self.wav_data, self.RATE = librosa.load(wav_file)  # Audio file and sample rate of wav audio

        self.dtype = self.wav_data.dtype
        if self.dtype == np.float32:
            self.FORMAT = pyaudio.paFloat32
        elif self.dtype == np.int16:
            self.FORMAT = pyaudio.paInt16
        elif self.dtype == np.int32:
            self.FORMAT = pyaudio.paInt32
        if len(self.wav_data.shape) == 1:
            self.wav_data = self.wav_data.reshape((-1, 1))
        self.CHANNELS = self.wav_data.shape[1]
        
        self.FRAMES_PER_BUFFER = frames_per_buffer
        
        if debug_prints:
            print("Audio init parameters:\nFormat = %s\ndtype = %s\nChannels = %d\nFrames per buffer = %d" % (self.FORMAT, self.dtype, self.CHANNELS, self.FRAMES_PER_BUFFER))
            print("Shape of wav_data: ", self.wav_data.shape)

        # Helper function vals
        self.on_threshold = 0.5  # RMS threshold for audio_on

        # PyAudio
        self.p = None  # PyAudio object
        self.stream = None  # PyAudio stream

        # Instance vals
        self.output_array = None  # Most recent output data
        self.input_on = False  # True if audio is being played into PyAudio, False otherwise, set by audio_on()
        self.stop_request = False   # True if AudioThreadWithBuffer needs to be killed, False otherwise

        # input wav
        self.wav_index = 0  # Where we are in the wav file (in samples)
        self.wav_len = len(self.wav_data)
        self.wav_transform = self.transform_func(self.wav_data)
        if debug_prints:
            print("Wav transform shape = %s" % (str(self.wav_transform.shape)))
        # Make sure to reshape input data

        # set audio buffer
        self.buffer_elements = 50  # number of CHUNKs the buffer should store
        self.buffer_size = self.buffer_elements * self.FRAMES_PER_BUFFER  # desired buffer size in samples
        # round to nearest multiple of self.CHUNK
        # self.buffer_size = self.desired_buffer_size + self.FRAMES_PER_BUFFER - (self.desired_buffer_size % self.FRAMES_PER_BUFFER)
        self.audio_buffer = np.zeros((self.buffer_size, self.CHANNELS), dtype=self.dtype)  # set a zero array
        self.buffer_index = 0  # current last sample stored in buffer
        self.buffer_filled = False # True if buffer has been filled all the way, False otherwise

        if debug_prints:
            print("Buffer elements: %d\nBuffer size (in samples): %d\nBuffer size (in seconds): %.2f" % (self.buffer_elements, self.buffer_size, self.buffer_size / float(self.RATE)))

        self.transform_buffer = np.zeros((self.buffer_elements, *self.wav_transform.shape[1:]), dtype=self.dtype)
        self.transform_buffer_index = 0
        self.transform_buffer_filled = False

        if debug_prints:
            print("Transform buffer shape %s" % (str(self.transform_buffer.shape)))

        self.sample_counter = Counter()


    def transform_func(self, audio: np.ndarray) -> np.ndarray:
        if len(audio) < self.FRAMES_PER_BUFFER:
            audio = np.concatenate((audio, np.zeros((self.FRAMES_PER_BUFFER - audio.shape[0], audio.shape[1]), dtype=audio.dtype)))
        transform_output = librosa.feature.chroma_cqt(y=audio.T, sr=self.RATE, hop_length=self.FRAMES_PER_BUFFER)
        transform_output = transform_output.swapaxes(0, 2)
        if transform_output.shape[0] == 1:
            transform_output.reshape(transform_output.shape[1:])
        return transform_output

    def set_process_func_args(self, a = ()):
        """
        Changes the arguments after the sound array when process_func is called.
        Parameters: a: the arguments
        Returns: nothing
        """
        self.process_func_args = a

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
                                  frames_per_buffer=self.FRAMES_PER_BUFFER)
        # Ensure that this is the expected size
        while not self.stop_request:
            time.sleep(1.0)
        self.stop()

    def stop(self):
        """
        When the thread is stopped, this function is called which closes the PyAudio object
        Parameters: nothing
        Returns: nothing
        """
        # self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.stop_request = True

    def audio_on(self, audio: np.array):
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

    def get_last_samples(self, n: int):
        """
        Returns the last n samples from the buffer, or the maximum possible elements if there aren't enough recorded yet.
        Parameters: n: number of samples
        Returns: the last n samples from the buffer (as a numpy array)
        """
        # return self.audio_buffer[max(self.buffer_index - n, 0):self.buffer_index]
        if n > self.buffer_size:
            n = self.buffer_size
        if not self.buffer_filled and n > self.buffer_index:
            n = self.buffer_index
        if n > self.buffer_index:
            n_from_end = n - self.buffer_index + 1
            return np.concatenate((self.audio_buffer[self.buffer_size - n_from_end:], self.audio_buffer[0:self.buffer_index]), axis=1)
        return self.audio_buffer[self.buffer_index - n + 1:self.buffer_index]

    def get_last_transform(self, n: int):
        """
        Returns the last n transform frames from the buffer, or the maximum possible elements if there aren't enough recorded yet.
        Parameters: n: number of samples
        Returns: the last n samples from the buffer (as a numpy array)
        """
        if n > self.buffer_elements:
            n = self.buffer_elements
        if not self.buffer_filled and n > self.buffer_index:
            n = self.buffer_index
        if n > self.buffer_index:
            n_from_end = n - self.buffer_index + 1
            return np.concatenate((self.transform_buffer[self.buffer_elements - n_from_end:], self.transform_buffer[0:self.buffer_index]), axis=1)
        return self.transform_buffer[self.buffer_index - n + 1:self.buffer_index]
    
    def get_range_samples(self, m: int, n: int):
        """
        Returns the range of samples from the mth most recent sample (inclusive) to the nth most recent sample (exclusive), where n > m, or the maximum possible elements
        if there aren't enough recorded yet.
        Parameters: 
        m: the last sample you want the function to return from the buffer
        n: the first sample you want the function to return from the buffer
        Returns: see above (a numpy array)
        """
        if n > self.buffer_size:
            n = self.buffer_size
        if not self.buffer_filled and n > self.buffer_index:
            n = self.buffer_index
        if m >= n:
            return np.empty((self.CHANNELS,0), dtype=self.dtype)
        if n > self.buffer_index:
            n_from_end = n - self.buffer_index + 1
            if m > self.buffer_index:
                m_from_end = m - self.buffer_index
                return self.audio_buffer[self.buffer_size - n_from_end:self.buffer_size - m_from_end]
            else:
                return np.concatenate((self.audio_buffer[self.buffer_size - n_from_end:], self.audio_buffer[0:self.buffer_index - m]), axis=1)
        return self.audio_buffer[self.buffer_index - n + 1:self.buffer_index - m] 
    
    def get_range_transforms(self, m: int, n: int):
        """
        Returns the range of transforms from the mth most recent transform (inclusive) to the nth most recent transform (exclusive), where n > m, or the maximum possible elements
        if there aren't enough recorded yet.
        Parameters: 
        m: the last sample you want the function to return from the buffer
        n: the first sample you want the function to return from the buffer
        Returns: see above (a numpy array)
        """
        if n > self.buffer_elements:
            n = self.buffer_elements
        if not self.buffer_filled and n > self.buffer_index:
            n = self.buffer_index
        if m >= n:
            return np.empty((self.CHANNELS,0), dtype=self.dtype)
        if n > self.buffer_index:
            n_from_end = n - self.buffer_index + 1
            if m > self.buffer_index:
                m_from_end = m - self.buffer_index
                return self.transform_buffer[self.buffer_elements - n_from_end:self.buffer_elements - m_from_end]
            else:
                return np.concatenate((self.transform_buffer[self.buffer_elements - n_from_end:], self.transform_buffer[0:self.buffer_index - m]), axis=1)
        return self.transform_buffer[self.buffer_index - n + 1:self.buffer_index - m] 
            
    def callback(self, in_data, frame_count, time_info, flag):
        """
        This function is called whenever PyAudio recieves new audio. It calls process_func to process the sound data
        and stores the result in the field "data".
        This function should never be called directly.
        Parameters: none user-exposed
        Returns: new audio for PyAudio to play through speakers.
        """
        
        input_array = np.frombuffer(in_data, dtype=self.dtype)
        L = len(input_array)
        output_array = np.zeros(self.FRAMES_PER_BUFFER, dtype=self.dtype)

        # Reshaping code to correct channels
        input_array = np.reshape(input_array, (self.CHANNELS, -1)).T
       
        # Check if audio is on and update instance val
        self.audio_on(input_array)

        # Add audio to buffer
        if self.buffer_index + L > self.buffer_size: # If buffer will overflow
            self.audio_buffer[self.buffer_index:] = input_array[0:self.buffer_length-self.buffer_index] # Add the first portion to the end
            self.audio_buffer[0:L-(self.buffer_length-self.buffer_index)] = input_array[self.buffer_length-self.buffer_index:] # Add the rest at the front
            self.buffer_filled = True
        else:
            self.audio_buffer[self.buffer_index:self.buffer_index + L] = input_array # Add it all at once
        self.buffer_index = (self.buffer_index + L) % self.buffer_size # Increment the buffer counter

        self.sample_counter.subtract_all(L)  # Update sample counter

        # Process transform and add to transform buffer
        self.transform_buffer[self.transform_buffer_index] = self.process_func(input_array)  # Process the input info
        if self.transform_buffer_index == self.buffer_elements - 1:  # Once the buffer is filled, mark it as filled
            self.transform_buffer_filled = True
        self.transform_buffer_index = (self.transform_buffer_index + 1) % self.buffer_elements  # Increment the buffer counter

        # This is where process_func in threaded_parent_with_buffer.py is called from
        if self.wav_index + self.FRAMES_PER_BUFFER <= self.wav_len:  # If there is enough data in wav
            self.output_array = self.process_func(self, input_array, 
                                          self.wav_data[self.wav_index:self.wav_index + self.FRAMES_PER_BUFFER], 
                                          *self.process_func_args) # Call process_func
            self.wav_index += self.FRAMES_PER_BUFFER
        else:  # Send the rest of the wav to process_func and kill the PyAudio stream
            self.output_array = self.process_func(self, input_array, 
                                          self.wav_data[self.wav_index:], 
                                          *self.process_func_args)
            self.stop()
            return self.output_array.flatten(order='F'), pyaudio.paAbort
        if self.stop_request:
            self.stop()
            return self.output_array.flatten(order='F'), pyaudio.paAbort
        return self.output_array.flatten(order='F'), pyaudio.paContinue
