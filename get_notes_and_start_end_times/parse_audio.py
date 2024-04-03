"""this is the main file containing all functions required to parse input audio"""
from music21 import *
import numpy as np
import math

#to correctly get the exact start and end times, the sampling rate should be given
SAMPLING_RATE = 44100       #assumed default sampling rate if set_sampling_rate is not called

def set_sampling_rate(sr: int) -> None:
    SAMPLING_RATE = sr

def get_start_end_time_of_notes(freq_keys: list[float], audio: np.array) -> dict[float : tuple[int, int]]:
    # initialize the dictionary
    freq_to_time = {freq: [0,0] for freq in freq_keys}
    n_samples = len(audio)

    # fill-in start and end times
    for idx, sample in enumerate(audio):
        sample = np.abs(sample)         #prevent negative frequency
        if sample not in freq_keys:
            print(f'sample frequency {sample:.2f} is not in parsed score')
            continue
        freq_to_time[sample][0] = idx / SAMPLING_RATE # fill-in start time
        end_idx = idx + 1
        # if a note is played following some pause (i.e. audio[idx+1:(somewhere)] = 0.0)
        # if a note is played following some pause (i.e. audio[idx+1:(somewhere)] = 0.0)
        while (end_idx < n_samples) and (audio[end_idx] == 0.0):
            end_idx += 1
        freq_to_time[sample][1] = end_idx/ SAMPLING_RATE

    # convert the filled-in dictionary to float:tuple
    freq_to_time = {freq : tuple(pair) for freq,pair in freq_to_time.items()}
    return freq_to_time