from simple_pid import PID
from BeatTracker import *
import time

class BeatSynchronizer(threading.Thread):
    """Synchronize the beats from two BeatTracker threads using PID contrl """
    def __init__(self, 
                 soloist_beat_thread: BeatTracker, 
                 accomp_beat_thread: BeatTracker,
                 Kp = 0.15,
                 Ki = 0.001,
                 Kd = 0.5,
                 sample_time = 0.1,
                 min_tempo = 0.5,
                 max_tempo = 2.5):
        super().__init__()
        self.daemon = True
        self.soloist_beat_thread = soloist_beat_thread
        self.accomp_beat_thread = accomp_beat_thread
        self.PID = PID(Kp, Ki, Kd, setpoint=0)
        self.PID.output_limits = (min_tempo, max_tempo)
        self.PID.sample_time = sample_time
        self.playback_rate = 1
        self.enabled = True

    def run(self):
        """Set self.playback_rate using PID control to synchronize the beats """
        _ = self.PID(0)
        start_time = time.time()
        while self.enabled:
            soloist_beats = self.soloist_beat_thread.get_total_beats()
            accomp_beats = self.accomp_beat_thread.get_total_beats()
            elapsed_time = time.time() - start_time
            if elapsed_time > 6:
                error = accomp_beats - soloist_beats
                self.playback_rate = self.PID(error)
            time.sleep(self.PID.sample_time)

    def stop(self):
        """Stop the thread """
        self.enabled = False

        
    
    

    