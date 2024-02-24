"""
File: TsmThread.py
Description: This file contains the definition of the TimeStretchThread class,
    which is a threaded implementation for time-stretching audio based on microphone and WAV tempos,
    and process_func() function, which performs time-stretching on WAV audio based on microphone
    and WAV tempos.
Key Functions:
- run(): The main method of the TimeStretchThread class that performs the time-stretching operation.
- process_func(wav_tempo, mic_tempo, wav_data): Performs time-stretching on WAV audio
  using the provided tempos and returns the time-stretch ratio.
"""

import numpy as np
import pytsmod as tsm
import soundfile as sf
import threading
from Tsm import time_stretch

class TimeStretchThread(threading.Thread):
    def __init__(self, wav_tempo, mic_tempo, input_file, output_filepath):
        threading.Thread.__init__(self) 
        self.input_file = input_file
        self.pairs = 0
        self.output_filepath = output_filepath
        self.stop_request = False
        self.mic_tempo = mic_tempo
        self.wav_tempo = wav_tempo
        self.timestretch_ratio = 0
        self.output = None

    def run(self):
        while not self.stop_request:
            data = self.AThread.get_n_samples(1000)
            if data is not None and len(data) > 5000:
                x, sr = time_stretch(data, self.BeatThread.output)
                self.output = x
            tempo_microphone = self.mic_tempo     # Get the tempo of the microphone audio from the beatThread
            tempo_wav = self.wav_tempo  # Get the tempo of the wav audio from the beatThread
            self.timestretch_ratio = float(tempo_wav) /tempo_microphone
            self.stop_request = True
               # sf.write(self.output_filepath, np.ravel(self.output), sr)




def process_func(wav_tempo, mic_tempo, wav_data):
    '''
    Perform time-stretching on the WAV audio based on microphone and WAV tempos.

    Args:
    - wav_tempo: Tempo of the WAV audio (float)
    - mic_tempo: Tempo of the microphone audio (float)
    - wav_data: WAV audio data (numpy array)

    Returns:
    - timestretch_ratio: Time-stretch ratio (float)
    '''
    tempo_microphone = mic_tempo    # Get the tempo of the microphone audio from the beatThread
    tempo_wav = wav_tempo  # Get the tempo of the wav audio from the beatThread
    timestretch_ratio = tempo_microphone / tempo_wav # Calculate the time-stretch ratio
    timestretched_wav = time_stretch(wav_data, timestretch_ratio) # Perform time-stretching on the wav audio using the ratio

    # self.previous_microphone_tempo = tempo_microphone
    # self.previous_wav_tempo = tempo_wav
    return timestretch_ratio

