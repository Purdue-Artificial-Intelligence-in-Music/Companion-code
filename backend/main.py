from src.synchronizer import Synchronizer
import numpy as np
from src.alignment_error import load_data, calculate_alignment_error
from src.accompaniment_error import calculate_accompaniment_error
import os
import librosa

if not os.path.exists('output'):
    os.makedirs('output')
output_file = open('output/output.txt', 'w')

soloist_times = []
estimated_times = []
accompanist_times = []
playback_rates = []

reference = os.path.join('backend', 'data', 'audio', 'air_on_the_g_string', 'synthesized', 'solo.wav')
source = os.path.join('backend', 'data', 'audio', 'air_on_the_g_string', 'live', 'constant_tempo.wav')

source_audio, _ = librosa.load(source, sr=44100)
source_audio = source_audio.reshape((1, -1))

# Create a Synchronizer object
synchronizer = Synchronizer(
    reference=reference,
    sample_rate=44100,
    channels=1,
    win_length=8192,
    hop_length=2048,
    c=50,
    max_run_count=3,
    diag_weight=0.4
)

accompanist_time = 0

# Start the synchronizer
for i in range(0, source_audio.shape[-1], 8192):
    frames = source_audio[:, i:i + 8192]
    playback_rate, estimated_time = synchronizer.step(frames, accompanist_time)
    accompanist_time += playback_rate * 8192 / 44100
    soloist_time = synchronizer.get_live_time()

    soloist_times.append(soloist_time)
    estimated_times.append(estimated_time)
    accompanist_times.append(accompanist_time)

    print(f'Soloist time: {soloist_time:.2f}, Estimated time: {estimated_time:.2f}, '
          f'Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}')
    output_file.write(f'Soloist time: {soloist_time:.2f}, Estimated time: {estimated_time:.2f}, '
                      f'Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}\n')

synchronizer.save_performance(path='output/performance.wav')
output_file.close()

df_alignment = load_data('backend/data/alignments/constant_tempo.csv')
warping_path = np.asarray([estimated_times, soloist_times], dtype=np.float32).T
df_alignment = calculate_alignment_error(df_alignment, warping_path)

estimated_times = warping_path[:, 0]
df_accompaniment = calculate_accompaniment_error(
    df_alignment,
    estimated_times=estimated_times,
    accompanist_times=np.asarray(accompanist_times)
)

df_accompaniment.to_csv(
    'output/error_analysis_per_measure_constant.csv', index=False)
print(df_accompaniment)