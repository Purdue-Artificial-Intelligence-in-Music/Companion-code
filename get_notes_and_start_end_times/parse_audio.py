"""this is the main file containing all functions required to parse input audio"""
from music21 import *
import numpy as np
import math

#to correctly get the exact start and end times, the sampling rate should be given
SAMPLING_RATE = 44100       #assumed default sampling rate if set_sampling_rate is not called

def set_sampling_rate(sr: int) -> None:
    SAMPLING_RATE = sr

def get_start_end_time_of_notes(freq_keys: list[float], audio: np.array) -> dict[float : tuple[int, int]]:
    # note that freq_keys.length <= audio.length
    freq_to_time = {freq: [0,0] for freq in freq_keys}
    # try to account for repeated notes in a section (e.g. if an audio plays 4 C notes in a single measure, make sure to get the correct start end times for each C)
    for idx, sample in enumerate(audio):
        freq_to_time[sample][0] = idx / SAMPLING_RATE
        freq_to_time[sample][1] = (idx + 1)/ SAMPLING_RATE

    for freq in freq_to_time.keys():
        freq_to_time[freq] = tuple(freq_to_time[freq])

    return freq_to_time