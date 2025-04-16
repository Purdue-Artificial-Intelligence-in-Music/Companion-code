import numpy as np
from src.alignment_error import load_data, calculate_alignment_error
from src.accompaniment_error import calculate_accompaniment_error
import os
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

SAMPLE_RATE = 44100  # Universal sample rate
CHANNELS = 1  # Universal number of channels
WIN_LENGTH = 4096  # Samples per window for score follower
HOP_LENGTH = 4096  # Samples per hop for score follower. This should be the same as WIN_LENGTH for now. Can add support for different values in the future
C = 50  # Search width for score follower. Higher values are more computationally expensive
MAX_RUN_COUNT = 3  # Slope constraint for score follower. 1 / MAX_RUN_COUNT <= slope <= MAX_RUN_COUNT
DIAG_WEIGHT = 0.75  # Weight for the diagonal in the cost matrix for score follower. Values less than 2 bias toward diagonal steps
MAX_DURATION = 600  # Maximum duration of audio buffer in seconds


STATED_TEMPO = 100  # Tempo at which the user plans to play in BPM
SOURCE_TEMPO = 110  # Tempo at which the user actually plays in BPM
PIECE_NAME = 'rubato'  # Name of piece
PROGAM_NUMBER = 42  # Program number for accompaniment instrument
SOLO_VOLUME_MULTIPLIER = 0.75

MIDI_SCORE = os.path.join('data', 'midi', PIECE_NAME + '.mid')  # Path to MIDI file
OUTPUT_DIR = os.path.join('data', 'audio', PIECE_NAME)  # Directory where synthesized audio will be saved

generator = AudioGenerator(score_path=MIDI_SCORE)  # Create an AudioGenerator instance
generator.generate_audio(output_dir=os.path.join(OUTPUT_DIR, f'{STATED_TEMPO}bpm'), tempo=STATED_TEMPO)  # Generate a WAV file for each instrument in the MIDI file
generator.generate_audio(output_dir=os.path.join(OUTPUT_DIR, f'{SOURCE_TEMPO}bpm'), tempo=SOURCE_TEMPO)  # Generate a WAV file for each instrument in the MIDI file at a different tempo

reference = os.path.join('data', 'audio', PIECE_NAME, f'{STATED_TEMPO}bpm', 'instrument_0.wav')  # Path to reference audio file
source = os.path.join('data', 'audio', PIECE_NAME, f'{SOURCE_TEMPO}bpm', 'instrument_0.wav')  # Path to soloist audio file (can optionally replace mic input)

source_audio, _ = librosa.load(source, sr=SAMPLE_RATE)  # load soloist audio
source_audio = source_audio.reshape((CHANNELS, -1))  # reshape soloist audio to 2D array
source_index = 0  # index to keep track of soloist audio
use_mic = False  # set to True to use microphone input, False to use prerecorded soloist audio

# Create an audio buffer to store the soloist audio
solo_buffer = AudioBuffer(max_duration=MAX_DURATION, sample_rate=SAMPLE_RATE, channels=1)

# Create a ScoreFollower instance to track the soloist
score_follower = ScoreFollower(reference=reference, 
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

    if use_mic:  # If using microphone input
        data = np.frombuffer(in_data, dtype=np.float32)  # convert data to numpy array
        data = data.reshape((1, -1))  # reshape data to 2D array
    else:  # If using prerecorded soloist audio
        data = source_audio[:, source_index:source_index + frame_count]  # get audio data from source audio
        source_index += frame_count  # update source index

    solo_buffer.write(data)  # write soloist audio to buffer so it can be saved to a WAV file later

    estimated_time = score_follower.step(data)  # get estimated time in soloist audio in seconds

    ref_index, live_index = score_follower.path[-1]
    ref_beat = ref_index * WIN_LENGTH / SAMPLE_RATE * STATED_TEMPO / 60
    live_beat = live_index * WIN_LENGTH / SAMPLE_RATE * STATED_TEMPO / 60
    print(f"Alignment path (beats): ({ref_beat:.2f}, {live_beat:.2f})")


    soloist_times.append(source_index / SAMPLE_RATE)  # log soloist time for error analysis
    estimated_times.append(estimated_time)  # log estimated time for error analysis

    position = estimated_time  / 60 * STATED_TEMPO  # convert estimated time (seconds) to position in piece (beats)

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
performance = MidiPerformance(midi_file_path=MIDI_SCORE, tempo=STATED_TEMPO, instrument_index=1, program_number=PROGAM_NUMBER)

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
# Build the DataFrame
df_alignment = pd.DataFrame({
    'measure': list(range(len(soloist_times))),
    'live': soloist_times,
    'ref': estimated_times
})

warping_path = np.asarray(score_follower.path, dtype=np.float32)
df_alignment = calculate_alignment_error(df_alignment, warping_path)

# Convert to beats and round
df_alignment['ref_beats'] = (df_alignment['ref'] * STATED_TEMPO / 60).round(2)
df_alignment['live_beats'] = (df_alignment['live'] * STATED_TEMPO / 60).round(2)
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
df_alignment_final.to_csv(r'C:\Users\ashwi\OneDrive\Documents\Companion-code\backend\alignment_error_results.csv', index=False)

