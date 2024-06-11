import pyaudio
import numpy as np
import threading
import time
import librosa
from typing import Callable
from BeatNet_local.BeatNet_files import BeatNet_for_audio_arr
from Counter import *
import os
from BeatSynchronizer import *

'''
This class is a template class for a thread that reads in audio from PyAudio and stores it in a buffer.

This is version 2 of the code.
'''

class AudioBuffer(threading.Thread):
    """
    Thread for storing and processing audio data.

    ...

    Attributes
    ----------
    name : str
        Name of the thread.
    frames_per_buffer : int, optional
        Number of frames in the PyAudio buffer.
    process_func : Callable, optional
        Function to process audio data before it is played.
    calc_chroma : bool, optional
        Calculate chroma features for WAV and microphone audio.
    calc_beats : bool, optional
        Calculate beats for WAV audio
    run_counter : bool, optional
        Create a Counter object to synchronize buffer with beat detection
    kill_after_finished : bool, optional
        Stop the thread when the WAV audio finishes playing
    time_stretch : bool, optional
        Time stretch the WAV audio according to the playback rate
    playback_rate : float, optional
        Multiplier for WAV audio speed
    sample_rate : int, optional
        Sample rate for microphone audio if no WAV file is provided
    dtype : numeric type, optional
        Data type to use when loading 
    channels : int, optional
        Number of channels in WAV audio
    debug_prints : bool, optional
        Print debug information
    

    Methods
    -------
    to_chroma(audio)
        Generate chroma features from audio data

    """
    def __init__(self, name: str, 
                 frames_per_buffer: int = 1024, 
                 process_func: Callable = None, 
                 wav_file: str = None, 
                 process_func_args=(), 
                 calc_chroma = False, 
                 calc_beats = False, 
                 run_counter = False,
                 kill_after_finished = True,
                 time_stretch = False,
                 playback_rate = 1,
                 sample_rate = None,
                 dtype = np.float32,
                 channels = 1,
                 debug_prints = False):
        """
        Initializes an AudioThreadWithBuffer object (a thread that takes audio, stores it in a buffer,
        optionally processes it, and returns new audio to play back).
        Parameters:
            name: unique identifier for audio thread
            frames_per_buffer: frames per buffer for the pyaudio stream
            process_func: the user-defined function to be called as a callback when new audio is received from PyAudio - must accept at least 2 args
            process_func_args: additional arguments for process_func
            wav_file: path to a wav file to pass to process_func
            calc_transforms: if True, calculate chroma features for microphone audio in real time
            calc_beats: if True, detect beats in microphone and wav file audio using BeatNet
            run_counter: if Ture, create a Counter object to help with synchronization
            kill_after_finished: if False, keep pyaudio stream will remain open after entire wav file has been played
            time_stretch: if True, time stretch the wav file audio
            time_stretch_factor: multiplier for audio speed when time stretching
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
        self.daemon = True

        self.name = name 
        self.FRAMES_PER_BUFFER = frames_per_buffer 
        self.process_func = process_func 
        self.process_func_args = process_func_args
        self.calc_chroma = calc_chroma
        self.calc_beats = calc_beats
        self.run_counter = run_counter
        self.kill_after_finished = kill_after_finished 
        self.time_stretch = time_stretch
        self.playback_rate = playback_rate
        self.RATE = sample_rate
        self.dtype = dtype
        self.CHANNELS = channels
        self.debug_prints = debug_prints

        self.paused = False
        self.mic_sample_counter = None
        if run_counter:
            self.mic_sample_counter = Counter()

        # initialize WAV file properites
        self.wav_data = None
        self.wav_index = 0
        self.wav_len = 0
        self.prev_wav_slice = np.zeros((self.CHANNELS, self.FRAMES_PER_BUFFER))

        # Get the audio data and sample rate from the wav file if one is provided
        if wav_file is not None:
            mono = channels == 1
            self.wav_data, self.RATE = librosa.load(wav_file, sr=self.RATE, mono=mono, dtype=dtype)

            # if there is a single channel, reshape the WAV data into the correct shape
            if mono:
                self.wav_data = self.wav_data.reshape(1, -1)

            # self.wav_data has shape (channels, # samples)
            self.CHANNELS, self.wav_len = self.wav_data.shape

        # Helper function vals
        self.on_threshold = 0.5  # RMS threshold for audio_on

        # PyAudio
        self.p = None  # PyAudio object
        self.stream = None  # PyAudio stream

        # Instance vals
        self.output_array = None  # Audio data that the audio stream will play next
        self.input_on = False  # True if audio is being played into PyAudio, False otherwise, set by audio_on()
        self.stop_request = False   # True if AudioThreadWithBuffer needs to be killed, False otherwise

        # create audio buffer to store microphone input (not the same as pyaudio buffer)
        self.buffer_elements = 50  # number of CHUNKs the buffer should store
        self.buffer_size = self.buffer_elements * self.FRAMES_PER_BUFFER  # desired buffer size in samples
        self.audio_buffer = np.zeros((self.CHANNELS, self.buffer_size), dtype=self.dtype)  # set a zero array
        self.buffer_index = 0  # current last sample stored in buffer
        self.buffer_filled = False # True if buffer has been filled all the way, False otherwise
        self.buffer_length = self.audio_buffer.shape[1]

        if debug_prints:
            print("Buffer elements: %d\nBuffer size (in samples): %d\nBuffer size (in seconds): %.2f" % (self.buffer_elements, self.buffer_size, self.buffer_size / float(self.RATE)))

        # Set the pyaudio format
        if self.dtype == np.int16:
            self.FORMAT = pyaudio.paInt16
        elif self.dtype == np.int32:
            self.FORMAT = pyaudio.paInt32
        else:
            self.FORMAT = pyaudio.paFloat32

        # Calculate chroma features for wav file and mic audio
        self.chroma_buffer = None
        if calc_chroma:
            if self.wav_data is not None:  # if wav file was provided, calculate its chroma features
                self.wav_chroma = librosa.feature.chroma_cqt(y=self.wav_data, sr=self.RATE, hop_length=self.FRAMES_PER_BUFFER)

            # chroma buffer for mic audio
            # Shape of chroma buffer: (Buffer elements, channels, n_chroma)
            self.chroma_buffer = np.zeros((self.buffer_elements, self.CHANNELS, 12), dtype=self.dtype)
            self.chroma_buffer_index = 0

            if debug_prints:
                print("Transform buffer shape = %s" % (str(self.chroma_buffer.shape)))
        
        # a frame consists of samples across all channels at a certain point in time
        print("Audio init parameters: Rate = %d, Channels = %d, Frames per buffer = %d" % (self.RATE, self.CHANNELS, self.FRAMES_PER_BUFFER))
        if debug_prints:
            print("Format = %s, dtype = %s, Frames per buffer = %d" % (self.FORMAT, self.dtype))
            if wav_file is not None:
                print("Shape of wav_data: ", self.wav_data.shape)
        self.wav_beats = None

        if calc_beats:
            cwd = os.getcwd()
            if not os.path.exists(os.path.join(cwd, "beat_cache/")):
                os.mkdir(os.path.join(cwd, "beat_cache/"))
            modified_wav_file_name = wav_file.replace("\\", "/")
            beat_path = os.path.join(cwd, "beat_cache/") + str(modified_wav_file_name.split("/")[-1]) + ".npy"
            if debug_prints:
                print("Beat path = \"%s\"" % (beat_path))
            if os.path.exists(beat_path):
                if debug_prints:
                    print("Loading beats from file...")
                self.wav_beats = np.load(beat_path)
            else:
                if debug_prints:
                    print("Calculating beats...")
                estimator = BeatNet_for_audio_arr(1, mode='online', inference_model='PF', plot=[], thread=False, sample_rate=self.RATE)
                self.wav_beats = estimator.process(self.wav_data)
                for i in range(len(self.wav_beats)):
                    self.wav_beats[i][0] = int(self.wav_beats[i][0] * self.RATE)
                self.wav_beats = np.array(self.wav_beats)
                np.save(beat_path, self.wav_beats)

            if debug_prints:
                print(self.wav_beats)

    def to_chroma(self, audio: np.ndarray) -> np.ndarray:
        """

        Parameters
        ----------
        audio: np.ndarray 
            an array containing audio data with shape (channels, number_of_frames)

        Returns
        -------
        np.ndarray
            chroma feature with shape (channels, 12)

        """

        # if there are not enough samples, pad with zeros
        if audio.shape[1] < self.FRAMES_PER_BUFFER:
            audio = np.pad(audio, ((0, 0), (0, self.FRAMES_PER_BUFFER - audio.shape[1])), mode='constant', constant_values=((0, 0), (0, 0)))
        
        # calculate chroma cqt - shape: (channels, n_chroma, time)
        chroma_cqt = librosa.feature.chroma_cqt(y=audio, sr=self.RATE, hop_length=self.CHANNELS * self.FRAMES_PER_BUFFER)

        return chroma_cqt.reshape((self.CHANNELS, 12))

    def set_process_func_args(self, a = ()):
        """Changes the arguments after the sound array when process_func is called.

        Parameters
        ----------
        a :
             (Default value = ())

        Returns
        -------
        type
            

        """
        self.process_func_args = a

    def run(self):
        """When the thread is started, this function is called which opens the PyAudio object
        and keeps the thread alive.

        Parameters
        ----------

        Returns
        -------
        type
            

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

    def stop(self):
        """When the thread is stopped, this function is called which closes the PyAudio object"""
        # self.stream.stop_stream()
        print("Stopping")
        self.stream.close()
        self.p.terminate()
        self.stop_request = True

    def audio_on(self, audio: np.array):
        """Takes an audio input array and sets an instance variable saying whether the input is playing or not.

        Parameters
        ----------
        audio: np.array :
            

        Returns
        -------
        type
            

        """
        audio = audio.astype(np.float64)
        val_sum = 0.0
        for col in audio.T:
            val = np.dot(col, col)
            val_sum += val
        val_sum /= len(audio)
        if val_sum > self.on_threshold:
            self.input_on = True
        else:
            self.input_on = False

    def get_last_samples(self, n: int):
        """Returns the last n samples from the buffer, or the maximum possible elements if there aren't enough recorded yet.

        Parameters
        ----------
        n: int :
            

        Returns
        -------
        type
            

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
        """Returns the last n transform frames from the buffer, or the maximum possible elements if there aren't enough recorded yet.

        Parameters
        ----------
        n: int :
            

        Returns
        -------
        type
            

        """
        if n > self.buffer_elements:
            n = self.buffer_elements
        if not self.buffer_filled and n > self.buffer_index:
            n = self.buffer_index
        if n > self.buffer_index:
            n_from_end = n - self.buffer_index + 1
            return np.concatenate((self.chroma_buffer[:, self.buffer_elements - n_from_end:], self.chroma_buffer[:, 0:self.buffer_index]), axis=1)
        return self.chroma_buffer[:, self.buffer_index - n + 1:self.buffer_index]
    
    def get_range_samples(self, m: int, n: int):
        """Returns the range of samples from the mth most recent sample (inclusive) to the nth most recent sample (exclusive), where n > m, or the maximum possible elements
        if there aren't enough recorded yet.

        Parameters
        ----------
        m :
            the last sample you want the function to return from the buffer
        n :
            the first sample you want the function to return from the buffer
        m: int :
            
        n: int :
            

        Returns
        -------
        type
            

        """
        if n > self.buffer_size:
            n = self.buffer_size
        if not self.buffer_filled and n > self.buffer_index:
            n = self.buffer_index
        if not self.buffer_filled and m > self.buffer_index:
            m = self.buffer_index
        if m >= n:
            return np.empty((self.CHANNELS,0), dtype=self.dtype)
        output = None
        if n > self.buffer_index:
            n_from_end = n - self.buffer_index + 1
            if m > self.buffer_index:
                m_from_end = m - self.buffer_index
                output = self.audio_buffer.T[self.buffer_size - n_from_end + 1:self.buffer_size - m_from_end - 1].T
            else:
                L = self.buffer_size - n_from_end + 1
                R = self.buffer_index - m - 1
                output = np.concatenate((self.audio_buffer.T[L:].T, self.audio_buffer.T[0:R].T), axis=1)
        elif self.buffer_filled and self.buffer_index == 0:
            output = self.audio_buffer.T[self.buffer_index - n + 1:].T 
        else:
            output = self.audio_buffer.T[self.buffer_index - n + 1:self.buffer_index - m].T 
        assert len(output.T) == n - m - 1
        return output
    
    def get_range_transforms(self, m: int, n: int):
        """Returns the range of transforms from the mth most recent transform (inclusive) to the nth most recent transform (exclusive), where n > m, or the maximum possible elements
        if there aren't enough recorded yet.

        Parameters
        ----------
        m :
            the last sample you want the function to return from the buffer
        n :
            the first sample you want the function to return from the buffer
        m: int :
            
        n: int :
            

        Returns
        -------
        type
            

        """
        if n > self.buffer_elements:
            n = self.buffer_elements
        if not self.buffer_filled and n > self.buffer_index:
            n = self.buffer_index
        if not self.buffer_filled and m > self.buffer_index:
            m = self.buffer_index
        if m >= n:
            return np.empty((self.CHANNELS,0), dtype=self.dtype)
        if n > self.buffer_index:
            n_from_end = n - self.buffer_index + 1
            if m > self.buffer_index:
                m_from_end = m - self.buffer_index
                return self.chroma_buffer[:, self.buffer_elements - n_from_end:self.buffer_elements - m_from_end]
            else:
                return np.concatenate((self.chroma_buffer[:, self.buffer_elements - n_from_end:], self.chroma_buffer[:, 0:self.buffer_index - m]), axis=0)
        return self.chroma_buffer[:, self.buffer_index - n + 1:self.buffer_index - m] 
    
    def pause(self):
        """ """
        self.paused = True

    def unpause(self):
        """ """
        self.paused = False

    def change_playback_rate(self, val: float):
        """

        Parameters
        ----------
        val: float :
            

        Returns
        -------

        """
        self.playback_rate = val

    def fade_in(self, audio, num_samples):
        """

        Parameters
        ----------
        audio :
            
        num_samples :
            

        Returns
        -------

        """
        num_samples = min(audio.shape[1], num_samples)
        fade_curve = np.log(np.linspace(1, np.e, num_samples))

        for channel in audio[:, :num_samples]:
            channel *= fade_curve

    def fade_out(self, audio, num_samples):
        """

        Parameters
        ----------
        audio :
            
        num_samples :
            

        Returns
        -------

        """
        num_samples = min(audio.shape[1], num_samples)
        start = audio.shape[1] - num_samples
        fade_curve = np.log(np.linspace(np.e, 1, num_samples))

        for channel in audio[:, start:]:
            channel *= fade_curve
        
        
    def callback(self, in_data, frame_count, time_info, flag):
        """This function is called whenever PyAudio recieves new audio. It calls process_func to process the sound data
        and stores the result in the field "data".
        This function should never be called directly.

        Parameters
        ----------
        in_data :
            
        frame_count :
            
        time_info :
            
        flag :
            

        Returns
        -------
        type
            

        """
        input_array = np.frombuffer(in_data, dtype=self.dtype)

        # Reshaping code to correct channels
        input_array = np.reshape(input_array, (self.CHANNELS, -1))
        L = len(input_array[0])

        # Check if audio is on and update instance val
        self.audio_on(input_array)

        # Add audio to buffer
        if self.buffer_index + L > self.buffer_size: # If buffer will overflow
            self.audio_buffer[:, self.buffer_index:] = input_array[:, :self.buffer_length-self.buffer_index] # Add the first portion to the end
            self.audio_buffer[:, 0:L-(self.buffer_length-self.buffer_index)] = input_array[:, self.buffer_length-self.buffer_index:] # Add the rest at the front
        else:
            self.audio_buffer[:, self.buffer_index:self.buffer_index + L] = input_array # Add it all at once
        new_idx = (self.buffer_index + L) % self.buffer_size # Increment the buffer counter
        if new_idx < self.buffer_index:
            self.buffer_filled = True
        self.buffer_index = new_idx

        # Counter
        if self.run_counter:
            self.mic_sample_counter.add_all(L)  # Update sample counter

        # Transforms
        if self.calc_chroma:
            # Calculate chroma feature for microphone audio
            chroma = self.to_chroma(input_array)

            # Store chroma feature in buffer
            self.chroma_buffer[self.chroma_buffer_index] = chroma
            # Increment the chroma buffer index
            # Mod for circular buffer
            self.chroma_buffer_index = (self.chroma_buffer_index + 1) % self.buffer_elements  # Increment the buffer counter

        # If paused, play nothing
        if self.paused:
            self.output_array = np.zeros((self.CHANNELS, self.FRAMES_PER_BUFFER))
            return self.output_array.flatten(order='F'), pyaudio.paContinue
        
        # If a WAV file was not provided
        if self.wav_data is None:
            # Process only the microphone data
            self.output_array = self.process_func(self, input_array, None, *self.process_func_args)
            return self.output_array.flatten(order='F'), pyaudio.paContinue
        
        # If you reach this point, a WAV file was provided

        # Play the next self.FRAMES_PER_BUFFER samples from the WAV file
        # Get twice the number of frames needed to fill the PyAudio buffer after time stretching
        start = max(0, self.wav_index)
        end = min(self.wav_index + 5 * self.playback_rate * self.FRAMES_PER_BUFFER, self.wav_len)

        # Increment the wav_index based on the playback rate
        self.wav_index += self.playback_rate * self.FRAMES_PER_BUFFER

        # Time stretch the audio based on the playback rate
        stretched_audio = librosa.effects.time_stretch(y=self.wav_data[:, int(start):int(end)], rate=self.playback_rate)  # get audio
        
        # Reshaped the stretched audio (necessary if there is only one channel)
        stretched_audio = stretched_audio.reshape((self.CHANNELS, -1))

        # Get exactly enough frames to fill the PyAudio buffer
        wav_slice = stretched_audio[:, :self.FRAMES_PER_BUFFER]

        # If there are not enough frames, pad with zeros
        if wav_slice.shape[1] < self.FRAMES_PER_BUFFER:
            wav_slice = np.pad(wav_slice, ((0, 0), (0, self.FRAMES_PER_BUFFER - wav_slice.shape[1])), mode='constant', constant_values=((0, 0), (0, 0)))
        
        # Add the last frames from the previous wav_slice to the first frames of the current wav_slice
        overlap_size = 128
        wav_slice[:, :overlap_size] += self.prev_wav_slice[:, self.prev_wav_slice.shape[1]-overlap_size:]
        self.prev_wav_slice = wav_slice

        # Fade in and out of each wav_slice to eliminate popping noise
        fade_size = 128
        self.fade_in(wav_slice, num_samples=fade_size)
        self.fade_out(wav_slice, num_samples=fade_size)

        # If there is enough data in wav, process the microphone audio and WAV audio as normal
        if self.wav_index < self.wav_len:
            self.output_array = self.process_func(self, input_array, wav_slice, *self.process_func_args)
            return self.output_array.flatten(order='F'), pyaudio.paContinue
        
        # Else if the thread is set to stop after the WAV file is finished, stop the thread
        elif self.kill_after_finished:
            self.stop()
            self.output_array = np.zeros((self.CHANNELS, self.FRAMES_PER_BUFFER))
            return self.output_array.flatten(order='F'), pyaudio.paAbort

        # Else, pause, reset the wav index, and play nothing
        else:
            self.pause()
            self.wav_index = 0
            self.output_array = np.zeros((self.CHANNELS, self.FRAMES_PER_BUFFER))
            return self.output_array, pyaudio.paContinue
