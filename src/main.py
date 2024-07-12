from Synchronizer import Synchronizer
import time
import matplotlib.pyplot as plt
import numpy as np
from librosa.display import specshow


# create a synchronizer object
synchronizer = Synchronizer(score='scores/Air_on_the_G_String.musicxml',
                            source=None,
                            max_run_count=3,
                            diag_weight=0.5)

# start the synchronizer
synchronizer.start()

# wait until the synchronizer is active
while not synchronizer.is_active():
    time.sleep(0.01)

try:
    while synchronizer.is_active():
        # update the playback rate of the accompaniment
        synchronizer.update()
        soloist_time = synchronizer.soloist_time()
        predicted_time = synchronizer.predicted_time()
        accompanist_time = synchronizer.accompanist_time()
        playback_rate = synchronizer.player.playback_rate
        print(f'Soloist time: {soloist_time:.2f}, Predicted time: {predicted_time:.2f}, Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}')
except KeyboardInterrupt:
    synchronizer.stop()


synchronizer.save_performance()

t = synchronizer.score_follower.otw.t
mic_chroma = np.flip(synchronizer.score_follower.otw.live[:, :t], axis=0)
ref_chroma = np.flip(synchronizer.score_follower.otw.ref, axis=0)

fig, ax = plt.subplots(nrows=2, sharex=False, sharey=True, figsize=(4, 8))
specshow(mic_chroma, y_axis='chroma', x_axis='time', ax=ax[0])
specshow(ref_chroma, y_axis='chroma', x_axis='time', ax=ax[1])
plt.show()
