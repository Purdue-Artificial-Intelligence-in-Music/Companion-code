"""
File: Tsm.py
Description: This file contains functions for audio processing, including time-stretching and splitting audio files.
Functions:
- split_file(x, sr, time, tempo): Splits an audio file into multiple chunks based on time and tempo.
- time_stretch(input_file, pairs): Time-stretches an audio file based on specified time and tempo pairs.
"""


import numpy as np
import pytsmod as tsm
import soundfile as sf


def split_file(x,sr,time,tempo):
    '''
    Split the input audio file into multiple chunks based on time and tempo.

    Args:
    - x: Soundfile data (numpy array)
    - sr: Sample rate (integer)
    - time: List of time boundaries (seconds)
    - tempo: List of tempos (beats per minute)

    Returns:
    - x_split: List of audio chunks
    - scale: List of scaling factors
    '''
    x_split = []
    scale = []
    temp = []
    time.append((x.shape[-1])/sr)
    for i in range(len(time)-1):
        i1 = int(time[i]*sr)
        i2 = int((time[i+1]*sr)+1)
        # Split the audio into chunks
        print(i1,i2)
        temp = x[:,i1:i2].copy()
        print(temp)
        x_split.append(temp)
        # Calculate the scaling factor based on tempo
        scale.append(120/tempo[i])
    return(x_split, scale)

def time_stretch(input_file, pairs):
    '''
    Time-stretch an audio file based on specified time and tempo pairs.

    Args:
    - input_file: Path to the input WAV file
    - pairs: List of time and tempo pairs [(time, tempo), ...]

    Returns:
    - x_output: Time-stretched audio data
    - sr: Sample rate
    '''
    x,sr = sf.read(input_file) #gets data and sample rate
    x = x.T
    print("length:",len(x[0]),"sr:",sr,"time:",(len(x[0])/sr))
    print(x)
    #gets data from pair
    time = pairs[0]
    bpm = pairs[1]
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
