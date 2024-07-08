from AudioPlayer import AudioPlayer
from ScoreFollower import ScoreFollower
from AudioGenerator import AudioGenerator
from simple_pid import PID
from threading import Thread
import os


class Synchronizer(Thread):
    """ """
    def __init__(self, path, sample_rate=22050, channels=1, frames_per_buffer=1024, window_length=4096, c=10, max_run_count=3, diag_weight=0.4):
        # Initialize parent class
        super(Synchronizer, self).__init__()
        self.daemon = True

        self.window_length = window_length
        self.c = c

        generator = AudioGenerator(path=path)
        if not os.path.exists('soloist.wav'):
            generator.generate_audio(output_path='soloist.wav', midi_program=43, inst_num=0)

        if not os.path.exists('accompanist.wav'):
            generator.generate_audio(output_path='accompanist.wav', midi_program=41, inst_num=1)

        self.score_follower = ScoreFollower(path='soloist.wav',
                                            sample_rate=sample_rate,
                                            channels=channels,
                                            frames_per_buffer=frames_per_buffer,
                                            window_length=window_length,
                                            c=c,
                                            max_run_count=max_run_count,
                                            diag_weight=diag_weight)
        
        self.player = AudioPlayer(path='accompanist.wav', 
                                  sample_rate=sample_rate,
                                  channels=channels,
                                  frames_per_buffer=frames_per_buffer,
                                  playback_rate=1.0)
        
        self.PID = PID(Kp=0.04, Ki=0.001, Kd=0.001, setpoint=0, starting_output=1.0)
        self.PID.output_limits = (0.33, 3)
        self.PID.sample_time = window_length / sample_rate
        
    def run(self):
        """ """
        self.score_follower.start()
        self.player.start()

    def stop(self):
        """ """
        self.score_follower.stop()
        self.player.stop()

    def update(self):
        """ """
        soloist_pos = self.score_follower.step()
        accompanist_pos = self.player.index // self.window_length
        error = accompanist_pos - soloist_pos
        if soloist_pos > self.c:
            self.player.playback_rate = self.PID(error)
        print(f'Soloist position: {soloist_pos}, Accompanist position {accompanist_pos}, Playback rate: {self.player.playback_rate}')

    def is_active(self):
        """ """
        return self.score_follower.is_active() and self.player.is_active()


if __name__ == '__main__':
    import time
    import matplotlib.pyplot as plt
    import numpy as np

    # create a synchronizer object
    synchronizer = Synchronizer(path='midi_files/buns.mid',
                                sample_rate=22050,
                                channels=1,
                                frames_per_buffer=4096,
                                window_length=4096,
                                c=10,
                                max_run_count=3,
                                diag_weight=1)

    # start the synchronizer
    synchronizer.start()

    # wait until the synchronizer is active
    while not synchronizer.is_active():
        time.sleep(0.01)

    try:
        while synchronizer.is_active():
            # update the playback rate of the accompaniment
            synchronizer.update()
    except KeyboardInterrupt:
        synchronizer.stop()

    indices = np.asarray(synchronizer.score_follower.path).T
    synchronizer.score_follower.otw.D[(indices[0], indices[1])] = np.inf
    plt.imshow(synchronizer.score_follower.otw.D)
    plt.show()
    