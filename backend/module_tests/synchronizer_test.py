import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from src.synchronizer import Synchronizer

class TestSynchronizer(unittest.TestCase):
    @patch('src.synchronizer.ScoreFollower')
    @patch('src.audio_buffer.AudioBuffer')
    @patch('simple_pid.PID')
    @patch('librosa.load')
    def setUp(self, MockLibrosaLoad, MockPID, MockAudioBuffer, MockScoreFollower):
        # Mock librosa.load to avoid loading an actual file
        MockLibrosaLoad.return_value = (np.random.random(44100), 44100)

        # Mock ScoreFollower, AudioBuffer, and PID
        self.mock_score_follower = MockScoreFollower.return_value
        self.mock_audio_buffer = MockAudioBuffer.return_value
        self.mock_pid = MockPID.return_value

        # Instantiate Synchronizer
        self.synchronizer = Synchronizer(reference='path/to/score')

    def test_synchronizer_initialization(self):
        self.assertEqual(self.synchronizer.sample_rate, 44100)
        self.assertEqual(self.synchronizer.c, 10)

    def test_synchronizer_step(self):
        frames = np.random.random((1, 8192))
        soloist_time = 8192 / 44100
        accompanist_time = 8192 / 44100

        # Ensure that score_follower.step returns the correct soloist_time
        self.synchronizer.score_follower.step = MagicMock(return_value=soloist_time)
        
        # Spy on the live_buffer.write method
        self.synchronizer.live_buffer.write = MagicMock()

        playback_rate, estimated_time = self.synchronizer.step(frames, accompanist_time)

        # Assert that live_buffer.write was called with correct arguments
        self.synchronizer.live_buffer.write.assert_called_once_with(frames)

        self.assertEqual(playback_rate, 1.0)
        self.assertEqual(estimated_time, soloist_time)

    def test_save_performance(self):
        # Spy on the live_buffer.save method
        self.synchronizer.live_buffer.save = MagicMock()

        # Call the method under test
        path = "path/to/save"
        self.synchronizer.save_performance(path)

        # Assert that live_buffer.save was called with the correct arguments
        self.synchronizer.live_buffer.save.assert_called_once_with(path)

if __name__ == '__main__':
    unittest.main()
