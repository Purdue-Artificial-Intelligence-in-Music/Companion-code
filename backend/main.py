import numpy as np
import os
import librosa
import soundfile as sf
import pyaudio
import threading
from time import sleep, time

from src.alignment_error import load_data, calculate_alignment_error
from src.accompaniment_error import calculate_accompaniment_error
from src.audio_buffer import AudioBuffer
from src.score_follower import ScoreFollower
from src.midi_performance import MidiPerformance
from src.audio_generator import AudioGenerator
from src.synchronizer import Synchronizer
from src.phase_vocoder import PhaseVocoder


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Normalize audio data to the range [-1, 1]."""
    return audio / np.max(np.abs(audio))


# ===========================
# UNIVERSAL PARAMETERS
# ===========================
SAMPLE_RATE = 44100
CHANNELS = 1
WIN_LENGTH = 4096
HOP_LENGTH = 4096
C = 100
MAX_RUN_COUNT = 3
DIAG_WEIGHT = 0.5
MAX_DURATION = 600

TEMPO = 180
PIECE_NAME = "twinkle_twinkle"
PROGRAM_NUMBER = 43  # MIDI program number (e.g., 43 = Cello)
SOLO_VOLUME_MULTIPLIER = 1

# ===========================
# FILE PATHS
# ===========================
MIDI_SCORE = os.path.join("data", "midi", PIECE_NAME + ".mid")
OUTPUT_DIR = os.path.join("data", "audio", PIECE_NAME)

# Generate Audio from MIDI
generator = AudioGenerator(score_path=MIDI_SCORE)
generator.generate_audio(output_dir=OUTPUT_DIR, tempo=TEMPO)

# Load Reference & Accompaniment Files
reference = os.path.join(OUTPUT_DIR, "instrument_0.wav")
source = os.path.join(OUTPUT_DIR, "instrument_0.wav")
accompaniment = os.path.join(OUTPUT_DIR, "instrument_1.wav")

# Load Soloist Audio
source_audio, _ = librosa.load(source, sr=SAMPLE_RATE)
source_audio = source_audio.reshape((CHANNELS, -1))
source_index = 0
use_mic = False  # Set to True to use microphone input

# ===========================
# INITIALIZE COMPONENTS
# ===========================
# Audio Buffer for Soloist
solo_buffer = AudioBuffer(max_duration=MAX_DURATION, sample_rate=SAMPLE_RATE, channels=CHANNELS)

# Score Follower for tracking soloist
score_follower = ScoreFollower(reference=reference, 
                               c=C, 
                               max_run_count=MAX_RUN_COUNT, 
                               diag_weight=DIAG_WEIGHT, 
                               sample_rate=SAMPLE_RATE, 
                               win_length=WIN_LENGTH)

# Synchronizer for accompaniment tempo control
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

# Phase Vocoder for real-time accompaniment playback speed adjustment
pv = PhaseVocoder(path=accompaniment,
                  sample_rate=SAMPLE_RATE,
                  channels=CHANNELS,
                  playback_rate=1,
                  n_fft=WIN_LENGTH,
                  win_length=WIN_LENGTH,
                  hop_length=HOP_LENGTH)

# Audio Buffer for accompaniment
acc_buffer = AudioBuffer(max_duration=MAX_DURATION, sample_rate=SAMPLE_RATE, channels=CHANNELS)

# ===========================
# MIDI PERFORMANCE SETUP
# ===========================
midi_performance = MidiPerformance(midi_file_path=MIDI_SCORE, tempo=TEMPO, instrument_index=1, program_number=PROGRAM_NUMBER)


# ===========================
# CALLBACK FUNCTION
# ===========================
def callback(in_data, frame_count, time_info, status):
    global source_index

    if use_mic:
        data = np.frombuffer(in_data, dtype=np.float32).reshape((CHANNELS, -1))
    else:
        data = source_audio[:, source_index:source_index + frame_count]
        source_index += frame_count

    # Get estimated playback rate
    accompanist_time = pv.get_time()
    playback_rate, estimated_time = synchronizer.step(data, accompanist_time)

    # Update tempo dynamically in MIDI Performance
    midi_performance.set_tempo(TEMPO * playback_rate)

    # Update MIDI score position
    midi_performance.update_score_position(estimated_time)

    # Adjust accompaniment speed
    pv.set_playback_rate(playback_rate)
    frames = pv.get_next_frames(frame_count)

    if frames is None:
        return (np.zeros((frame_count,), dtype=np.float32).tobytes(), pyaudio.paComplete)

    acc_buffer.write(frames.reshape((-1,)))

    # Flatten frame output
    return (frames.flatten().tobytes(), pyaudio.paContinue)


# ===========================
# PYTHON AUDIO SETUP
# ===========================
p = pyaudio.PyAudio()

stream = p.open(rate=SAMPLE_RATE,
                channels=CHANNELS,
                format=pyaudio.paFloat32,
                input=True,
                output=True,
                frames_per_buffer=WIN_LENGTH,
                start=False,
                stream_callback=callback)


# ===========================
# MAIN FUNCTION
# ===========================
if __name__ == "__main__":
    input("Press ENTER to start the performance...\n")

    # Start MIDI performance and accompaniment together
    midi_performance.worker_thread.start()
    stream.start_stream()

    try:
        while stream.is_active():
            sleep(0.01)
    except KeyboardInterrupt:
        pass

    # Stop the performance
    stream.close()
    p.terminate()
    midi_performance.stop()

    # Save Soloist Audio
    solo_audio = solo_buffer.get_audio()
    solo_audio = normalize_audio(solo_audio).reshape(-1)
    sf.write("solo.wav", solo_audio, SAMPLE_RATE)

    print("Performance completed. Audio saved.")