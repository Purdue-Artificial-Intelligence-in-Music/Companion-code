from AudioThreadWithBuffer import AudioThreadWithBuffer
from BeatDetectionThread import BeatDetectionThread
import time
import numpy as np
import pytsmod as tsm
import soundfile as sf

def process_func(self, data, wav_data,
                 smoothing=2):
    """
    Processes incoming microphone and wav file samples when new audio is received

    This function is user-editable, but currently adjusts the amplitude of the wav file audio to match
    the amplitude of the microphone volume.

    Parameters:
        self: self parameter for when this function is called from inside AudioThreadWithBuffer
        data: microphone data (numpy array)
        wav_data: wav file data (numpy array)
        smoothing: parameter for how smooth the adjustment above is
    Returns: Audio for AudioThreadWithBuffer to play through speakers with content listed above (numpy array)
    """
    print(wav_data[0:10])
    print(data[0:10])

    data = data.astype(np.int32, casting='safe')
    wav_data = wav_data.astype(np.int32, casting='safe')

    # use RMS to match the input amplitude and output amplitude
    if data is not None:
        input_amplitude = np.sqrt(np.mean(data ** 2))
        output_amplitude = np.sqrt(np.mean(wav_data ** 2))
        scaling_factor = min(max(np.power(input_amplitude / (output_amplitude + 1e-6), 1.5), 0.001), 1)

        if self.last_gain == 0.0:
            self.last_gain = scaling_factor
            self.last_time_updated = time.time()
        else:
            time_since_update = time.time() - self.last_time_updated
            time_since_update /= 1000.0
            average_factor = max(0, min(time_since_update, 1 / smoothing)) * smoothing
            out_gain = average_factor * scaling_factor + (1 - average_factor) * self.last_gain
            self.last_gain = out_gain
        print(self.last_gain)
        wav_data = np.rint(wav_data * self.last_gain).astype(np.int16)
    return wav_data


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
        i1 = int(time[i]*sr)
        i2 = int((time[i+1]*sr)+1)
        print(i1,i2)
        temp = x[:,i1:i2].copy()
        print(temp)
        x_split.append(temp)
        scale.append(120/tempo[i])
    return(x_split, scale)

def time_stretch(data, rate, pairs):
    '''
    input:
    - data (wav file)
    -rate (sampling rate)
    - pairs (t, bpm)
    output:
    - x (soundfile data)
    - rate (sample rate)
    '''
    x = data
    print("length:",len(x[0]),"sr:",rate,"time:",(len(x[0])/sr))
    print(x)
    time = pairs[0]
    bpm = pairs[1]
    time.insert(0,0)
    bpm.insert(0,120)
    x_split,scale = split_file(x,rate,time,bpm)
    x_output = np.array([[],[]])
    for i in range(len(x_split)):
        print("period:",i)
        print(x_split[i],scale[i])
        x_output = np.concatenate((x_output,(tsm.hptsm(x_split[i],scale[i]))),axis = 1)
        print("current length: ",(len(x_output[0])/rate))
    return (x_output,rate)