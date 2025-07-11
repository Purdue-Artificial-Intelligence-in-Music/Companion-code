from .features import Features

import numpy as np
import librosa


class MelSpecFeatures(Features):
    FEATURE_LEN = 128

    def __init__(self, sr, win_length, hop_length, num_features=0):
        super().__init__(
            sr=sr,
            hop_length=hop_length,
            win_length=win_length,
            num_features=num_features,
        )

    def compare_features(self, other, i, j):
        return np.dot(self.get_feature(i), other.get_feature(j))

    def make_feature(self, y):
        # mel spectogram
        S = librosa.feature.melspectrogram(
            y=y,
            sr=self.sr,
            n_fft=self.win_length,
            hop_length=self.win_length,
            win_length=self.win_length,
            power=1.0,
            n_mels=self.FEATURE_LEN,
        )

        # convert to decibel to prevent skewing by loudness
        S_dB = librosa.power_to_db(S, ref=np.max, top_db=80)

        # 1 vector because win len = win len
        mel_vec = S_dB[:, 0]

        # shift to non-negative
        mel_vec = mel_vec - mel_vec.min()

        # L2 Normalize
        mel_vec = mel_vec / np.linalg.norm(mel_vec)

        return mel_vec
