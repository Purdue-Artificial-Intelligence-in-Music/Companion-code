from Synchronizer import Synchronizer
import time
import numpy as np
from alignment_error import load_data, calculate_alignment_error
from accompaniment_error import calculate_accompaniment_error
import os

output_file = open('output\\output.txt', 'w')

soloist_times = []
predicted_times = []
accompanist_times = []
playback_rates = []

reference = os.path.join('data', 'audio', 'bach', 'synthesized', 'solo.wav')
accompaniment = os.path.join('data', 'audio', 'bach', 'synthesized', 'accompaniment.wav')
source = os.path.join('data', 'audio', 'bach', 'live', 'variable_tempo.wav')

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

while not synchronizer.is_active():
    time.sleep(0.01)

try:
    while synchronizer.update():
        soloist_time = synchronizer.soloist_time()
        estimated_time = synchronizer.estimated_time()
        accompanist_time = synchronizer.accompanist_time()
        playback_rate = synchronizer.player.playback_rate

        soloist_times.append(soloist_time)
        predicted_times.append(estimated_time)
        accompanist_times.append(accompanist_time)
        playback_rates.append(playback_rate)

        print(f'Soloist time: {soloist_time:.2f}, Estimated time: {estimated_time:.2f}, Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}, Unread frames: {synchronizer.score_follower.mic.count:4}', end='\r')
        output_file.write(f'Soloist time: {soloist_time:.2f}, Predicted time: {estimated_time:.2f}, '
                          f'Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}\n')

except KeyboardInterrupt:
    synchronizer.stop()

synchronizer.save_performance(path='performance.wav')
output_file.close()

score_follower = synchronizer.score_follower

df_alignment = load_data('data\\alignments\\variable_tempo.csv')
warping_path = np.array(synchronizer.get_warping_path(), dtype=np.float32)
warping_path = warping_path * score_follower.win_length / score_follower.sample_rate
df_alignment = calculate_alignment_error(df_alignment, warping_path)

estimated_times = warping_path[:, 0]
df_accompaniment = calculate_accompaniment_error(
    df_alignment,
    estimated_times=predicted_times,
    accompanist_times=np.asarray(accompanist_times)
)

df_accompaniment.to_csv('output\\error_analysis_per_measure_variable.csv', index=False)
print(df_accompaniment)
