from Synchronizer import Synchronizer
import time
import pandas as pd
import numpy as np
from alignment_error import calculate_alignment_error
from accompaniment_error import calculate_accompaniment_error
import os

output_file = open('output.txt', 'w')

soloist_times = []
predicted_times = []
accompanist_times = []
playback_rates = []

reference = os.path.join('data', 'audio', 'mozart', 'synthesized', 'solo.wav')
accompaniment = os.path.join('data', 'audio', 'mozart', 'synthesized', 'accompaniment.wav')
source = os.path.join('data', 'audio', 'mozart', 'live', 'variable_tempo.wav')

synchronizer = Synchronizer(
    reference=reference,
    accompaniment=accompaniment,
    source=source,
    Kp=0.5,
    Ki=0.001,
    Kd=0.05,
    sample_rate=16000,
    win_length=4096,
    hop_length=1024,
    c=20,
    max_run_count=3,
    diag_weight=0.5,
    channels=1,
    frames_per_buffer=1024
)

synchronizer.start()

while not synchronizer.is_active():
    time.sleep(0.01)

try:
    while synchronizer.update():
        soloist_time = synchronizer.soloist_time()
        predicted_time = synchronizer.estimated_time()
        accompanist_time = synchronizer.accompanist_time()
        playback_rate = synchronizer.player.playback_rate

        soloist_times.append(soloist_time)
        predicted_times.append(predicted_time)
        accompanist_times.append(accompanist_time)
        playback_rates.append(playback_rate)

        print(f'Soloist time: {soloist_time:.2f}, Predicted time: {predicted_time:.2f}, '
              f'Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}')
        output_file.write(f'Soloist time: {soloist_time:.2f}, Predicted time: {predicted_time:.2f}, '
                          f'Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}\n')

except KeyboardInterrupt:
    synchronizer.stop()

synchronizer.save_performance(path='/Users/ranavsethi/aim_practice/Companion-code/data/bach/performance.wav')
output_file.close()

soloist_times_np = np.array(soloist_times)
predicted_times_np = np.array(predicted_times)
accompanist_times_np = np.array(accompanist_times)

measure_numbers = list(range(1, 37))
ref_times = [i * 4 for i in range(36)]

def find_closest_time_indices(ref_times, times):
    indices = []
    for ref_time in ref_times:
        differences = np.abs(times - ref_time)
        index = np.argmin(differences)
        indices.append(index)
    return indices

closest_indices = find_closest_time_indices(ref_times, soloist_times_np)

closest_measures = measure_numbers
closest_live_times = soloist_times_np[closest_indices]
closest_ref_times = np.array(ref_times)
closest_predicted_times = predicted_times_np[closest_indices]
closest_accompanist_times = accompanist_times_np[closest_indices]

df_alignment = pd.DataFrame({
    'measure': closest_measures,
    'live': closest_live_times,
    'ref': closest_ref_times
})

warping_path = np.array(synchronizer.get_warping_path())

df_alignment = calculate_alignment_error(df_alignment, warping_path)
estimated_times = df_alignment['estimated_ref'].values

df_accompaniment = calculate_accompaniment_error(
    df_alignment,
    estimated_times=estimated_times,
    accompanist_times=closest_accompanist_times
)

df_accompaniment.to_csv('error_analysis_per_measure_variable.csv', index=False)
print(df_accompaniment)
df_accompaniment.to_excel('error_analysis_per_measure_variable.xlsx', index=False)
