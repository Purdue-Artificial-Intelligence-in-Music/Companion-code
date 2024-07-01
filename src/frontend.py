
from BeatNet_local.BeatNet_thread import BeatNet_thread
from AudioBuffer import *
from VoiceCommandThread import *
import pytsmod as tsm

FRAMES_PER_BUFFER = 1024

def process_func(self, input_array, wav_data):
    if wav_data is not None:
    # print("-------")
    # print(input_array.shape)
    # print(input_array.dtype)
    # print(wav_data.shape)
    # print(wav_data.dtype)
        # L = min(len(input_array), len(wav_data))
        # output = input_array[:L] + wav_data[:L]
        output = wav_data[self.wav_index, self.wav_index+self.FRAMES_PER_BUFFER]
        self.wav_index += self.FRAMES_PER_BUFFER
    else:
        output = input_array
    # print(wav_data.shape)
    # print(wav_data.dtype)
    return output

def main():

    buffer = AudioBuffer(name="buffer", 
                         frames_per_buffer=FRAMES_PER_BUFFER,
                         wav_file="new_src\hunt.wav",
                         process_func=process_func,
                         process_func_args=(),
                         calc_beats=True,
                         debug_prints=True,
                         time_stretch=True,
                         kill_after_finished=True,
                         output_path="./src/wav_output.wav")
    # beat_detector = BeatNet_thread(model="PF", BUFFER=buffer, plot=[], thread = False, device='cpu')
    voice_recognizer = VoiceAnalyzerThread(name="voice_recognizer",
                                           BUFFER=buffer,
                                           voice_length=3)
    buffer.daemon = True
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
