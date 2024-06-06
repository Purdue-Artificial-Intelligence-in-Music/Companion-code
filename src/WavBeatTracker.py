import numpy as np
from AudioBuffer import AudioBuffer
from BeatTracker import BeatTracker

class WavBeatTracker(BeatTracker):
    def __init__(self, BUFFER: AudioBuffer):
        self.BUFFER = BUFFER
        self.beats = BUFFER.wav_beats
        self.len_beats = len(self.beats)
        self.downbeats = 0
        self.total_beats = 0
        self.next_beat_idx = 0
        self.next_beat_sample_idx = BUFFER.wav_beats[0][0]

    def update_beats(self):
        curr_sample_idx = self.BUFFER.wav_index
        while self.next_beat_idx < self.len_beats and curr_sample_idx > self.next_beat_sample_idx:
            type = self.BUFFER.wav_beats[self.next_beat_sample_idx][1]
            if type == 1:
                self.downbeats += 1
            self.total_beats = 0
            self.next_beat_idx += 1
            self.next_beat_sample_idx = self.BUFFER.wav_beats[self.next_beat_idx][0]
    
    def get_downbeats(self) -> int:
        self.update_beats()
        return self.downbeats
    
    def get_total_beats(self) -> int:
        self.update_beats()
        return self.total_beats
    
    def get_current_beats(self):
        self.update_beats()
        return self.beats[:self.next_beat_idx]