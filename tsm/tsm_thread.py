import numpy as np
import pytsmod as tsm
import soundfile as sf
import threading
from scipy.interpolate import interp1d
from pydub import AudioSegment


def split_file(x,sr,time,tempo):
    '''
    input:
    -x, sf data
    -sr, sample rate
    -time(seconds)
    -tempo(bpm)
    '''
    x_split = []
    scale = []
    temp = []
    time.append((x.shape[-1])/sr)
    for i in range(len(time)-1):
        print("The index is: ", i)
        i1 = int(time[i]*sr)
        i2 = int((time[i+1]*sr)+1)
        print(i1,i2)
        temp = x[:,i1:i2].copy()
        print(temp)
        x_split.append(temp)
        scale.append(120/tempo[i])
    return(x_split, scale)

def time_stretch(input_file, pairs):
    '''
    input:
    - input_file (wav file)
    - pairs (t, bpm)
    output:
    - x (soundfile data)
    - sr (sample rate)
    '''
    x,sr = sf.read(input_file) #gets data and sample rate
    x = x.T
    print("length:",len(x[0]),"sr:",sr,"time:",(len(x[0])/sr))
    print(x)
    #gets data from pair
    time = pairs[0]
    bpm = pairs[1]

    if len(time) != len(bpm):
        print("Time and bpm lengths don't match")
        print("The data in Time variable: ", len(time))
        print("The data in Bpm variable: ", len(bpm))

    #insert starting data
    time.insert(0,0) 
    bpm.insert(0,120)

    x_split,scale = split_file(x,sr,time,bpm) #splits data into multiple chunks
    x_output = np.array([[],[]])
    for i in range(len(x_split)):
        print("period:",i)
        print(x_split[i],scale[i])
        x_output = np.concatenate((x_output,(tsm.hptsm(x_split[i],scale[i]))),axis = 1) #added each chunks scaled
        print("current length: ",(len(x_output[0])/sr))
    return (x_output,sr)


# class TimeStretchThread(threading.Thread):
#     def __init__(self, input_file, pairs, output_filepath):
#         threading.Thread.__init__(self)
#         self.input_file = input_file
#         self.pairs = pairs
#         self.output_filepath = output_filepath
#         self.stop_request = False

#     def run(self):
#         while not self.stop_request:
#             x, sr = time_stretch(self.input_file, self.pairs)
#             # pymp3.encode(self.input_file, output_file)
#             # sf.write(self.output_filepath, x, sr)
#             # sf.write(output_file, x, 44100, format='WAV', subtype='PCM_16', endian="LITTLE")
#             # audio = AudioSegment.from_file(self.input_file)  
#             # audio.export(output_file, format="mp3")
#             sf.write(output_file,np.ravel(x),sr) 

class TimeStretchThread(threading.Thread):
    def __init__(self, AudioThread, BeatThread, input_file, pairs, output_filepath):
        threading.Thread.__init__(self)
        self.input_file = input_file
        self.pairs = pairs
        self.output_filepath = output_filepath
        self.stop_request = False
        self.AThread = AudioThread
        self.BeatThread = BeatThread
        self.output = None

    def run(self):
        while not self.stop_request:
            data = self.AThread.get_n_samples(10000)
            if data is not None and len(data) > 5000:
                x, sr = time_stretch(data, self.BeatThread.output)
                self.output = x
            self.stop_request = True

        sf.write(self.output_filepath, np.ravel(self.output), sr)



filepath = 'C:\\Users\\Tima\\Desktop\\Companion-code\\beat_tempo_detection\\songs\\trumpet.mp3'
output_file = 'C:\\Users\\Tima\\Desktop\\Companion-code\\tsm.wav'
pairs = [[2], [240]]  # Modify pairs to match the length of time and bpm
# pairs = [[2, 3], [60, 120]] # times and bpms for 2 periods

t = TimeStretchThread(filepath, pairs, output_file)
t.start()