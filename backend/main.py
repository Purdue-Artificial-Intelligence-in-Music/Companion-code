from src.synchronizer import Synchronizer
import numpy as np
from src.alignment_error import load_data, calculate_alignment_error
from src.accompaniment_error import calculate_accompaniment_error
import os
import librosa
from src.phase_vocoder import PhaseVocoder, normalize_audio
from src.audio_buffer import AudioBuffer
import soundfile as sf
import matplotlib.pyplot as plt
import pyaudio
import time

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

reference = os.path.join('data', 'audio', 'air_on_the_g_string', '130bpm', 'instrument_0.wav')
source = os.path.join('data', 'audio', 'air_on_the_g_string', '150bpm', 'instrument_0.wav')
accompaniment = os.path.join('data', 'audio', 'air_on_the_g_string', '130bpm', 'instrument_1.wav')

source_audio, _ = librosa.load(source, sr=44100)
source_audio = source_audio.reshape((1, -1))
source_index = 0
use_mic = False

# create a synchronizer object
synchronizer = Synchronizer(reference=reference,
                            Kp=0.09,
                            Ki=0.01,
                            Kd=0.0,
                            sample_rate=SAMPLE_RATE,
                            channels=CHANNELS,
                            win_length=WIN_LENGTH,
                            hop_length=HOP_LENGTH,
                            c=C,
                            max_run_count=MAX_RUN_COUNT,
                            diag_weight=DIAG_WEIGHT)

pv = PhaseVocoder(path=accompaniment,
                  sample_rate=SAMPLE_RATE,
                  channels=1,
                  playback_rate=1,
                  n_fft=WIN_LENGTH,
                  win_length=WIN_LENGTH,
                  hop_length=HOP_LENGTH)

acc_buffer = AudioBuffer(max_duration=MAX_DURATION, sample_rate=SAMPLE_RATE, channels=1)

def callback(in_data, frame_count, time_info, status):
    global source_index

    if use_mic:
        # convert data to numpy array
        data = np.frombuffer(in_data, dtype=np.float32)
        data = data.reshape((1, -1))  # reshape data to 2D array
    else:
        data = source_audio[:, source_index:source_index + frame_count]
        source_index += frame_count

    # 1. get the playback rate and estimated time
    accompanist_time = pv.get_time()
    playback_rate, estimated_time = synchronizer.step(data, accompanist_time)
    # 2. get the accompaniment frames
    pv.set_playback_rate(playback_rate)
    frames = pv.get_next_frames(frame_count)
    if frames is None:
        # end of audio
        return (np.zeros((frame_count,), dtype=np.float32).tobytes(), pyaudio.paComplete)
    acc_buffer.write(frames.reshape((-1, )))
    soloist_time = synchronizer.get_live_time()

    soloist_times.append(soloist_time)
    estimated_times.append(estimated_time)
    accompanist_times.append(accompanist_time)
    playback_rates.append(playback_rate)

    print(f'Soloist time: {soloist_time:.2f}, Estimated time: {estimated_time:.2f}, Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}')

     # frames shape => (channels, frame_count)
    # If channels=1, flatten to shape (frame_count,)
    output_data = frames.flatten().tobytes()
    return (output_data, pyaudio.paContinue)


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

input('Press Enter to start the performance')
stream.start_stream()

try:
    # Wait for stream to finish
    while stream.is_active():
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
# Close the stream
stream.close()

# Release PortAudio system resources
p.terminate()

solo = synchronizer.live_buffer.get_audio()
solo = normalize_audio(solo)
acc = acc_buffer.get_audio()
acc = normalize_audio(acc)
length = min(solo.shape[-1], acc.shape[-1])
solo = solo[..., :length]
acc = acc[..., :length]
output = solo + acc
output = normalize_audio(output)
output = output.reshape((-1, ))
sf.write('performance.wav', output, 44100)

df_alignment = load_data('data\\alignments\\constant_tempo.csv')
warping_path = np.asarray([estimated_times, soloist_times], dtype=np.float32).T
df_alignment = calculate_alignment_error(df_alignment, warping_path)

estimated_times = warping_path[:, 0]
df_accompaniment = calculate_accompaniment_error(
    df_alignment,
    estimated_times=estimated_times,
    accompanist_times=np.asarray(accompanist_times)
)

df_accompaniment.to_csv(
    'output\\error_analysis_per_measure_constant.csv', index=False)
print(df_accompaniment)
