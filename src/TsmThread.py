# import numpy as np
# import pytsmod as tsm
# import soundfile as sf
# import threading



# """""  Original version
# def split_file(x,sr,time,tempo):
#     '''
#     input:
#     -x, sf data
#     -sr, sample rate
#     -time(seconds)
#     -tempo(bpm)
#     '''
#     x_split = []
#     scale = []
#     temp = []
#     time.append((x.shape[-1])/sr)
#     for i in range(len(time)-1):
#         i1 = int(time[i]*sr)
#         i2 = int((time[i+1]*sr)+1)
#         print(i1,i2)
#         temp = x[:,i1:i2].copy()
#         print(temp)
#         x_split.append(temp)
#         scale.append(120/tempo[i])
#     return(x_split, scale)


# # def time_stretch(input_file, pairs):
#     '''
#     input:
#     - input_file (wav file)
#     - pairs (t, bpm)
#     output:
#     - x (soundfile data)
#     - sr (sample rate)
#     '''
#     x,sr = sf.read(input_file)
#     x = x.T
#     print("length:",len(x[0]),"sr:",sr,"time:",(len(x[0])/sr))
#     print(x)
#     time = pairs[0]
#     bpm = pairs[1]
#     time.insert(0,0)
#     bpm.insert(0,120)
#     x_split,scale = split_file(x,sr,time,bpm)
#     x_output = np.array([[],[]])
#     for i in range(len(x_split)):
#         print("period:",i)
#         print(x_split[i],scale[i])
#         x_output = np.concatenate((x_output,(tsm.hptsm(x_split[i],scale[i]))),axis = 1)
#         print("current length: ",(len(x_output[0])/sr))
#     return (x_output,sr)

# """"" 

# """""   new version 1/28

# def time_stretch(input_file, pairs):

#     x,sr = sf.read(input_file)

#     if x.ndim == 1:
#         num_samples = len(x) 
#     else:
#         num_samples = x.shape[1]

#     print("length:", num_samples, "sr:", sr, "time:", (num_samples/sr))

#     time = pairs[0]
#     bpm = pairs[1]
#     time.insert(0,0)
#     bpm.insert(0,120)
#     x_split,scale = split_file(x,sr,time,bpm)
#     x_output = np.array([[],[]])
#     for i in range(len(x_split)):
#         print("period:",i)
#         print(x_split[i],scale[i])
#         x_output = np.concatenate((x_output,(tsm.hptsm(x_split[i],scale[i]))),axis = 1)
#         print("current length: ",(len(x_output[0])/sr))
#     return (x_output,sr)

# """

# def split_file(x,sr,time,tempo):
#     x_split = []
#     scale = []
#     temp = []
#     time.append((x.shape[-1])/sr)
#     for i in range(len(time)-1):
#         i1 = int(time[i]*sr)
#         i2 = int((time[i+1]*sr)+1)
#         print(i1,i2)
#         temp = x[:,i1:i2].copy()
#         print(temp)
#         x_split.append(temp)
#         scale.append(120/tempo[i])
#     return(x_split, scale)

# def time_stretch(input_file, pairs):
#     x,sr = sf.read(input_file) #gets data and sample rate
#     x = x.T
#     # print("length:",len(x[0]),"sr:",sr,"time:",(len(x[0])/sr))
#     print(x)
#     #gets data from pair
#     time = pairs[0]
#     bpm = pairs[1]
#     #insert starting data
#     time.insert(0,0) 
#     bpm.insert(0,120)

#     x_split,scale = split_file(x,sr,time,bpm) #splits data into multiple chunks
#     x_output = np.array([[],[]])
#     for i in range(len(x_split)):
#         print("period:",i)
#         print(x_split[i],scale[i])
#         x_output = np.concatenate((x_output,(tsm.hptsm(x_split[i],scale[i]))),axis = 1) #added each chunks scaled
#         print("current length: ",(len(x_output[0])/sr))
#     return (x_output,sr)


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
#             sf.write(self.output_filepath, np.ravel(x), sr)


# # class TimeStretchThread(threading.Thread):

# #   def __init__(self, input_file, pairs, output_filepath):
# #       threading.Thread.__init__(self)
# #       self.input_file = input_file  
# #       self.pairs = pairs
# #       self.output_filepath = output_filepath
# #       self.stop_request = False

# #   def run(self):

# #       while not self.stop_request:

# #          x, sr = sf.read(self.input_file)

# #          if x.ndim == 1:
# #             num_samples = len(x)  
# #          else:   
# #             num_samples = x.shape[1]

# #          print("length:", num_samples, "sr:", sr)  

# #          x, sr = time_stretch(self.input_file, self.pairs)

# #          time = self.pairs[0] 
# #          bpm = self.pairs[1]

# #          x_split, scale = split_file(x, sr, time, bpm)

# #          # concatenate stretched segments

# #          sf.write(self.output_filepath, x, sr)



# filepath = 'C:\\Users\\Tima\\Desktop\\Companion-code\\beat_tempo_detection\\songs\\around_the_output.wav'
# output_file = 'C:\\Users\\Tima\\Desktop\\Companion-code\\tsm'
# pairs = [[2], [60]]

# t = TimeStretchThread(filepath, pairs, output_file)

# t.start()


# import numpy as np
# import soundfile as sf
# import threading
# import tsm
# from scipy.interpolate import interp1d

