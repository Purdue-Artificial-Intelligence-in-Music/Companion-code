from Synchronizer import Synchronizer
import time
import matplotlib.pyplot as plt
import numpy as np
from librosa.display import specshow, waveshow
import librosa
from features import audio_to_np_cens

SCORE = 'scores/Air_on_the_G_String.musicxml'
source = 'audio/cello1.wav'

# create a synchronizer object
synchronizer = Synchronizer(score=SCORE,
                            source='audio/cello1.wav',
                            sample_rate=16000,
                            channels=1,
                            frames_per_buffer=1024,
                            window_length=8192,
                            c=10,
                            max_run_count=3,
                            diag_weight=0.5,
                            Kp=0.1,
                            Ki=0.001,
                            Kd=0.01)

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
        alignment_error = predicted_time - soloist_time
        accompaniment_error = accompanist_time - predicted_time
        # print(f'Accompaniment error: {accompaniment_error}')
except KeyboardInterrupt:
    synchronizer.stop()
    synchronizer.join()

synchronizer.save_performance()

plt.rcParams.update({'font.size': 18})
figsize = (18, 6)
dpi = 400
pad_inches = 0.1

indices = np.asarray(synchronizer.score_follower.path).T
cost_matrix = synchronizer.score_follower.otw.D
cost_matrix[(indices[0], indices[1])] = np.inf
cost_matrix = cost_matrix[:, :synchronizer.score_follower.otw.t]

plt.figure()
plt.imshow(cost_matrix)
plt.title('OTW Cost Matrix')
plt.xlabel('Live Sequence')
plt.ylabel('Reference Sequence')
plt.savefig('cost_matrix.png', bbox_inches='tight', pad_inches=pad_inches, dpi=dpi)
plt.close()

plt.figure()
plt.plot(synchronizer.accompaniment_error)
plt.title('Accompaniment error')
plt.xlabel('Predicted Time')
plt.ylabel('Accompaniment error')
plt.show()