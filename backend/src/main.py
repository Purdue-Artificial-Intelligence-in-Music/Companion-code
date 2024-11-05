from synchronizer import Synchronizer
import numpy as np
from alignment_error import load_data, calculate_alignment_error
from accompaniment_error import calculate_accompaniment_error
import os
import librosa

output_file = open('output\\output.txt', 'w')

soloist_times = []
estimated_times = []
accompanist_times = []
playback_rates = []

reference = os.path.join('data', 'audio', 'bach', 'synthesized', 'solo.wav')
accompaniment = os.path.join(
    'data', 'audio', 'bach', 'synthesized', 'accompaniment.wav')
source = os.path.join('data', 'audio', 'bach', 'synthesized', 'solo.wav')

source_audio = librosa.load(source, sr=44100)
source_audio = source_audio[0].reshape((1, -1))

# create a synchronizer object
synchronizer = Synchronizer(reference=reference,
                            accompaniment=accompaniment,
                            Kp=0.2,
                            Ki=0.001,
                            Kd=0.005,
                            sample_rate=44100,
                            win_length=8192,
                            hop_length=2048,
                            c=50,
                            max_run_count=3,
                            diag_weight=0.4,
                            channels=1)

input('Press Enter to start the performance')
# start the synchronizer

for i in range(0, source_audio.shape[-1], 8192):
    frames = source_audio[:, i:i+8192]
    accompanist_frames, estimated_time = synchronizer.step(frames)

    soloist_time = synchronizer.soloist_time()
    accompanist_time = synchronizer.accompanist_time()
    playback_rate = synchronizer.phase_vocoder.playback_rate

    soloist_times.append(soloist_time)
    estimated_times.append(estimated_time)
    accompanist_times.append(accompanist_time)
    playback_rates.append(playback_rate)

    print(f'Soloist time: {soloist_time:.2f}, Estimated time: {estimated_time:.2f}, Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}')
    output_file.write(f'Soloist time: {soloist_time:.2f}, Predicted time: {estimated_time:.2f}, '
                      f'Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}\n')


synchronizer.save_performance(path='performance.wav')
output_file.close()

# score_follower = synchronizer.score_follower

# df_alignment = load_data('data\\alignments\\constant_tempo.csv')
# warping_path = np.asarray([estimated_times, soloist_times], dtype=np.float32).T
# print(warping_path)
# df_alignment = calculate_alignment_error(df_alignment, warping_path)

# estimated_times = warping_path[:, 0]
# df_accompaniment = calculate_accompaniment_error(
#     df_alignment,
#     estimated_times=estimated_times,
#     accompanist_times=np.asarray(accompanist_times)
# )

# df_accompaniment.to_csv(
#     'output\\error_analysis_per_measure_constant.csv', index=False)
# print(df_accompaniment)
