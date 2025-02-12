import unittest
import numpy as np
import os
import librosa
from src.score_follower import ScoreFollower

class TestScoreFollower(unittest.TestCase):
    def test_get_chroma(self):
        ref_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'data', 'test', 'bach_prelude.wav')

        score_follower = ScoreFollower(reference=ref_path,
                                   c=10,
                                   max_run_count=3,
                                   diag_weight=0.5,
                                   sample_rate=44100,
                                   win_length=8192)
        sample_frames = np.zeros((1,2))
        chroma = score_follower._get_chroma(sample_frames)
        for i in chroma:
            print(i)

        self.assertTrue(len(chroma) == 12)

    def test_step(self):
        ref_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'data', 'test', 'bach_prelude.wav')
        source = os.path.join(os.path.dirname(__file__), '..', 'data', 'data', 'test', 'bach_prelude.wav')

        sample_rate = 44100
        win_length = 8192

        score_follower = ScoreFollower(reference=ref_path,
                                   c=10,
                                   max_run_count=3,
                                   diag_weight=0.5,
                                   sample_rate=sample_rate,
                                   win_length=win_length)
        
        source_audio = librosa.load(source, sr=44100)
        source_audio = source_audio[0].reshape((1, -1))
        
        prev_time = 0
        change = win_length / sample_rate

        for i in range(0, source_audio.shape[-1], 8192):
            frames = source_audio[:, i:i+8192]
            estimated_time = score_follower.step(frames)
            print(f'Estimated: {estimated_time} Increase: {estimated_time - prev_time} Change: {change}')

            prev_time = estimated_time
            # print(
            #    f'Live index: {score_follower.otw.live_index}, Ref index: {score_follower.otw.ref_index}')
