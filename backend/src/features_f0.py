from .features import Features

import numpy as np
import librosa

class F0Features(Features):
    FEATURE_LEN = 5

    def __init__(self, sr, win_len, num_features=0):
        super().__init__(sr=sr, win_len=win_len, num_features=num_features)

    def compare_features(self, other, i, j):
        f1 = self.get_feature(i)
        f2 = other.get_feature(j)
      
        if np.any(np.isnan(f1)) or np.any(np.isnan(f2)):
            return 0.0
        
        p1 = librosa.hz_to_midi(f1)
        p2 = librosa.hz_to_midi(f2)

        diffs = np.abs(p1 - p2)
        min_diff = np.min(diffs)

        # Convert semitone difference to similarity via Gaussian
        sigma = 1.5 
        result = np.exp(-0.5 * (min_diff / sigma) ** 2)

        return result
    
    def make_feature(self, y):
        test0 = librosa.yin(y,
                     fmin=librosa.note_to_hz('C2'),
                     fmax=librosa.note_to_hz('C7'),
                     sr=self.sr, 
                    #  frame_length=self.win_len // self.FEATURE_LEN,
                     center=False)
        return test0

    