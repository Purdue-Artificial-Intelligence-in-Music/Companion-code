#from AudioBuffer import *
from VoiceCommands import *

FRAMES_PER_BUFFER = 1024

def process_func(self, input_array, wav_data):
    # print("-------")
    # print(input_array.shape)
    # print(input_array.dtype)
    # print(wav_data.shape)
    # print(wav_data.dtype)
    L = min(len(input_array), len(wav_data))
    output = input_array[0:L] + wav_data[0:L]
    # print(wav_data.shape)
    # print(wav_data.dtype)
    return output

def main():
    
    buffer = AudioBuffer(name="buffer", frames_per_buffer=FRAMES_PER_BUFFER,
                                    wav_file="C:\\Users\\TPNml\\Downloads\\sine tone.wav",
                                    process_func=process_func,
                                    process_func_args=(),
                                    debug_prints=True)
    voice = VoiceAnalyzerThread(name="voice", AThread=AudioBuffer)
    try:
        buffer.start()
        print("Buffer started")
        voice.start()
        print("Voice Commands started")
        while not buffer.stop_request:
            time.sleep(0.5)
    except Exception:
        print("Detected interrupt")
        buffer.stop_request = True
        buffer.stop()
        voice.stop_request = True
    print("Program done")


if __name__ == "__main__":
    main()
