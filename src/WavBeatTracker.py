import numpy as np
from AudioPlayer import AudioPlayer
from BeatTracker import BeatTracker
from BeatNet_local.BeatNet_files import BeatNet_for_audio_arr
import os

class WavBeatTracker(BeatTracker):
    """Track how many beats have been played in a WAV file"""
    def __init__(self, player: AudioPlayer):
        super().__init__()
        self.player = player
        self.beats = None
        self.calc_beats()
        self.len_beats = len(self.beats)
        self.downbeats = 0
        self.total_beats = 0
        self.next_beat_idx = 0
        self.next_beat_sample_idx = self.beats[0][0]
        self.daemon = True

    def calc_beats(self):
        cwd = os.getcwd()
        if not os.path.exists(os.path.join(cwd, "beat_cache/")):
            os.mkdir(os.path.join(cwd, "beat_cache/"))
        modified_wav_file_name = self.player.path.replace("\\", "/")
        beat_path = os.path.join(cwd, "beat_cache/") + str(modified_wav_file_name.split("/")[-1]) + ".npy"
        if os.path.exists(beat_path):
            self.beats = np.load(beat_path)
        else:
            estimator = BeatNet_for_audio_arr(1, mode='online', inference_model='PF', plot=[], thread=False, sample_rate=self.player.sample_rate)
            self.beats = estimator.process(self.player.audio)
            for i in range(len(self.beats)):
                self.beats[i][0] = int(self.beats[i][0] * self.player.sample_rate)
            self.beats = np.array(self.beats)
            np.save(beat_path, self.beats)

    def update_beats(self):
        """Compares the WAV index to known beat positions to update how many beats have been played """
        curr_sample_idx = self.player.index
        while self.next_beat_idx < self.len_beats and curr_sample_idx > self.next_beat_sample_idx:
            type = self.beats[self.next_beat_idx][1]
            if type == 1:
                self.downbeats += 1
            self.total_beats += 1
            self.next_beat_idx += 1
            self.next_beat_sample_idx = self.beats[self.next_beat_idx][0]
    
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
