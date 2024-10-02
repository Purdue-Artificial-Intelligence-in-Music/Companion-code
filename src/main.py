from Synchronizer import Synchronizer
import time
import os
from alignment_error import load_data, calculate_alignment_error
import numpy as np

reference = os.path.join('data', 'audio', 'mozart', 'synthesized', 'solo.wav')
accompaniment = os.path.join('data', 'audio', 'mozart', 'synthesized', 'accompaniment.wav')
source = os.path.join('data', 'audio', 'mozart', 'live', 'variable_tempo.wav')

# create a synchronizer object
synchronizer = Synchronizer(reference=reference,
                            accompaniment=accompaniment,
                            source=source,
                            Kp=0.2,
                            Ki=0.001,
                            Kd=0.005,
                            sample_rate=44100,
                            win_length=8192,
                            hop_length=2048,
                            c=50,
                            max_run_count=3,
                            diag_weight=0.4,
                            channels=1,
                            frames_per_buffer=2048)

input('Press Enter to start the performance')
# start the synchronizer
synchronizer.start()

# wait until the synchronizer is active
while not synchronizer.is_active():
    time.sleep(0.01)

print('Starting performance')
try:
    while synchronizer.update():  # update the playback rate of the accompaniment
        soloist_time = synchronizer.soloist_time()
        estimated_time = synchronizer.estimated_time()
        accompanist_time = synchronizer.accompanist_time()
        playback_rate = synchronizer.player.playback_rate
        print(f'Soloist time: {soloist_time:.2f}, Estimated time: {estimated_time:.2f}, Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}, Unread frames: {synchronizer.score_follower.mic.count:4}', end='\r')
        # print(synchronizer.score_follower.mic.count)
        alignment_error = estimated_time - soloist_time
        accompaniment_error = accompanist_time - estimated_time

except KeyboardInterrupt:
    synchronizer.stop()

synchronizer.save_performance(path='performance.wav')

# Measure the alignment error
score_follower = synchronizer.score_follower

df = load_data('data\\alignments\\variable_tempo.csv')
warping_path = np.asarray(score_follower.path, dtype=np.float32)
warping_path = warping_path * score_follower.win_length / score_follower.sample_rate
df = calculate_alignment_error(df, warping_path)
df.to_csv('output\\variable_tempo_log.csv', index=False)
