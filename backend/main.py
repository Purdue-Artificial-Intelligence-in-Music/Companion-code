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
from time import time, sleep

def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Normalize audio data to the range [-1, 1]."""
    return audio / np.max(np.abs(audio))

SAMPLE_RATE = 44100  # Universal sample rate
CHANNELS = 1  # Universal number of channels
WIN_LENGTH = 8192  # Samples per window for score follower
HOP_LENGTH = 8192  # Samples per hop for score follower
C = 50  # Search width for score follower. Higher values are more computationally expensive
MAX_RUN_COUNT = 3  # Slope constraint for score follower. 1 / MAX_RUN_COUNT <= slope <= MAX_RUN_COUNT
DIAG_WEIGHT = 1  # Weight for the diagonal in the cost matrix for score follower. Values less than 2 bias toward diagonal steps
MAX_DURATION = 600  # Maximum duration of audio buffer in seconds

soloist_times = []
estimated_times = []
accompanist_times = []
playback_rates = []

TEMPO = 240  # Tempo at which piece is played in BPM
piece_name = 'greensleeves'  # Name of piece

MIDI_SCORE = os.path.join('data', 'midi', piece_name + '.mid')  # Path to MIDI file
OUTPUT_DIR = os.path.join('data', 'audio', piece_name)  # Directory where synthesized audio will be saved

generator = AudioGenerator(score_path=MIDI_SCORE)  # Create an AudioGenerator instance
generator.generate_audio(output_dir=OUTPUT_DIR, tempo=TEMPO)  # Generate a WAV file for each instrument in the MIDI file

reference = os.path.join('data', 'audio', piece_name, 'instrument_0.wav')  # Path to reference audio file
source = os.path.join('data', 'audio', piece_name, 'instrument_0.wav')  # Path to soloist audio file (can optionally replace mic input)

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
    soloist_times.append(source_index / SAMPLE_RATE)  # log soloist time for error analysis
    estimated_times.append(estimated_time)  # log estimated time for error analysis

    position = estimated_time  / 60 * performance.current_tempo  # convert estimated time (seconds) to position in piece (beats)

    # Tell the MidiPerformance instance to update the score position.
    # The MidiPerformance instance will play the most recently passed note in the accompaniment.
    performance.update_score_position(position)
    sleep(0.01)  # update roughly every 10ms
    return (data, pyaudio.paContinue)  # Output the solo to the speakers. The accompaniment is already being played by the MidiPerformance instance.

# PyAudio
p = pyaudio.PyAudio()

# Open a stream with the callback function
stream = p.open(rate=SAMPLE_RATE,
                channels=CHANNELS,
                format=pyaudio.paFloat32,
                input=True,
                output=True,
                frames_per_buffer=8192,
                start=False,
                stream_callback=callback)

# Create a MidiPerformance instance with a MIDI file and an initial tempo (BPM).
performance = MidiPerformance(midi_file_path=MIDI_SCORE, tempo=TEMPO, instrument_index=1, program_number=43)

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
