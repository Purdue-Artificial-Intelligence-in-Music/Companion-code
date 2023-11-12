import threading
import time
from OnsetDetection import get_times

class BeatDetectionThread(threading.Thread):
    def __init__(self, name, AThread):
        super(BeatDetectionThread, self).__init__()
        self.name = name
        self.AThread = AThread
        self.AThread.buffer_elements = 30
        self.stop_request = False
        self.wav_output = 0
        self.mic_output = 0

    def run(self):
        time.sleep(0.5)
        while not self.stop_request:
            wav_samples = self.AThread.wav_data
            mic_samples = self.AThread.get_last_samples(220500) # 5 seconds
            if not (len(mic_samples) < 100000):
                self.wav_output = get_times(wav_samples)
                self.mic_output = get_times(mic_samples)
            # Outputs a np.ndarray of shape (t,)
            time.sleep(1.0)