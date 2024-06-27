from AudioPlayer import AudioPlayer
from ScoreFollower import ScoreFollower
from simple_pid import PID
from threading import Thread


class Synchronizer(Thread):
    def __init__(self, sample_rate=22050, channels=1, frames_per_buffer=1024):
        super(Synchronizer, self).__init__()

        self.frames_per_buffer = frames_per_buffer
        self.daemon = True

        self.score_follower = ScoreFollower(midi_file='buns.mid', 
                                            sample_rate=sample_rate,
                                            channels=channels,
                                            frames_per_buffer=frames_per_buffer)
        
        self.player = AudioPlayer(filepath='audio_files/buns_viola.wav', 
                                  sample_rate=sample_rate,
                                  channels=channels,
                                  frames_per_buffer=frames_per_buffer)
        
        self.PID = PID(Kp=0.05, Ki=0.0, Kd=0.0, setpoint=0)
        self.PID.output_limits = (0.5, 2)
        self.PID.sample_time = 0.1
        
    def run(self):
        self.score_follower.start()
        self.player.start()

    def stop(self):
        self.score_follower.stop()
        self.player.stop()

    def sync(self):
        musician_pos = self.score_follower.step()
        player_pos = self.player.index // self.frames_per_buffer
        error = player_pos - musician_pos

        # if musician_pos > 20:
        #     self.player.playback_rate = self.PID(error)
        # print(f'Musician position: {musician_pos}, Player position {player_pos}, Plyback rate: {self.player.playback_rate}')

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
            time.sleep(0.1)
    except KeyboardInterrupt:
        synchronizer.stop()


    plt.imshow(synchronizer.score_follower.otw.D)
    plt.show()
    