import numpy as np
from AudioBuffer import AudioBuffer
from BeatTracker import BeatTracker

class WavBeatTracker(BeatTracker):
    """Track how many beats have been played in a WAV file"""
    def __init__(self, BUFFER: AudioBuffer):
        super().__init__()
        self.BUFFER = BUFFER
        self.beats = BUFFER.wav_beats
        self.len_beats = len(self.beats)
        self.downbeats = 0
        self.total_beats = 0
        self.next_beat_idx = 0
        self.next_beat_sample_idx = BUFFER.wav_beats[0][0]
        self.daemon = True

    def update_beats(self):
        """Compares the WAV index to known beat positions to update how many beats have been played """
        curr_sample_idx = self.BUFFER.wav_index
        while self.next_beat_idx < self.len_beats and curr_sample_idx > self.next_beat_sample_idx:
            type = self.BUFFER.wav_beats[self.next_beat_idx][1]
            if type == 1:
                self.downbeats += 1
            self.total_beats += 1
            self.next_beat_idx += 1
            self.next_beat_sample_idx = self.BUFFER.wav_beats[self.next_beat_idx][0]
    
    def get_downbeats(self) -> int:
        """Return the updated number of downbeats that have been played."""
        self.update_beats()
        return self.downbeats
    
    def get_total_beats(self) -> int:
        """Return the updataed number of beats (upbeats and downbeats) that have been played."""
        self.update_beats()
        return self.total_beats
    
    def get_current_beats(self):
        """Return the indices of the frames of all beats that have been played """
        self.update_beats()
        return self.beats[:self.next_beat_idx]
