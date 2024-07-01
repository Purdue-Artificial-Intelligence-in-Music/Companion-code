
from BeatNet_local.BeatNet_thread import BeatNet_thread
from WavBeatTracker import *
from buffer import *
from AudioGenerator import *
from AudioPlayer import *
# from VoiceCommandThread import *
from BeatSynchronizer import *
import traceback
import sys
import torch
from process_funcs import *

FRAMES_PER_BUFFER = 1024  # number of frames in PyAudio buffer
WAV_FILE = 'accompanist.wav'  # accompaniment WAV file

def main():

    # create AudioBuffer
    buffer = AudioBuffer(sample_rate=22050,
                         channels=1,
                         frames_per_buffer=1024,
                         num_chunks=100)
    
    # use CUDA if available
    if torch.cuda.is_available():
        device = 'cuda'
    else:
        device = 'cpu'

    beat_detector = BeatNet_thread(model=1, buffer=buffer, plot=[], device=device)
    player = AudioPlayer(path=WAV_FILE)
    wav_beat_tracker = WavBeatTracker(player=player)
    beat_sync = BeatSynchronizer(soloist_beat_thread=beat_detector, accomp_beat_thread=wav_beat_tracker)
    print("All thread objects initialized")

    buffer.start()
    print("Buffer started")

    player.start()
    print("Player started")

    beat_detector.start()
    print("Beat detector started")

    wav_beat_tracker.start()
    print("Wav beat tracker started")

    beat_sync.start()
    print("Beat synchronizer started")

    minutes_long = int(player.audio_len / player.sample_rate / 60)
    seconds_long = int(player.audio_len / player.sample_rate) % 60

    while not player.is_active():
        time.sleep(0.01)

    try:
        start_time = time.time()
        print("", end="")
        while player.is_active():
            elapsed_time = time.time() - start_time
            minutes_elapsed_in_wav = int(player.index / player.sample_rate / 60)
            seconds_elapsed_in_wav = int(player.index / player.sample_rate) % 60
            player.playback_rate = beat_sync.playback_rate
            print("\r(%.2fs) Mic beats: %d, Wav beats: %d, playback speed = %.2f | Wav playback: %d:%02d out of %d:%02d" % 
                  (elapsed_time, beat_detector.get_total_beats(), wav_beat_tracker.get_total_beats(), player.playback_rate, 
                   minutes_elapsed_in_wav, seconds_elapsed_in_wav, minutes_long, seconds_long),
                  end="",
                  flush=True)
            time.sleep(0.1)

    except Exception as e:
        print("Detected interrupt")
        print(traceback.format_exception(None, # <- type(e) by docs, but ignored 
                                         e, e.__traceback__),
                                         file=sys.stderr, flush=True)
        beat_sync.stop()
        beat_sync.join()

    print("Program done")


if __name__ == "__main__":
    main()
