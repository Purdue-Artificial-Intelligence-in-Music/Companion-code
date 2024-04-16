"""
File: TsmThread.py
Description: This file contains the definition of the TimeStretchThread class,
    which is a threaded implementation for time-stretching audio based on microphone and WAV tempos,
    and process_func() function, which performs time-stretching on WAV audio based on microphone
    and WAV tempos.
Key Functions:
- run(): The main method of the TimeStretchThread class that performs the time-stretching operation.
- process_func(wav_tempo, mic_tempo, wav_data): Performs time-stretching on WAV audio
  using the provided tempos and returns the time-stretch ratio.
"""

import numpy as np
import pytsmod as tsm
import soundfile as sf
import threading
import librosa
import time
from tsm_functions import *
from BeatDetectionThread import *
from AudioThreadWithBuffer import *

class TimeStretchThread(threading.Thread):
    def __init__(self, name, AThread: AudioThreadWithBuffer, Beat_Thread: BeatDetectionThread):
        threading.Thread.__init__(self) 
        self.name = name
        self.AThread = AThread
        self.Beat_Thread = Beat_Thread
        self.stop_request = False
        self.output_audio = None

        # PID control variables
        self.current_tempo = 0
        self.timestretch_ratio = 0
        self.integrating_error = 0

    def calculate_expected_tempo(self, error):
        # Calculate expected tempo using PID controller
        # Update integrating error
        return self.current_tempo

    def run(self):
        while not self.stop_request:
            # Attempt to get most recent prediction from BeatThread for beats
            error = self.Beat_Thread.error
            # Calculate expected tempo
            self.current_tempo = self.calculate_expected_tempo(error)
            actual_wav_tempo = self.Beat_Thread.wav_tempo
            self.timestretch_ratio = self.current_tempo / actual_wav_tempo
            # Ask AudioThread for correct number of samples
            current_audio = self.AThread.get_last_samples_wav_file(self.AThread.CHUNK / float(self.timestretch_ratio))
            # Time stretch samples and set output_audio to time-stretched samples
            self.output_audio = librosa.effects.time_stretch(current_audio, rate=self.AThread.RATE)
            assert abs(len(self.output_audio) - len(current_audio) / float(self.AThread.CHUNK)) < 0.05
