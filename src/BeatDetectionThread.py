
"""""
import threading
import time

import numpy as np

from OnsetDetection import get_times

def get_tempo(x: np.ndarray):
    out = 0.0
    for i in range(len(x) - 1):
        diff = x[i+1] - x[i]
        out += diff
    out /= len(x)
    out = 60.0 / out
    return out

class BeatDetectionThread(threading.Thread):
    def __init__(self, name, AThread):
        super(BeatDetectionThread, self).__init__()
        self.name = name
        self.AThread = AThread
        self.AThread.buffer_elements = 30
        self.stop_request = False
        self.wav_output = 0
        self.mic_output = 0
        self.wav_tempo = 120.0
        self.mic_tempo = 120.0

    def run(self):
        time.sleep(0.5)
        while not self.stop_request:
            wav_samples = self.AThread.wav_data
            mic_samples = self.AThread.get_last_samples(220500) # 5 seconds
            if not (len(mic_samples) < 100000):
                self.wav_output = get_times(wav_samples, sampling_rate=self.AThread.RATE)
                self.wav_tempo = get_tempo(self.wav_output)
                self.mic_output = get_times(mic_samples, sampling_rate=self.AThread.RATE)
                self.mic_tempo = get_tempo(self.mic_output)

            # Outputs a np.ndarray of shape (t,)
            time.sleep(0.2)
"""""


import threading
import time

import numpy as np

from OnsetDetection import get_times

def get_tempo(x: np.ndarray):
    out = 0.0
    for i in range(len(x) - 1):
        diff = x[i+1] - x[i]
        out += diff
    out /= len(x)
    out = 60.0 / out
    return out

def get_error(input_times, wav_times):
    beats = len(input_times)
    tempo = get_tempo(wav_times)
    for i in range(len(input_times) - 1):
        if input_times[i+1] - input_times[i] > (tempo / 60.0 + 5): # Assumption is missing beat
            beats += (input_times[i+1] - input_times[i]) * tempo / 60.0 # Divide by 60 for BPS
        if input_times[i+1] - input_times[i] < 0.5: # Too fast to be an actual beat
            beats -= 1
    return beats - len(wav_times)

class BeatDetectionThread(threading.Thread):
    def __init__(self, name, AThread):
        super(BeatDetectionThread, self).__init__()
        self.name = name
        self.AThread = AThread
        self.AThread.buffer_elements = 30
        self.stop_request = False
        self.wav_output = 0
        self.mic_output = 0
        self.wav_tempo = 120.0
        self.mic_tempo = 120.0
        self.loss = 0

    def run(self):
        time.sleep(0.5)
        while not self.stop_request:
            wav_samples = self.AThread.wav_data
            mic_samples = self.AThread.get_last_samples(220500) # 5 seconds
            if not (len(mic_samples) < 100000):
                self.wav_output = get_times(wav_samples, sampling_rate=self.AThread.RATE)
                self.wav_tempo = get_tempo(self.wav_output)
                self.mic_output = get_times(mic_samples, sampling_rate=self.AThread.RATE)
                self.mic_tempo = get_tempo(self.mic_output)
                self.loss = get_error(self.mic_output, self.wav_output)

            # Outputs a np.ndarray of shape (t,)
            time.sleep(0.2)
