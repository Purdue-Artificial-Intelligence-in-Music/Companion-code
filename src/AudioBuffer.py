import pyaudio
import numpy as np
import threading
import time
import librosa
from typing import Callable
from BeatNet_local.BeatNet_files import BeatNet_for_audio_arr
from Counter import *
import pytsmod
import soundfile
import matplotlib.pyplot as plt

'''
This class is a template class for a thread that reads in audio fromxPyAudio and stores it in a buffer.

This is version 2 of the code.
'''


class AudioBuffer(threading.Thread):
    def __init__(self, name: str, 
                 frames_per_buffer: int = 1024, 
                 process_func: Callable = None, 
                 wav_file: str = None, 
                 process_func_args=(), 
                 calc_transforms = False, 
                 calc_beats = False, 
                 run_counter = False,
                 kill_after_finished = True,
                 time_stretch = False,
                 sr_no_wav = 44100,
                 dtype_no_wav = np.float32,
                 channels_no_wav = 1,
                 output_path = "",
                 debug_prints = False):
        """
        Initializes an AudioThreadWithBuffer object (a thread that takes audio, stores it in a buffer,
        optionally processes it, and returns new audio to play back).
        Parameters:
            name: unique identifier for audio thread
            frames_per_buffer: size of the buffer (a frame is the set of samples across all channels at a given index)
            process_func: the user-defined function to be called as a callback when new audio is received from PyAudio - must accept at least 2 args
            process_func_args: additional arguments for process_func
            wav_file: path to a wav file to pass to process_func
            calc_transforms: if True, calculate chroma features for microphone audio in real time
            calc_beats: if True, detect beats in microphone and wav file audio using BeatNet
            run_counter:
            kill_after_finished: if False, keep pyaudio stream will remain open after entire wav file has been played
            time_stretch: if True, time stretch the wav file audio
            sr_no_wav: sample rate to use if no wav file is provided
            dtype_no_wav: dtype to use if no wav file is provided
            channels_no_wav: number of channels if no wav file is provided
            output_path: file path for audio recording output
            debug_prints: if True, print debug info
        Returns: nothing

        All params directly passed to PyAudio are in ALL CAPS.
        """
        super(AudioBuffer, self).__init__()  # initialize parent class
        np.set_printoptions(suppress=True)
        self.name = name 
        self.FRAMES_PER_BUFFER = frames_per_buffer 
        self.process_func = process_func 
        self.process_func_args = process_func_args
        self.calc_transforms = calc_transforms
        self.calc_beats = calc_beats
        self.run_counter = run_counter
        self.kill_after_finished = kill_after_finished 
        self.time_stretch = time_stretch
        self.RATE = sr_no_wav
        self.dtype = dtype_no_wav
        self.output_path = output_path

        self.paused = False

        # User-editable parameters for the audio system
        self.wav_data = None
        self.wav_index = 0
        self.wav_len = 0
        self.CHANNELS = channels_no_wav
        self.wav_buffer = None
        
        # Get the audio data and sample rate from the wav file
        if wav_file is not None:
            self.wav_data, self.RATE = librosa.load(wav_file) 
            self.dtype = self.wav_data.dtype
            
            # if there is a single channel, reshape it into the correct shape
            if len(self.wav_data.shape) == 1:
                self.wav_data = self.wav_data.reshape(1, -1)

            self.CHANNELS, self.wav_len = self.wav_data.shape
            # if calc_transforms:
            #     self.wav_transform = self.transform_func(self.wav_data)
            #     if debug_prints:
            #         print("Wav transform shape = %s" % (str(self.wav_transform.shape)))

            self.wav_buffer = np.zeros_like(self.wav_data)  # set a zero array

        # set the pyaudio format
        if self.dtype == np.float32:
            self.FORMAT = pyaudio.paFloat32
        elif self.dtype == np.int16:
            self.FORMAT = pyaudio.paInt16
        elif self.dtype == np.int32:
            self.FORMAT = pyaudio.paInt32
        
        # a frame consists of samples across all channels at a certain point in time
        if debug_prints:
            print("Audio init parameters:\nFormat = %s\ndtype = %s\nRate = %d\nChannels = %d\nFrames per buffer = %d" % (self.FORMAT, self.dtype, self.RATE, self.CHANNELS, self.FRAMES_PER_BUFFER))
            if wav_file is not None:
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

        # set audio buffer
        self.buffer_elements = 50  # number of CHUNKs the buffer should store
        self.buffer_size = self.buffer_elements * self.FRAMES_PER_BUFFER  # desired buffer size in samples
        self.audio_buffer = np.zeros((self.CHANNELS, self.FRAMES_PER_BUFFER), dtype=self.dtype)  # set a zero array
        self.buffer_index = 0  # current last sample stored in buffer
        self.buffer_filled = False # True if buffer has been filled all the way, False otherwise

        if debug_prints:
            print("Buffer elements: %d\nBuffer size (in samples): %d\nBuffer size (in seconds): %.2f" % (self.buffer_elements, self.buffer_size, self.buffer_size / float(self.RATE)))

        # if calc_transforms:
        #     # Shape of transform buffer: Buffer elements * transform values * channels
        #     self.transform_buffer = np.zeros((self.buffer_elements, *self.wav_transform.shape[1:]), dtype=self.dtype)
        #     self.transform_buffer_index = 0
        #     self.transform_buffer_filled = False

        #     if debug_prints:
        #         print("Transform buffer shape = %s" % (str(self.transform_buffer.shape)))

        if run_counter:
            self.mic_sample_counter = Counter()

        if calc_beats:
            estimator = BeatNet_for_audio_arr(1, mode='online', inference_model='PF', plot=[], thread=False, sample_rate=self.RATE)
            self.wav_beats = estimator.process(self.wav_data)
            for i in range(len(self.wav_beats)):
                self.wav_beats[i][0] = int(self.wav_beats[i][0] * self.RATE)
            if debug_prints:
                print(self.wav_beats)

        # if self.time_stretch:
        #     self.time_stretch_factor = 0.5
        #     self.time_stretch_length = min(time_stretch_length, self.FRAMES_PER_BUFFER)


    def transform_func(self, audio: np.ndarray) -> np.ndarray:
        if len(audio) < self.FRAMES_PER_BUFFER:
            audio = np.concatenate((audio, np.zeros((self.FRAMES_PER_BUFFER - audio.shape[0], audio.shape[1]), dtype=audio.dtype)), axis=0)
        transform_output = librosa.feature.chroma_cqt(y=audio.T, sr=self.RATE, hop_length=self.FRAMES_PER_BUFFER)
        if len(audio) % self.FRAMES_PER_BUFFER == 0:
            transform_output = transform_output[:, :, :-1]
        transform_output = transform_output.swapaxes(0, 2)
        if transform_output.shape[0] == 1:
            transform_output.reshape(transform_output.shape[1:])
        return transform_output
    
    def time_stretch_func(self, audio: np.ndarray, rate: float) -> np.ndarray:
        fourier_transform = np.fft.fft(audio.flatten())
        inverse_fourier = np.real(np.fft.ifft(fourier_transform))
        inverse_fourier = inverse_fourier.reshape((-1, self.CHANNELS))
        print(np.isclose(audio, inverse_fourier, atol=0.001).all())
        # plt.figure()
        # plt.ylim(-1, 1)
        # plt.plot(audio - inverse_fourier)
        # plt.show()
        return inverse_fourier
        # return pytsmod.hptsm(audio.T, rate).reshape((-1, self.CHANNELS))

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
        print("Stopping")
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
    
    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def change_time_stretch_factor(self, val: float):
        self.time_stretch_factor = val
        
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

        # Counter
        if self.run_counter:
            self.mic_sample_counter.subtract_all(L)  # Update sample counter

        # Transforms
        # if self.calc_transforms:
        #     self.transform_buffer[self.transform_buffer_index] = self.transform_func(input_array)  # Process the input info
        #     if self.transform_buffer_index == self.buffer_elements - 1:  # Once the buffer is filled, mark it as filled
        #         self.transform_buffer_filled = True
        #     self.transform_buffer_index = (self.transform_buffer_index + 1) % self.buffer_elements  # Increment the buffer counter

        # Time stretching
        # enough_wav_data = True
        # if not self.time_stretch:
        #     if self.wav_index + self.FRAMES_PER_BUFFER <= self.wav_len:  # If there is enough data in wav
        #         current_wav_data = self.wav_data[self.wav_index:self.wav_index + self.FRAMES_PER_BUFFER]
        #         self.wav_index += self.FRAMES_PER_BUFFER
        #     else:  # Send the rest of the wav to process_func and kill the PyAudio stream
        #         current_wav_data = self.wav_data[self.wav_index:]
        #         self.wav_index = self.wav_len
        #         enough_wav_data = False
        # else:
        #     num_samples_needed = int(self.FRAMES_PER_BUFFER / self.time_stretch_factor)
        #     if self.wav_index + num_samples_needed <= self.wav_len:  # If there is enough data in wav
        #         if self.wav_index + self.time_stretch_length <= self.wav_len:
        #             wav_data_to_time_stretch = self.wav_data[self.wav_index:self.wav_index + self.time_stretch_length]
        #         else: 
        #             wav_data_to_time_stretch = self.wav_data[self.wav_index:]
        #         self.wav_index += num_samples_needed
        #     else:  # Send the rest of the wav to process_func and kill the PyAudio stream
        #         wav_data_to_time_stretch = self.wav_data[self.wav_index:]
        #         enough_wav_data = False
        #         self.wav_index = self.wav_len
        #     current_wav_data = self.time_stretch_func(wav_data_to_time_stretch, self.time_stretch_factor)
        #     current_wav_data = current_wav_data[:num_samples_needed]
        #     self.wav_buffer[self.wav_index : self.wav_index + len(current_wav_data)] = current_wav_data
        #     print("current_wav_data shape", current_wav_data.shape)

        # This is where process_func in threaded_parent_with_buffer.py is called from
        if not self.paused:
            if self.wav_data is not None:
                if self.wav_index < self.wav_len:  # If there is enough data in wav
                    self.output_array = self.process_func(self, 
                                                          input_array, 
                                                          self.wav_data, 
                                                          *self.process_func_args) # Call process_func
                    # self.wav_index += self.FRAMES_PER_BUFFER
                else:  # Send the rest of the wav to process_func and kill the PyAudio stream
                    self.output_array = self.process_func(self, input_array, 
                                                self.wav_data, 
                                                *self.process_func_args)
                    if self.kill_after_finished:
                        if self.wave_data is not None and self.output_path is not None:
                            soundfile.write(self.output_path, self.wav_buffer.flatten(), self.RATE)
                        self.stop()
                        return self.output_array.flatten(order='F'), pyaudio.paAbort
                    else:
                        self.pause()
                        self.wav_index = 0
            else:
                self.output_array = self.process_func(self, input_array, 
                                                None, 
                                                *self.process_func_args) # Call process_func
        if self.stop_request:
            self.stop()
            return self.output_array.flatten(order='F'), pyaudio.paAbort
        return self.output_array.flatten(order='F'), pyaudio.paContinue
