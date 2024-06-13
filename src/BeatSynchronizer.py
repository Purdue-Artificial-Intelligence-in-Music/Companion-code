from simple_pid import PID
from BeatTracker import *
import time

class BeatSynchronizer(threading.Thread):
    """Synchronize the beats from two BeatTracker threads using PID contrl """
    def __init__(self, 
                 player_beat_thread: BeatTracker, 
                 accomp_beat_thread: BeatTracker,
                 Kp = 0.02,
                 Ki = 0.004,
                 Kd = 0.01,
                 sample_time = 0.1,
                 min_tempo = 0.5,
                 max_tempo = 2.5):
        super().__init__()
        self.daemon = True
        self.player_beat_thread = player_beat_thread
        self.accomp_beat_thread = accomp_beat_thread
        self.PID = PID(Kp, Ki, Kd, setpoint=0)
        self.PID.output_limits = (min_tempo, max_tempo)
        self.PID.sample_time = sample_time
        self.playback_rate = 1
        self.enabled = True

    def run(self):
        """Set self.playback_rate using PID control to synchronize the beats """
        _ = self.PID(0)
        while self.enabled:
            player_beats = self.player_beat_thread.get_total_beats()
            accomp_beats = self.accomp_beat_thread.get_total_beats()
            error = accomp_beats - player_beats
            self.playback_rate = self.PID(error)
            time.sleep(self.PID.sample_time)

    def stop(self):
        """Stop the thread """
        self.enabled = False

        
    
    

    