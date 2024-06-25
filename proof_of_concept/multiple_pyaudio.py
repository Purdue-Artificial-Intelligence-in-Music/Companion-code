import pyaudio
import numpy as np
import time


mic_data = np.zeros((1024, ))
# Define callback for playback (1)
def mic_callback(in_data, frame_count, time_info, status):
    # If len(data) is less than requested frame_count, PyAudio automatically
    # assumes the stream is finished, and the stream stops.
    global mic_data
    mic_data = np.frombuffer(in_data)
    # print(mic_data)
    return (mic_data, pyaudio.paContinue)

def output_callback(in_data, frame_count, time_info, status):
    # If len(data) is less than requested frame_count, PyAudio automatically
    # assumes the stream is finished, and the stream stops.
    global mic_data
    # print(mic_data)
    return (mic_data, pyaudio.paContinue)

p = pyaudio.PyAudio()

mic_stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=44100,
                    input=True,
                    output=False,
                    stream_callback=mic_callback,
                    frames_per_buffer=1024)

output_stream = p.open(format=pyaudio.paFloat32,
                       channels=1,
                       rate=44100,
                       input=False,
                       output=True,
                       stream_callback=output_callback,
                       frames_per_buffer=1024)

while mic_stream.is_active():
    time.sleep(0.1)


mic_stream.close()
p.terminate()