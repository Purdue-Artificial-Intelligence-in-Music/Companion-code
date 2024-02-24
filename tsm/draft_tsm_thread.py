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
        while not self.stop_request:
            data = self.AThread.get_n_samples(10000)
            if data is not None and len(data) > 5000:
                x, sr = time_stretch(data, self.BeatThread.output)
                self.output = x
            self.stop_request = True

        sf.write(self.output_filepath, np.ravel(self.output), sr)



filepath = 'C:\\Users\\Tima\\Desktop\\Companion-code\\beat_tempo_detection\\songs\\trumpet.mp3'
output_file = 'C:\\Users\\Tima\\Desktop\\Companion-code\\tsm.wav'
pairs = [[2], [240]]  # Modify pairs to match the length of time and bpm
# pairs = [[2, 3], [60, 120]] # times and bpms for 2 periods

t = TimeStretchThread(filepath, pairs, output_file)
t.start()