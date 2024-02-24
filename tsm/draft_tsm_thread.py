"""
File: draft_tsm_thread.py
Description: This file contains the draft script for time-stretching thread based on beat detection and input pairs of time and BPM.
Key Functions:
- TimeStretchThread: A threaded class that performs time-stretching on audio based on beat detection and input pairs.
- run(): The main method of the TimeStretchThread class that executes the time-stretching operation.
"""


import numpy as np
import pytsmod as tsm
import soundfile as sf
import threading
from scipy.interpolate import interp1d
from pydub import AudioSegment
from tsm_code import time_stretch
from AudioThread import AudioThread
from BeatDetectionThread import BeatDetectionThread


class TimeStretchThread(threading.Thread):
    def __init__(self, AudioThread, BeatDetectionThread, input_file, pairs, output_filepath):
        threading.Thread.__init__(self)
        self.input_file = input_file
        self.pairs = pairs
        self.output_filepath = output_filepath
        self.stop_request = False
        self.AThread = AudioThread
        self.BeatThread = BeatDetectionThread
        self.output = None

    def run(self):
        # Main thread execution loop
        while not self.stop_request:
            # Get audio samples from the AudioThread
            data = self.AThread.get_n_samples(10000)
            if data is not None and len(data) > 5000:
                # Perform time-stretching on the audio data using beat detection output from BeatDetectionThread
                x, sr = time_stretch(data, self.BeatThread.output)
                self.output = x
            self.stop_request = True

        # Write the output audio to the specified file path
        sf.write(self.output_filepath, np.ravel(self.output), sr)

# File paths and parameters
filepath = 'C:\\Users\\Tima\\Desktop\\Companion-code\\beat_tempo_detection\\songs\\trumpet.mp3'
output_file = 'C:\\Users\\Tima\\Desktop\\Companion-code\\tsm.wav'
pairs = [[2], [240]]  # Modify pairs to match the length of time and bpm
# pairs = [[2, 3], [60, 120]] # times and bpms for 2 periods

# Create and start the TimeStretchThread
t = TimeStretchThread(filepath, pairs, output_file)
t.start()