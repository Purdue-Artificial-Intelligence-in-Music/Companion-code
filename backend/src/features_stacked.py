from src.features_cens import CENSFeatures
from src.features_mel_spec import MelSpecFeatures
from src.features_f0 import F0Features
from .features import Features

import numpy as np


class StackedFeatures(Features):
    FEATURE_LEN = F0Features.FEATURE_LEN + MelSpecFeatures.FEATURE_LEN

    # FEATURE_LENS = [F0Features.FEATURE_LEN, MelSpecFeatures.FEATURE_LEN]

    def __init__(self, sr, hop_length, win_length, num_features=0):
        self.f0 = F0Features(sr, hop_length=hop_length, win_length=win_length)
        self.mel = MelSpecFeatures(sr, hop_length=hop_length, win_length=win_length)
        super().__init__(
            sr=sr,
            hop_length=hop_length,
            win_length=win_length,
            num_features=num_features,
        )

    def compare_features(self, other, i, j):
        feat_1 = self.get_feature(i)
        feat_2 = other.get_feature(j)

        def compare_f0(f0_1, f0_2):
            if np.any(np.isnan(f0_1)) or np.any(np.isnan(f0_2)):
                # TODO: warning
                return 0.0

            diffs = np.abs(f0_1 - f0_2)
            min_diff = np.min(diffs)

            # Convert semitone difference to similarity via Gaussian
            sigma = 1.5
            result = np.exp(-0.5 * (min_diff / sigma) ** 2)

            return result

        f0_1 = feat_1[: F0Features.FEATURE_LEN]
        mel_1 = feat_1[F0Features.FEATURE_LEN :]

        f0_2 = feat_2[: F0Features.FEATURE_LEN]
        mel_2 = feat_2[F0Features.FEATURE_LEN :]

        return (compare_f0(f0_1, f0_2) + np.dot(mel_1, mel_2)) / 2.0

    def make_feature(self, y):
        f0_feat = self.f0.make_feature(y)
        mel_feat = self.mel.make_feature(y)
        stacked_feat = np.concatenate((f0_feat, mel_feat))
        # print(stacked_feat.shape)
        return stacked_feat
