import threading
import time
from OnsetDetection import spectrogram, peak_extract

class BeatDetectionThread(threading.Thread):
    def __init__(self, name, AThread):
        super(BeatDetectionThread, self).__init__()
        self.name = name
        self.AThread = AThread
        self.stop_request = False
        # Initialize whatever stuff you need here
        self.output = 0

    def run(self):
        # Do beat detection
        time.sleep(0.5)
        while not self.stop_request:
            samples = self.AThread.get_last_samples(1000)
            spectro, df, dt = spectrogram(samples, plot=False)
            peaks = peak_extract(spectro)
            f_loc, t_loc = zip(*peaks)
            self.output = np.unique(dt * (np.array(tuple(t_loc)) + 1)) # np.ndarray of shape (t,)
            time.sleep(1.0)