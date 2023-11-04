import threading
import time

class BeatDetectionThread(threading.Thread):
    def __init__(self, name, AThread):
        super(BeatDetectionThread, self).__init__()
        self.name = name
        self.AThread = AThread
        self.stop_request = False
        # Initialize whatever stuff you need here

    def run(self):
        # Do beat detection
        time.sleep(0.5)
        while not self.stop_request:
            samples = self.AThread.get_last_samples(1000)
            time.sleep(1.0)

