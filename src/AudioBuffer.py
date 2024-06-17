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
import audioflux as af

'''
This class is a template class for a thread that reads in audio from PyAudio and stores it in a buffer.

This is version 2 of the code.
'''

mic_data, _ = librosa.load('audio_files/cello_suite1_cello.wav', sr=22050, mono=False)
if len(mic_data.shape) == 1:
    mic_data = mic_data.reshape(1, -1)
# mic_data = librosa.effects.time_stretch(mic_data, rate=0.75)
mic_index = 0


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
    stop_request : bool, 
    

    Methods
    -------
    to_chroma(audio: np.ndarray)
        Generate chroma features from audio data

    set_process_func_args(a = ())
        Changes the arguments after the sound array when process_func is called.

    run()
        When the thread is started, this function is called which opens the PyAudio object
        and keeps the thread alive.

    stop()
        When the thread is stopped, this function is called which closes the PyAudio object
    
    audio_on(audio: np.ndarray)
        Takes an audio input array and sets an instance variable saying whether the input is playing or not.
        
    get_last_samples(self, n: int)
        Returns the last n samples from the buffer, or the maximum possible elements if there aren't enough recorded yet.

    """
    def __init__(self, name: str, 
                 frames_per_buffer: int = 1024, 
                 process_func: Callable = None, 
                 wav_file: str = None,
                 process_func_args=(), 
                 calc_chroma: bool = False, 
                 calc_beats: bool = False, 
                 kill_after_finished: bool = True,
                 playback_rate: int = 1,
                 sample_rate: int = None,
                 dtype = np.float32,
                 channels: int = 1,
                 debug_prints: bool = False):
        """
        Initializes an AudioThreadWithBuffer object (a thread that takes audio, stores it in a buffer,
        optionally processes it, and returns new audio to play back). All params directly passed to PyAudio are in ALL CAPS.
        
        Parameters
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
        kill_after_finished : bool, optional
            Stop the thread when the WAV audio finishes playing
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

        Returns
        -------
        None

        """
        # PARENT CLASS
        super(AudioBuffer, self).__init__()
        self.daemon = True

        # PRINT OPTIONS
        np.set_printoptions(suppress=True)

        # PARAMS
        self.name = name 
        self.FRAMES_PER_BUFFER = frames_per_buffer 
        self.process_func = process_func
        self.process_func_args = process_func_args
        self.calc_chroma = calc_chroma
        self.calc_beats = calc_beats
        self.kill_after_finished = kill_after_finished 
        self.playback_rate = playback_rate
        self.RATE = sample_rate
        self.dtype = dtype
        self.CHANNELS = channels
        self.debug_prints = debug_prints

        # THREAD ATTRIBUTES
        self.stop_request = False   # True if AudioBuffer needs to be killed, False otherwise
        self.paused = False

        # WAV FILE
        self.wav_data = None
        self.wav_index = 0
        self.wav_len = 0
        self.wav_chroma = None
        self.wav_beats = None

        # If a WAV file was provided
        if wav_file is not None:
            # Load the audio data
            mono = channels == 1
            self.wav_data, self.RATE = librosa.load(wav_file, sr=self.RATE, mono=mono, dtype=dtype)

            # For mono audio, reshape the WAV data into the correct shape
            if mono:
                self.wav_data = self.wav_data.reshape(1, -1)

            # self.wav_data has shape (channels, # samples)
            self.CHANNELS, self.wav_len = self.wav_data.shape

            # Calculate croma 
            if calc_chroma:
                self.wav_chroma = librosa.feature.chroma_cqt(y=self.wav_data, sr=self.RATE, hop_length=self.FRAMES_PER_BUFFER)

            # Calculate beat locations
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

        # MICROPHONE
        # Create audio buffer to store microphone input (not the same as pyaudio buffer).
        self.num_chunks = 1000  # number of CHUNKs the buffer should store
        self.buffer_length = self.num_chunks * self.FRAMES_PER_BUFFER  # desired buffer length in frames
        self.buffer = np.zeros((self.CHANNELS, self.buffer_length), dtype=self.dtype)  # set a zero array
        self.buffer_index = 0  # index of next frame to be filled in buffer
        self.buffer_filled = False # True if buffer has been filled at least once, False otherwise
        self.mic_frame_count = 0  # Number of frames of mic data that have been processed

        self.on_threshold = 0.5  # RMS threshold for audio_on
        self.input_on = False  # True if audio is being played into PyAudio, False otherwise, set by audio_on()
        
        if debug_prints:
            print("Buffer elements: %d\nBuffer size (in samples): %d\nBuffer size (in seconds): %.2f" % (self.num_chunks, self.buffer_length, self.buffer_length / float(self.RATE)))

        # Calculate chroma features for mic audio
        self.chroma_buffer = None
        self.chroma_buffer_index = 0
        self.chroma_filled = False

        if calc_chroma:
            # chroma buffer for mic audio
            # Shape of chroma buffer: (channels, n_chroma, num_chunks)
            self.chroma_buffer = np.zeros((self.CHANNELS, 12, self.num_chunks), dtype=self.dtype)

            if debug_prints:
                print("Chroma buffer shape = %s" % (str(self.chroma_buffer.shape)))


        ################ PyAudio ##################
        self.p = None  # PyAudio object
        self.stream = None  # PyAudio stream
        self.output_array = None  # Audio data that the audio stream will play next

        # Set the pyaudio format
        if self.dtype == np.int16:
            self.FORMAT = pyaudio.paInt16
        elif self.dtype == np.int32:
            self.FORMAT = pyaudio.paInt32
        else:
            self.FORMAT = pyaudio.paFloat32

        print("Audio init parameters: Rate = %d, Channels = %d, Frames per buffer = %d" % (self.RATE, self.CHANNELS, self.FRAMES_PER_BUFFER))
        if debug_prints:
            print("Format = %s, dtype = %s, Frames per buffer = %d" % (self.FORMAT, self.dtype, self.FRAMES_PER_BUFFER))
            if wav_file is not None:
                print("Shape of wav_data: ", self.wav_data.shape)

        ################ PyAudio ##################
        self.p = None  # PyAudio object
        self.stream = None  # PyAudio stream
        self.output_array = None  # Audio data that the audio stream will play next

        # Set the pyaudio format
        if self.dtype == np.int16:
            self.FORMAT = pyaudio.paInt16
        elif self.dtype == np.int32:
            self.FORMAT = pyaudio.paInt32
        else:
            self.FORMAT = pyaudio.paFloat32

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
        cqt_obj = af.CQT(num=84, samplate=self.RATE, slide_length=self.FRAMES_PER_BUFFER + 1)
        cqt_arr = cqt_obj.cqt(audio)
        chroma_cqt_arr = cqt_obj.chroma(cqt_arr)
        chroma_cqt_arr = chroma_cqt_arr.reshape((self.CHANNELS, 12))
        return chroma_cqt_arr

    def set_process_func_args(self, a = ()):
        """Changes the arguments after the sound array when process_func is called.

        Parameters
        ----------
        a : tuple, optional
            Parameters for process_func

        Returns
        -------
        None

        """
        self.process_func_args = a

    def run(self):
        """When the thread is started, this function is called which opens the PyAudio object
        and keeps the thread alive.

        Returns
        -------
        None
            

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
        if val_sum > self.on_threshold:
            self.input_on = True
        else:
            self.input_on = False

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
        num_frames = min(num_frames, self.buffer_length)

        # if n is greater than the buffer index
        if num_frames > self.buffer_index:
            # If the buffer has been filled, wrap around to the end of the array
            if self.buffer_filled:
                # calculate the number of frames needed from the end of the array
                frames_from_end = num_frames - self.buffer_index
                # concatenate the fromaes from the end with the frames from the start to the buffer index
                return np.concatenate((self.buffer[:, -frames_from_end:], self.buffer[:, :self.buffer_index]), axis=1)
            # if the buffer has not been filled at least once, the frames on the end are not valid
            return self.buffer[:, :self.buffer_index]
        
        # if n is less than the buffer index
        return self.buffer[:, self.buffer_index - num_frames:self.buffer_index]

    def get_last_chroma(self, num_features: int):
        """Returns the last n transform frames from the buffer, or the maximum possible elements if there aren't enough recorded yet.

        Parameters
        ----------
        num_features : int
           Number of chroma

        Returns
        -------
        np.ndarray
            Array containing the n most recent chroma features

        """
        # num_features cannot be greater than the size of the buffer
        num_features = min(num_features, self.num_chunks)

        # if num_features is greater than the buffer index
        if num_features > self.chroma_buffer_index:
            # If the buffer has been filled, wrap around to the end of the array
            if self.buffer_filled:
                # calculate the number of features needed from the end of the array
                features_from_end = num_features - self.chroma_buffer_index
                # concatenate the features from the end with the features from the start to the buffer index
                return np.concatenate((self.chroma_buffer[:, :, -features_from_end:], self.chroma_buffer[:, :, :self.chroma_buffer_index]), axis=2)
            # if the buffer has not been filled at least once, the features on the end are not valid
            return self.chroma_buffer[:, :, :self.chroma_buffer_index]
        # if num_features is less than the buffer index
        return self.chroma_buffer[:, :, self.chroma_buffer_index - num_features:self.chroma_buffer_index]
    
    def get_frames(self, start: int, end: int):
        """Returns a slice of the audio buffer from the frame at the start index (inclusive) to the frame at the end index (exclusive).

        Parameters
        ----------
        start : int
            the oldest frame to be returned from the audio buffer
        end : int
            the most recent frames
            

        Returns
        -------
        np.ndarray
            Array containing the slice of the audio buffer from start to end indices

        """

        if start >= self.buffer_length or end > self.buffer_length:
            raise Exception ('Error: Index out of bounds')

        # If the buffer is not filled
        if not self.buffer_filled:
            # Any of these scenarios would result in accessing invalid frames
            if start >= self.buffer_index or end > self.buffer_index or start > end:
                raise Exception('Error: Attempted to read invalid frames from audio buffer')
            
            # start <= end <= self.buff_index and start < self.buffer_index
            return self.buffer[:, start:end]
        
        # At this point, the buffer is filled

        # If start index is greater than end index, wrap around
        if start > end:
            return np.concatenate((self.buffer[:, start:], self.buffer[:, end:]), axis=1)
        
        # If start <= end
        return self.buffer[:, start:end]
    
    def get_chroma(self, start: int, end: int):
        """Returns a slice of the audio buffer from the frame at the start index (inclusive) to the frame at the end index (exclusive).

        Parameters
        ----------
        start : int
            the oldest frame to be returned from the audio buffer
        end : int
            the most recent frame
            

        Returns
        -------
        np.ndarray
            Array containing the slice of the audio buffer from start to end indices

        """
        start = max(0, start)

        if start >= self.num_chunks or end > self.num_chunks:
            raise Exception ('Error: Index out of bounds')

        # If the buffer is not filled
        if not self.chroma_filled:
            # Any of these scenarios would result in accessing invalid frames
            if start >= self.chroma_buffer_index or end > self.chroma_buffer_index or start > end:
                raise Exception('Error: Attempted to read invalid frames from audio buffer')
            
            # start <= end <= self.buff_index and start < self.buffer_index
            return self.chroma_buffer[:, :, start:end]
        
        # At this point, the buffer is filled

        # If start index is greater than end index, wrap around
        if start > end:
            return np.concatenate((self.chroma_buffer[:, :, start:], self.chroma_buffer[:, :, end:]), axis=2)
        
        # If start <= end
        return self.chroma_buffer[:, :, start:end]
    
    def pause(self):
        """Pause but do not kill the thread."""
        self.paused = True

    def unpause(self):
        """Unpause the thread."""
        self.paused = False

    def change_playback_rate(self, val: float):
        """Changes the playback rate of the WAV audio.

        Parameters
        ----------
        val : float
            New playback rate

        Returns
        -------
        None
        """
        self.playback_rate = val

    def fade_in(self, audio, num_frames):
        """Fades in an audio segment.

        Parameters
        ----------
        audio : np.ndarray
            Audio to fade in.
        num_frames : int
            Number of frames to fade in.

        Returns
        -------
        None
        """
        num_frames = min(audio.shape[1], num_frames)
        fade_curve = np.log(np.linspace(1, np.e, num_frames))

        for channel in audio[:, :num_frames]:
            channel *= fade_curve

    def fade_out(self, audio, num_frames):
        """Fades out an audio segment.

        Parameters
        ----------
        audio : np.ndarray
            Audio to fade in.
        num_frames : int
            Number of frames to fade in.

        Returns
        -------
        None
        """
        num_frames = min(audio.shape[1], num_frames)
        start = audio.shape[1] - num_frames
        fade_curve = np.log(np.linspace(np.e, 1, num_frames))

        for channel in audio[:, start:]:
            channel *= fade_curve
        
        
    def callback(self, in_data, frame_count, time_info, flag):
        """This function is called whenever PyAudio recieves new audio. It calls process_func to process the sound data
        and stores the result in the field "data".
        This function should never be called directly.

        Parameters
        ----------
        in_data : np.ndarray
            Microphone audio.
        frame_count : int
            Number of frames in in_data
        time_info :
            
        flag :
            

        Returns
        -------
        (np.ndarray, PortAudio Callback Return Code)
            Audio data to play and return code indicating whether PyAudio stream should continue
            

        """
        input_array = np.frombuffer(in_data, dtype=self.dtype)
        # global mic_data
        # global mic_index
        # input_array = mic_data[:, int(mic_index):int(mic_index+self.FRAMES_PER_BUFFER)]
        # mic_index += self.FRAMES_PER_BUFFER
        # mic_index %= mic_data.shape[1] - self.FRAMES_PER_BUFFER

        # Reshaping code to correct channels
        input_array = np.reshape(input_array, (self.CHANNELS, frame_count))
        L = frame_count

        # Check if audio is on and update instance val
        self.audio_on(input_array)

        # Add audio to buffer
        if self.buffer_index + L > self.buffer_length: # If buffer will overflow
            self.buffer[:, self.buffer_index:] = input_array[:, :self.buffer_length-self.buffer_index] # Add the first portion to the end
            self.buffer[:, 0:L-(self.buffer_length-self.buffer_index)] = input_array[:, self.buffer_length-self.buffer_index:] # Add the rest at the front
        else:
            self.buffer[:, self.buffer_index:self.buffer_index + L] = input_array # Add it all at once
        new_idx = (self.buffer_index + L) % self.buffer_length # Increment the buffer counter
        if new_idx < self.buffer_index:
            self.buffer_filled = True
        self.buffer_index = new_idx

        # Update the frame count
        self.mic_frame_count += frame_count

        # Transforms
        if self.calc_chroma:
            # Calculate chroma feature for microphone audio
            chroma = self.to_chroma(input_array)
            # Store chroma feature in buffer
            self.chroma_buffer[:, :, self.chroma_buffer_index] = chroma
            # Increment the chroma buffer index
            # Mod for circular buffer
            self.chroma_buffer_index = (self.chroma_buffer_index + 1) % self.num_chunks  # Increment the buffer counter

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

        # Fade in and out of each wav_slice to eliminate popping noise
        fade_size = 128
        self.fade_in(wav_slice, num_frames=fade_size)
        self.fade_out(wav_slice, num_frames=fade_size)

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
