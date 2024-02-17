"""this is the main file containing all functions required to parse input audio"""
from music21 import *
import numpy as np
import math

#to correctly get the exact start and end times, the sampling rate should be given
SAMPLING_RATE = 44100       #assumed default sampling rate if set_sampling_rate is not called

def set_sampling_rate(sr: int) -> None:
    SAMPLING_RATE = sr

def get_start_end_time_of_notes(freq_keys: list[float], audio: np.array) -> dict[float : tuple[int, int]]:
    
    return None