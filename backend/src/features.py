import numpy as np
import librosa

class Features(object):
    FEATURE_LEN = 0

    def __init__(self, sr, win_len, num_features=0):
        '''Streaming implementation of wave-to-feature. Initialize with sr, win_len.
        Then call .insert(y) to add a frame of win_len samples.'''
        self.sr = sr
        self.win_len = win_len

        self.num_features = num_features
        self.preallocated = num_features > 0

        if self.preallocated:
            self.buffer = np.zeros((self.FEATURE_LEN, self.num_features))
        else:
            self.buffer = []
        
        self.current_index = 0

    def compare_features(self, other: 'Features', i: int, j: int):
        raise NotImplementedError("Subclasses must implement compare_features()")

    def make_feature(self, audio: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Subclasses must implement make_feature()")
    
    def insert(self, audio: np.ndarray) -> np.ndarray:
        'Insert new audio y. Return a (feature_size, 1) vector representing a feature.'
        vec = self.make_feature(audio)

        if self.preallocated:
            if self.current_index >= self.buffer.shape[1]:
                raise IndexError("Buffer full")
            self.buffer[:, self.current_index] = vec
        else:
            self.buffer.append(vec)
            self.num_features += 1

        self.current_index += 1

        return vec
    
    def get_feature(self, index: int) -> np.ndarray:
        if self.preallocated:
            return self.buffer[:, index]
        else:
            return self.buffer[index]
        
    def get_featuregram(self) -> np.ndarray:
        'Return buffer as ndarray with shape: (FEATURE_SIZE, num_features)'
        if self.preallocated:
            return self.buffer
        else:
            return np.stack(self.buffer, axis=1)

    @classmethod
    def from_audio(cls, y: np.ndarray, sr: int, win_len: int, hop_len: int):
        'Factory method. Load audio and instantiate based on params'
        num_features = (len(y) - win_len) // hop_len + 1
        num_features = max(0, num_features)

        out = cls(sr, win_len)

        for m in range(num_features):
            window = y[m*hop_len:m*hop_len+win_len]
            out.insert(window)

        return out
    
    @classmethod
    def from_file(cls, filepath, sr: int, win_len: int, hop_len: int):
        'Factory method. Load a file and convert to an np-cens chromagram based on params'
        y, _ = librosa.load(path=filepath, sr=sr, mono=True)
        return cls.from_audio(y, sr, win_len, hop_len)