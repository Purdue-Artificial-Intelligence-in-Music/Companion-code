import threading

class BeatTracker(threading.Thread):
    def __init__(self):
        super().__init__()

    def get_downbeats(self) -> int:
        return -1
    
    def get_total_beats(self) -> int:
        return -1
    
    def get_current_beats(self):
        return [[]]