import numpy as np
from src.alignment_error import load_data, calculate_alignment_error
from src.accompaniment_error import calculate_accompaniment_error
import os
import yaml
import librosa
from src.audio_buffer import AudioBuffer
from src.score_follower import ScoreFollower
from src.midi_performance import MidiPerformance
from src.audio_generator import AudioGenerator
import soundfile as sf
import pyaudio
import pandas as pd
from time import time, sleep

def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Normalize audio data to the range [-1, 1]."""
    return audio / np.max(np.abs(audio))

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Base parameters
SAMPLE_RATE = config.get("sample_rate", 44100)
CHANNELS = config.get("channels", 1)
WIN_LENGTH = config.get("win_length", 4096)
HOP_LENGTH = config.get("hop_length", WIN_LENGTH)
C = config.get("c", 50)
MAX_RUN_COUNT = config.get("max_run_count", 3)
DIAG_WEIGHT = config.get("diag_weight", 0.75)
MAX_DURATION = config.get("max_duration", 600)
SOLO_VOLUME_MULTIPLIER = config.get("solo_volume_multiplier", 0.75)
PROGAM_NUMBER = config.get("program_number", 42)
REF_TEMPO = config.get("ref_tempo", 100)
LIVE_TEMPO = config.get("live_tempo", 110)
USE_MIC = config.get("use_mic", False)

# PATH LOGIC
PIECE_NAME = config.get("piece_name", "ode_to_joy")
PATH_MIDI_SCORE = config.get("path_midi_score")
PATH_REF_WAV = config.get("path_ref_wav")
PATH_LIVE_WAV = config.get("path_live_wav")

if PIECE_NAME:
    PATH_MIDI_SCORE = os.path.join('data', 'midi', f"{PIECE_NAME}.mid")
    PATH_REF_WAV = os.path.join('data', 'audio', PIECE_NAME, f"ref_{REF_TEMPO}bpm.wav")
    PATH_LIVE_WAV = os.path.join('data', 'audio', PIECE_NAME, f"live_{LIVE_TEMPO}bpm.wav")
elif not (PATH_MIDI_SCORE and PATH_REF_WAV and PATH_LIVE_WAV):
    raise ValueError("Must specify either 'piece_name' or all of 'path_midi_score', 'path_ref_wav', and 'path_live_wav'.")

generator = AudioGenerator(score_path=PATH_MIDI_SCORE)  # Create an AudioGenerator instance
if not os.path.isfile(PATH_REF_WAV):
    generator.generate_solo(output_file=PATH_REF_WAV, tempo=REF_TEMPO, instrument_index=0)
if not os.path.isfile(PATH_LIVE_WAV):
    generator.generate_solo(output_file=PATH_LIVE_WAV, tempo=LIVE_TEMPO, instrument_index=0)

source_audio, _ = librosa.load(PATH_LIVE_WAV, sr=SAMPLE_RATE)  # load soloist audio
source_audio = source_audio.reshape((CHANNELS, -1))  # reshape soloist audio to 2D array
source_index = 0  # index to keep track of soloist audio

# Create an audio buffer to store the soloist audio
solo_buffer = AudioBuffer(max_duration=MAX_DURATION, sample_rate=SAMPLE_RATE, channels=1)

# Create a ScoreFollower instance to track the soloist
score_follower = ScoreFollower(reference=PATH_REF_WAV, 
                               c=C, 
                               max_run_count=MAX_RUN_COUNT, 
                               diag_weight=DIAG_WEIGHT, 
                               sample_rate=SAMPLE_RATE, 
                               win_length=WIN_LENGTH)

soloist_times = []
estimated_times = []
accompanist_times = []
playback_rates = []

# PyAudio callback function
def callback(in_data, frame_count, time_info, status):
    global source_index

    if USE_MIC:  # If using microphone input
        data = np.frombuffer(in_data, dtype=np.float32)  # convert data to numpy array
        data = data.reshape((1, -1))  # reshape data to 2D array
    else:  # If using prerecorded soloist audio
        data = source_audio[:, source_index:source_index + frame_count]  # get audio data from source audio
        source_index += frame_count  # update source index

    solo_buffer.write(data)  # write soloist audio to buffer so it can be saved to a WAV file later

    estimated_time = score_follower.step(data)  # get estimated time in soloist audio in seconds

    ref_index, live_index = score_follower.path[-1]
    ref_beat = ref_index * WIN_LENGTH / SAMPLE_RATE * REF_TEMPO / 60
    live_beat = live_index * WIN_LENGTH / SAMPLE_RATE * REF_TEMPO / 60
    print(f"Alignment path (beats): ({ref_beat:.2f}, {live_beat:.2f})")

    soloist_times.append(source_index / SAMPLE_RATE)  # log soloist time for error analysis
    estimated_times.append(estimated_time)  # log estimated time for error analysis

    position = estimated_time  / 60 * REF_TEMPO  # convert estimated time (seconds) to position in piece (beats)

    # Tell the MidiPerformance instance to update the score position.
    # The MidiPerformance instance will play the most recently passed note in the accompaniment.
    performance.update_score_position(position)
    sleep(0.01)  # update roughly every 10ms
    return (SOLO_VOLUME_MULTIPLIER * data, pyaudio.paContinue)  # Output the solo to the speakers. The accompaniment is already being played by the MidiPerformance instance.

# PyAudio
p = pyaudio.PyAudio()

# Open a stream with the callback function
stream = p.open(rate=SAMPLE_RATE,
                channels=CHANNELS,
                format=pyaudio.paFloat32,
                input=True,
                output=True,
                frames_per_buffer=WIN_LENGTH,
                start=False,
                stream_callback=callback)

# Create a MidiPerformance instance with a MIDI file and an initial tempo (BPM).
performance = MidiPerformance(midi_file_path=PATH_MIDI_SCORE, tempo=REF_TEMPO, instrument_index=1, program_number=PROGAM_NUMBER)

# Wait for user input to start the performance
input('Press Enter to start the performance')

# Start the performance to start playing the accompaniment
performance.start()

# Start the stream to start recording the soloist
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

# Save the soloist audio to a WAV file
solo_audio = solo_buffer.get_audio()
solo_audio = normalize_audio(solo_audio)
solo_audio = solo_audio.reshape(-1)
sf.write('solo.wav', solo_audio, SAMPLE_RATE)

# Build the DataFrame
df_alignment = pd.DataFrame({
    'measure': list(range(len(soloist_times))),
    'live': soloist_times,
    'ref': estimated_times
})

warping_path = np.asarray(score_follower.path, dtype=np.float32)
df_alignment = calculate_alignment_error(df_alignment, warping_path)

# Convert to beats and round
df_alignment['ref_beats'] = (df_alignment['ref'] * REF_TEMPO / 60).round(2)
df_alignment['live_beats'] = (df_alignment['live'] * REF_TEMPO / 60).round(2)
df_alignment['alignment_error'] = df_alignment['alignment_error'].round(2)

# Clean column names for CSV
df_alignment_final = df_alignment.rename(columns={
    'ref_beats': 'Ref Audio (Beats)',
    'live_beats': 'Live Audio (Beats)',
    'alignment_error': 'Alignment Error (Seconds)'
})[['measure', 'Ref Audio (Beats)', 'Live Audio (Beats)', 'Alignment Error (Seconds)']]

# Print results to terminal
print(f"{'Ref Audio (Beats)':>18} | {'Live Audio (Beats)':>18} | {'Alignment Error (Seconds)':>27}")
print("-" * 70)
for _, row in df_alignment_final.iterrows():
    print(f"{row['Ref Audio (Beats)']:18.2f} | {row['Live Audio (Beats)']:18.2f} | {row['Alignment Error (Seconds)']:27.2f}")

# Save to CSV
# df_alignment_final.to_csv(r'C:\Users\ashwi\OneDrive\Documents\Companion-code\backend\alignment_error_results.csv', index=False)

