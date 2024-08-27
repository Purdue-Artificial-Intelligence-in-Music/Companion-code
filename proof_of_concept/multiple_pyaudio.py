import pyaudio
import numpy as np
import time
import threading


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


class Microphone(threading.Thread):
    def __init__(self):
        super(Microphone, self).__init__()
        self.p = pyaudio.PyAudio()
        self.stream = None
        
    def run(self):
        self.stream = self.p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=44100,
                    input=True,
                    output=False,
                    stream_callback=mic_callback,
                    frames_per_buffer=1024)

class Player(threading.Thread):
    def __init__(self):
        super(Player, self).__init__()
        self.p = pyaudio.PyAudio()
        self.stream = None
        
    def run(self):
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                channels=1,
                                rate=44100,
                                input=False,
                                output=True,
                                stream_callback=output_callback,
                                frames_per_buffer=1024)

# Starting the threads
mic = Microphone()
player = Player()
mic.start()
player.start()

while True:
    time.sleep(0.1)

mic.stream.close()
player.stream.close()
mic.p.terminate()
player.p.terminate()
