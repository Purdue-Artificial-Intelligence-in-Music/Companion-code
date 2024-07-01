import threading
import time

import numpy as np

from unused_code.OnsetDetection import get_times

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