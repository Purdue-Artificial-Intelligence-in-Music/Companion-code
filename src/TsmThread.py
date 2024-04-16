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

class TimeStretchThread(threading.Thread):
    def __init__(self, name, AThread, Beat_Thread):
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

    def run(self):
        while not self.stop_request:
            # Attempt to get most recent prediction from BeatThread for beats
            # Calculate expected tempo
            # Ask AudioThread for correct number of samples
            # Time stretch samples
            # Set output_audio to time-stretched samples
            # Store played samples in buffer for BeatThread
