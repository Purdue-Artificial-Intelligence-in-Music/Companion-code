from Synchronizer import Synchronizer
import time
import matplotlib.pyplot as plt
import numpy as np

# create a synchronizer object
synchronizer = Synchronizer(midi_file='midi_files/buns.mid',
                            sample_rate=22050,
                            channels=1,
                            frames_per_buffer=1024,
                            window_length=4096,
                            c=100,
                            max_run_count=3,
                            diag_weight=2)

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
