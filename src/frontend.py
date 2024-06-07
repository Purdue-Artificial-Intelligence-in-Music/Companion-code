
from BeatNet_local.BeatNet_thread import BeatNet_thread
from WavBeatTracker import *
from AudioBuffer import *
from VoiceCommandThread import *
import numpy as np
import time
import traceback
import sys

FRAMES_PER_BUFFER = 4096

def process_func(self, input_array, wav_data):
    return wav_data

def main():
    buffer = AudioBuffer(name="buffer", 
                         frames_per_buffer=FRAMES_PER_BUFFER,
                         wav_file="src/mountain_king.mp3",
                         process_func=process_func,
                         process_func_args=(),
                         calc_transforms=False, 
                         calc_beats=True,
                         run_counter=False,
                         kill_after_finished=True,
                         time_stretch=True,
                         playback_rate=2.0,
                         sr_no_wav=44100,
                         dtype_no_wav=np.float32,
                         channels_no_wav=1,
                         debug_prints=True,
                         output_path="./src/wav_output.wav")
    
    beat_detector = BeatNet_thread(model=1, BUFFER=buffer, plot=[], device='cpu')
    wav_beat_tracker = WavBeatTracker(BUFFER=buffer)
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
    # voice_recognizer.start()
    # print("Voice recognizer started")
    try:
        while not buffer.stop_request:
            buffer.playback_rate = 0.5 * np.sin(0.5 * time.time()) + 1
            print("-----")
            print("Mic beats: %d" % (beat_detector.get_total_beats()))
            print("Wav beats: %d" % (wav_beat_tracker.get_total_beats()))
            time.sleep(0.5)

    except Exception:
        print("Detected interrupt")
        print(traceback.format_exception(None, # <- type(e) by docs, but ignored 
                                    e, e.__traceback__),
        file=sys.stderr, flush=True)
        buffer.stop()
        buffer.join()

    print("Program done")


if __name__ == "__main__":
    main()
