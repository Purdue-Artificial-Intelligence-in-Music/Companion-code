from simple_pid import PID
from BeatTracker import *
import time

class BeatSynchronizer(threading.Thread):
    def __init__(self, 
                 player_beat_thread: BeatTracker, 
                 accomp_beat_thread: BeatTracker,
                 Kp = 0.02,
                 Ki = 0.004,
                 Kd = 0.01,
                 sample_time = 0.1,
                 min_tempo = 0.2,
                 max_tempo = 2.5):
        super().__init__()
        self.daemon = True
        self.player_beat_thread = player_beat_thread
        self.accomp_beat_thread = accomp_beat_thread
        self.PID = PID(Kp, Ki, Kd, setpoint=0)
        self.PID.output_limits = (min_tempo, max_tempo)
        self.PID.sample_time = sample_time
        self.playback_rate = 1

    def run(self):
        _ = self.PID(0)
        while True:
            player_beats = self.player_beat_thread.get_total_beats()
            accomp_beats = self.accomp_beat_thread.get_total_beats()
            error = accomp_beats - player_beats
            self.playback_rate = self.PID(error)
            time.sleep(self.PID.sample_time)


        
    
    

    