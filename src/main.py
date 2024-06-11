
from BeatNet_local.BeatNet_thread import BeatNet_thread
from WavBeatTracker import *
from AudioBuffer import *
from VoiceCommandThread import *
from BeatSynchronizer import *
import traceback
import sys
import torch

FRAMES_PER_BUFFER = 1024  # number of frames in PyAudio buffer
WAV_FILE = 'test_audio\imperial_march.wav'  # accompaniment WAV file

# the data returned by this function is played by PyAudio
def process_func(self, input_array, wav_data):
    return wav_data

def main():
    # create AudioBuffer
    buffer = AudioBuffer(name="buffer", 
                         frames_per_buffer=FRAMES_PER_BUFFER,
                         wav_file=WAV_FILE,
                         process_func=process_func,
                         process_func_args=(),
                         calc_chroma=False, 
                         calc_beats=True,
                         run_counter=True,
                         kill_after_finished=True,
                         time_stretch=True,
                         playback_rate=1.0,
                         sr_no_wav=44100,
                         dtype_no_wav=np.float32,
                         channels_no_wav=1,
                         debug_prints=False,
                         output_path="./src/wav_output.wav")
    
    # use CUDA if available
    if torch.cuda.is_available():
        device = 'cuda'
    else:
        device = 'cpu'

    beat_detector = BeatNet_thread(model=1, BUFFER=buffer, plot=[], device=device)
    wav_beat_tracker = WavBeatTracker(BUFFER=buffer)
    beat_sync = BeatSynchronizer(player_beat_thread=beat_detector, accomp_beat_thread=wav_beat_tracker)
    print("All thread objects initialized")

    buffer.start()
    print("Buffer started")

    beat_detector.start()
    print("Beat detector started")

    wav_beat_tracker.start()
    print("Wav beat tracker started")

    beat_sync.start()
    print("Beat synchronizer started")

    minutes_long = int(buffer.wav_len / buffer.RATE / 60)
    seconds_long = int(buffer.wav_len / buffer.RATE) % 60
    try:
        start_time = time.time()
        print("", end="")
        while not buffer.stop_request:
            elapsed_time = time.time() - start_time
            minutes_elapsed_in_wav = int(buffer.wav_index / buffer.RATE / 60)
            seconds_elapsed_in_wav = int(buffer.wav_index / buffer.RATE) % 60
            buffer.playback_rate = beat_sync.playback_rate
            print("\r(%.2fs) Mic beats: %d, Wav beats: %d, playback speed = %.2f | Wav playback: %d:%02d out of %d:%02d" % 
                  (elapsed_time, beat_detector.get_total_beats(), wav_beat_tracker.get_total_beats(), buffer.playback_rate, 
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
        buffer.stop()
        buffer.join()

    print("Program done")


if __name__ == "__main__":
    main()
