import numpy as np
import librosa

class Features(object):
    FEATURE_SIZE = 0

    def __init__(self, sr, win_len):
        '''Streaming implementation of wave-to-feature. Initialize with sr, win_len.
        Then call .insert(y) to add a frame of win_len samples.'''
        self.sr = sr
        self.win_len = win_len

        self.buffer = []

    def insert(self, y):
        'Insert new audio y. Return a (feature_size, 1) vector representing a feature.'
        raise NotImplementedError("Subclasses must implement insert()")
    
    def access(self, index):
        'Access a feature at index feature_ind. Return a (feature_size, 1) vector representing a feature.'
        raise NotImplementedError("Subclasses must implement access()")
    
    def get_buffer(self):
        'Return buffer as ndarray with shape: (FEATURE_SIZE, num_features)'
        return np.stack(self.buffer, axis=1)

    @classmethod
    def from_audio(cls, y, sr, win_len, hop_len):
        'Factory method. Load audio and instantiate based on params'
        num_features = (len(y) - win_len) // hop_len + 1
        num_features = max(0, num_features)

        out = cls(sr, win_len)

        for m in range(num_features):
            window = y[m*hop_len:m*hop_len+win_len]
            out.insert(window)

        return out
    
    @classmethod
    def from_file(cls, filepath, sr, win_len, hop_len):
        'Factory method. Load a file and convert to an np-cens chromagram based on params'
        y, _ = librosa.load(path=filepath, sr=sr, mono=True)
        return cls.from_audio(y, sr, win_len, hop_len)