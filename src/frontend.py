
from BeatNet_local.BeatNet_thread import BeatNet_thread
from WavBeatTracker import *
from AudioBuffer import *
from VoiceCommandThread import *
from BeatSynchronizer import *
import traceback
import sys

FRAMES_PER_BUFFER = 1024
# WAV_FILE = "C:\\Users\\TPNml\\OneDrive\\remix 11 x1.wav"
# WAV_FILE = "C:\\Users\\TPNml\Downloads\\bcr 22050.wav"
WAV_FILE = 'test_audio\mountain_king.mp3'

def process_func(self, input_array, wav_data):
    return wav_data

def main():
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
    
    beat_detector = BeatNet_thread(model=1, BUFFER=buffer, plot=[], device='cpu')
    wav_beat_tracker = WavBeatTracker(BUFFER=buffer)
    beat_sync = BeatSynchronizer(player_beat_thread=beat_detector, accomp_beat_thread=wav_beat_tracker)
    # voice_recognizer = VoiceAnalyzerThread(name="voice_recognizer",
    #                                       BUFFER=buffer,
    #                                       voice_length=3)
    buffer.daemon = True
    beat_detector.daemon = True
    wav_beat_tracker.daemon = True
    # voice_recognizer.daemon = True
    print("All thread objects initialized")
    buffer.start()
    print("Buffer started")
    beat_detector.start()
    print("Beat detector started")
    wav_beat_tracker.start()
    print("Wav beat tracker started")
    beat_sync.start()
    print("Beat synchronizer started")
    # voice_recognizer.start()
    # print("Voice recognizer started")
    minutes_long = int(buffer.wav_len / buffer.RATE / 60)
    seconds_long = int(buffer.wav_len / buffer.RATE) % 60
    try:
        start_time = time.time()
        print("", end="")
        while not buffer.stop_request:
            elapsed_time = time.time() - start_time
            minutes_elapsed_in_wav = int(buffer.wav_index / buffer.RATE / 60)
            seconds_elapsed_in_wav = int(buffer.wav_index / buffer.RATE) % 60
            print("\r(%.2fs) Mic beats: %d, Wav beats: %d, playback speed = %.2f | Wav playback: %d:%02d out of %d:%02d" % 
                  (elapsed_time, beat_detector.get_total_beats(), wav_beat_tracker.get_total_beats(), beat_sync.playback_rate, 
                   minutes_elapsed_in_wav, seconds_elapsed_in_wav, minutes_long, seconds_long),
                  end="",
                  flush=True)
            time.sleep(0.5)

    except Exception as e:
        print("Detected interrupt")
        print(traceback.format_exception(None, # <- type(e) by docs, but ignored 
                                    e, e.__traceback__),
        file=sys.stderr, flush=True)
        buffer.stop()
        buffer.join()

    print("Program done")


if __name__ == "__main__":
    main()
