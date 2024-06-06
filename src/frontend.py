
from BeatNet_local.BeatNet_thread import BeatNet_thread
from AudioBuffer import *
from VoiceCommandThread import *

FRAMES_PER_BUFFER = 1024

def process_func(self, input_array, wav_data):
    return wav_data

def main():
    buffer = AudioBuffer(name="buffer", 
                         frames_per_buffer=FRAMES_PER_BUFFER,
                         wav_file="src\mountain_king.mp3",
                         process_func=process_func,
                         process_func_args=(),
                         calc_transforms=False, 
                         calc_beats=False,
                         run_counter=False,
                         kill_after_finished=True,
                         time_stretch=True,
                         playback_rate=2.0,
                         sr_no_wav=44100,
                         dtype_no_wav=np.float32,
                         channels_no_wav=1,
                         output_path="",
                         debug_prints=True)
    # beat_detector = BeatNet_thread(model="PF", BUFFER=buffer, plot=[], thread = False, device='cpu')
    voice_recognizer = VoiceAnalyzerThread(name="voice_recognizer",
                                           BUFFER=buffer,
                                           voice_length=3)
    # beat_detector = True
    voice_recognizer.daemon = True
    print("All thread objects initialized")
    buffer.start()
    print("Buffer started")
    # beat_detector.start()
    # print("Beat detector started")
    voice_recognizer.start()
    print("Voice recognizer started")
    try:
        while not buffer.stop_request:
            time.sleep(0.5)

    except Exception:
        print("Detected interrupt")
        buffer.stop()
        buffer.join()

    print("Program done")


if __name__ == "__main__":
    main()
