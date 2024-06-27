from AudioPlayer import AudioPlayer
from ScoreFollower import ScoreFollower
from simple_pid import PID
from threading import Thread


class Synchronizer(Thread):
    def __init__(self, sample_rate=22050, channels=1, frames_per_buffer=1024, window_length=4096, c=10, max_run_count=3, diag_weight=0.4):
        super(Synchronizer, self).__init__()

        self.frames_per_buffer = frames_per_buffer
        self.window_length = window_length
        self.c = c
        self.daemon = True

        self.score_follower = ScoreFollower(midi_file='buns.mid', 
                                            sample_rate=sample_rate,
                                            channels=channels,
                                            frames_per_buffer=frames_per_buffer,
                                            window_length=window_length,
                                            c=c,
                                            max_run_count=max_run_count,
                                            diag_weight=diag_weight)
        
        self.player = AudioPlayer(filepath='audio_files/buns_viola.wav', 
                                  sample_rate=sample_rate,
                                  channels=channels,
                                  frames_per_buffer=frames_per_buffer,
                                  playback_rate=0.8)
        
        self.PID = PID(Kp=0.04, Ki=0.001, Kd=0.001, setpoint=0, starting_output=0.8)
        self.PID.output_limits = (0.33, 3)
        self.PID.sample_time = window_length / sample_rate
        
    def run(self):
        self.score_follower.start()
        self.player.start()

    def stop(self):
        self.score_follower.stop()
        self.player.stop()

    def sync(self):
        soloist_pos = self.score_follower.step()
        accompanist_pos = self.player.index // self.window_length
        error = accompanist_pos - soloist_pos
        if soloist_pos > self.c:
            self.player.playback_rate = self.PID(error)
        print(f'Musician position: {soloist_pos}, Accompanist position {accompanist_pos}, Playback rate: {self.player.playback_rate}')

    def is_active(self):
        return self.score_follower.is_active() and self.player.is_active()


if __name__ == '__main__':
    import time
    import matplotlib.pyplot as plt

    synchronizer = Synchronizer()
    synchronizer.start()

    while not synchronizer.is_active():
        time.sleep(0.01)

    try:
        while synchronizer.is_active():
            synchronizer.sync()
    except KeyboardInterrupt:
        synchronizer.stop()


    plt.imshow(synchronizer.score_follower.otw.D)
    plt.show()
    