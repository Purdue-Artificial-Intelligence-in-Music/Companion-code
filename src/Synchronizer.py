from AudioPlayer import AudioPlayer
from ScoreFollower import ScoreFollower
from AudioGenerator import AudioGenerator
from simple_pid import PID
from threading import Thread
import os


class Synchronizer(Thread):
    """ """
    def __init__(self, path, sample_rate=16000, channels=1, frames_per_buffer=1024, window_length=4096, c=10, max_run_count=3, diag_weight=0.4):
        # Initialize parent class
        super(Synchronizer, self).__init__()
        self.daemon = True

        self.window_length = window_length
        self.c = c

        # Check that musicxml score was provided
        if not path.endswith('.musicxml'):
            raise Exception("Error: Synchronizer path must be for uncompressed MusicXML score (.musicxml)")
        
        # Create an AudioGenerator object
        generator = AudioGenerator(path=path)

        # Get the title of the score
        title = os.path.basename(path)[:-9]

        # Path to soloist audio
        soloist_path = os.path.join('audio_files', title, 'soloist.wav')

        # If the soloist audio does not exist, generate it
        if not os.path.exists(soloist_path):
            generator.generate_audio(output_path=soloist_path, midi_program=43, instrument_id=0)

        # Path to accompanist audio
        accompanist_path = os.path.join('audio_files', title, 'accompanist.wav')

        # If the accompanist audio does not exist, generate it
        if not os.path.exists(accompanist_path):
            generator.generate_audio(output_path=accompanist_path, midi_program=41, instrument_id=1)

        # ScoreFollower needs soloist audio
        self.score_follower = ScoreFollower(path=soloist_path,
                                            sample_rate=sample_rate,
                                            channels=channels,
                                            frames_per_buffer=frames_per_buffer,
                                            window_length=window_length,
                                            c=c,
                                            max_run_count=max_run_count,
                                            diag_weight=diag_weight)
        
        # AudioPlayer needs accompanist audio
        self.player = AudioPlayer(path=accompanist_path, 
                                  sample_rate=sample_rate,
                                  channels=channels,
                                  frames_per_buffer=frames_per_buffer,
                                  playback_rate=1.0)
        
        # PID Controller
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
        accompanist_pos = int(self.player.index // self.window_length)
        error = accompanist_pos - soloist_pos
        if accompanist_pos > self.c:
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
    synchronizer = Synchronizer(path='ode_to_joy.musicxml',
                                sample_rate=16000,
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
    