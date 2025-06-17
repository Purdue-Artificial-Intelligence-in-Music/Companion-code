from .features import Features

import numpy as np
import librosa

class F0Features(Features):
    # By defualt, librosa splits y into 5 sections
    FEATURE_LEN = 5

    def __init__(self, sr, win_len, num_features=0):
        super().__init__(sr=sr, win_len=win_len, num_features=num_features)

    def compare_features(self, other, i, j):
        f1 = self.get_feature(i)
        f2 = other.get_feature(j)
      
        if np.any(np.isnan(f1)) or np.any(np.isnan(f2)):
            return 0.0
        
        diffs = np.abs(f1 - f2)
        min_diff = np.min(diffs)

        # Convert semitone difference to similarity via Gaussian
        sigma = 1.5 
        result = np.exp(-0.5 * (min_diff / sigma) ** 2)

        return result
    
    def make_feature(self, y):
        f0_vec = librosa.yin(y,
                     fmin=librosa.note_to_hz('C2'),
                     fmax=librosa.note_to_hz('C7'),
                     sr=self.sr, 
                     center=False)
        
        # Use midi for consistent interval distances
        midi_vec = librosa.hz_to_midi(f0_vec)
        return midi_vec

    