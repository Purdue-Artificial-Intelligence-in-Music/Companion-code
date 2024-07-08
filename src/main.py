from Synchronizer import Synchronizer
import time
import matplotlib.pyplot as plt
import numpy as np


def main():

    # create a synchronizer object
    synchronizer = Synchronizer(path='scores/ode_to_joy.musicxml',
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

if __name__ == '__main__':
    main()
