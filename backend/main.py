from src.synchronizer import Synchronizer
import numpy as np
from src.alignment_error import load_data, calculate_alignment_error
from src.accompaniment_error import calculate_accompaniment_error
import os
import librosa
from src.audio_buffer import AudioBuffer
from src.score_follower import ScoreFollower
from src.midi_performance import MidiPerformance
import soundfile as sf
import pyaudio
from time import time, sleep
import threading


SAMPLE_RATE = 44100
CHANNELS = 1
WIN_LENGTH = 8192
HOP_LENGTH = 2048
C = 50
MAX_RUN_COUNT = 3
DIAG_WEIGHT = 0.4
MAX_DURATION = 600

soloist_times = []
estimated_times = []
accompanist_times = []
playback_rates = []

reference = os.path.join('data', 'audio', 'mozart_k487_no2', 'instrument_0.wav')
source = os.path.join('data', 'audio', 'mozart_k487_no2', 'instrument_0.wav')

source_audio, _ = librosa.load(source, sr=44100)
source_audio = source_audio.reshape((1, -1))
source_index = 0
use_mic = False


# acc_buffer = AudioBuffer(max_duration=MAX_DURATION, sample_rate=SAMPLE_RATE, channels=1)
score_follower = ScoreFollower(reference=reference, 
                               c=C, 
                               max_run_count=MAX_RUN_COUNT, 
                               diag_weight=DIAG_WEIGHT, 
                               sample_rate=SAMPLE_RATE, 
                               win_length=WIN_LENGTH)

def callback(in_data, frame_count, time_info, status):
    global source_index

    if use_mic:
        # convert data to numpy array
        data = np.frombuffer(in_data, dtype=np.float32)
        data = data.reshape((1, -1))  # reshape data to 2D array
    else:
        data = source_audio[:, source_index:source_index + frame_count]
        source_index += frame_count

    estimated_time = score_follower.step(data)
    # print(estimated_time)
    # print(performance.current_tempo)
    position = estimated_time  / 60 * performance.current_tempo  # in beats
    performance.update_score_position(position)
    sleep(0.01)  # update roughly every 10ms

    # 1. get the playback rate and estimated time
    # acc_buffer.write(frames.reshape((-1, )))
    # soloist_time = synchronizer.get_live_time()


    # soloist_times.append(soloist_time)
    # estimated_times.append(estimated_time)
    # accompanist_times.append(accompanist_time)
    # playback_rates.append(playback_rate)

    # print(f'Soloist time: {soloist_time:.2f}, Estimated time: {estimated_time:.2f}, Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}')

     # frames shape => (channels, frame_count)
    # If channels=1, flatten to shape (frame_count,)
    # output_data = frames.flatten().tobytes()
    return (data, pyaudio.paContinue)

# PyAudio
p = pyaudio.PyAudio()
stream = p.open(rate=44100,
                channels=1,
                format=pyaudio.paFloat32,
                input=True,
                output=True,
                frames_per_buffer=8192,
                start=False,
                stream_callback=callback)

# Create a MidiPerformance instance with a MIDI file and an initial tempo (BPM).
performance = MidiPerformance(midi_file_path=r"data/midi/mozart_k487_no2.mid", tempo=60, instrument_index=1)

input('Press Enter to start the performance')
performance.start()
stream.start_stream()

try:
    # Wait for stream to finish
    while stream.is_active():
        sleep(0.01)
except KeyboardInterrupt:
    pass
# Close the stream
stream.close()

# Release PortAudio system resources
p.terminate()


# solo = synchronizer.live_buffer.get_audio()
# solo = normalize_audio(solo)
# acc = acc_buffer.get_audio()
# acc = normalize_audio(acc)
# length = min(solo.shape[-1], acc.shape[-1])
# solo = solo[..., :length]
# acc = acc[..., :length]
# output = solo + acc
# output = normalize_audio(output)
# output = output.reshape((-1, ))
# sf.write('performance.wav', output, 44100)

# df_alignment = load_data('data\\alignments\\constant_tempo.csv')
# warping_path = np.asarray([estimated_times, soloist_times], dtype=np.float32).T
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