# def hptsm(x, scale):
#     # Compute the length of the output signal
#     output_length = int(len(x) * scale)
    
#     # Generate the time index for the output signal
#     output_time = np.arange(output_length) / scale
    
#     # Generate the time index for the input signal
#     input_time = np.linspace(0, len(x) - 1, len(x))
    
#     # Create an interpolation function
#     interp_func = interp1d(input_time, x)
    
#     # Interpolate the input signal at the time index of the output signal
#     x_output = interp_func(output_time)
    
#     return x_output

# def split_file(x, sr, time, tempo):
#     x_split = []
#     scale = []
#     temp = []
#     time.append((x.shape[-1]) / sr)
#     for i in range(len(time) - 1):
#         i1 = int(time[i] * sr)
#         i2 = int((time[i + 1] * sr) + 1)
#         print(i1, i2)
#         temp = x[i1:i2, :].copy()  # modify the indexing to split along the time axis
#         print(temp)
#         x_split.append(temp)
#         scale.append(120 / tempo[i])
#     return x_split, scale

# def time_stretch(input_file, pairs):
#     x, sr = sf.read(input_file)  # gets data and sample rate
#     # print("length:",len(x[0]),"sr:",sr,"time:",(len(x[0])/sr))
#     x = np.reshape(x, (-1, 1))
#     print(x)
#     # gets data from pair
#     time = pairs[0]
#     bpm = pairs[1]
#     # insert starting data
#     time.insert(0, 0)
#     bpm.insert(0, 120)

#     x_split, scale = split_file(x, sr, time, bpm)  # splits data into multiple chunks
#     x_output = np.array([[], []])
#     for i in range(len(x_split)):
#         print("period:", i)
#         print(x_split[i], scale[i])
#         x_output = np.concatenate((x_output, (hptsm(x_split[i], scale[i]))), axis=1)  # added each chunks scaled
#         print("current length: ", (len(x_output[0]) / sr))
#     return x_output, sr


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
#             sf.write(self.output_filepath, np.ravel(x), sr)


# filepath = 'C:\\Users\\Tima\\Desktop\\Companion-code\\beat_tempo_detection\\songs\\around_the_output.wav'
# output_file = 'C:\\Users\\Tima\\Desktop\\Companion-code\\tsm'
# pairs = [[2], [60]]

# t = TimeStretchThread(filepath, pairs, output_file)

# t.start()


import numpy as np
import soundfile as sf
import threading
from scipy.interpolate import interp1d

# def hptsm(x, scale):
#     output_length = int(len(x) * scale)
#     output_time = np.arange(output_length) / scale
#     input_time = np.linspace(0, len(x) - 1, len(x))
#     interp_func = interp1d(input_time, x[:, 0])  # Modify to only use the first channel
#     x_output = interp_func(output_time)
#     return x_output

def hptsm(x, scale):
    output_length = int(len(x) * scale)
    output_time = np.linspace(0, len(x) - 1, output_length) / scale  # Modify calculation of output_time
    input_time = np.linspace(0, len(x) - 1, len(x))
    interp_func = interp1d(input_time, x[:, 0])
    x_output = interp_func(output_time)
    return x_output

def split_file(x, sr, time, tempo):
    x_split = []
    scale = []
    temp = []
    time.append((x.shape[-1]) / sr)
    for i in range(len(time) - 1):
        print(i) # adding the index
        i1 = int(time[i] * sr)
        i2 = int((time[i + 1] * sr) + 1)
        temp = x[i1:i2, :].copy()  # Modify the indexing to split along the time axis
        x_split.append(temp)
        scale.append(120 / tempo[i])
    return x_split, scale

# def time_stretch(input_file, pairs):
    x, sr = sf.read(input_file)
    x = np.reshape(x, (-1, 1))
    time = pairs[0]
    bpm = pairs[1]
    time.insert(0, 0)
    bpm.insert(0, 120)
    x_split, scale = split_file(x, sr, time, bpm)
    x_output = np.array([])
    for i in range(len(x_split)):
        x_output = np.concatenate((x_output, hptsm(x_split[i], scale[i])), axis=0)
    return x_output, sr

def time_stretch(input_file, pairs):
    x, sr = sf.read(input_file)
    x = np.reshape(x, (-1, 1))
    time = pairs[0]
    bpm = pairs[1]
    time.insert(0, 0)
    bpm.insert(0, 120)
    x_split, scale = split_file(x, sr, time, bpm)
    x_output = np.array([])
    for i in range(len(x_split)):
        if len(x_split[i]) == 0:
            continue
        x_output = np.concatenate((x_output, hptsm(x_split[i], scale[i])), axis=0)
    return x_output, sr


class TimeStretchThread(threading.Thread):
    def __init__(self, input_file, pairs, output_filepath):
        threading.Thread.__init__(self)
        self.input_file = input_file
        self.pairs = pairs
        self.output_filepath = output_filepath
        self.stop_request = False

    def run(self):
        while not self.stop_request:
            x, sr = time_stretch(self.input_file, self.pairs)
            sf.write(self.output_filepath, x, sr)


filepath = 'C:\\Users\\Tima\\Desktop\\Companion-code\\beat_tempo_detection\\songs\\trumpet.mp3'
output_file = 'C:\\Users\\Tima\\Desktop\\Companion-code\\tsm.wav'
pairs = [[2], [60]]  # Modify pairs to match the length of time and bpm

t = TimeStretchThread(filepath, pairs, output_file)
t.start()