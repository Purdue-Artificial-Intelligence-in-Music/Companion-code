import unittest
from unittest import mock
import numpy as np
import soundfile
from Synchronizer import Synchronizer
from ScoreFollower import ScoreFollower
from AudioPlayer import AudioPlayer
from simple_pid import PID

#
# TODO: Pretty sure I need actual file paths for reference & accompaniment, those are just dummy paths right now
#

class TestSynchronizer(unittest.TestCase):

    # Test case 1: Initialization of the Synchronizer Object
    def test_synchronizer_initialization(self):
        reference = "path/to/score"
        accompaniment = "path/to/accompaniment"
        synchronizer = Synchronizer(reference, accompaniment)

        self.assertEqual(synchronizer.sample_rate, 44100)
        self.assertEqual(synchronizer.c, 10)
        self.assertIsInstance(synchronizer.score_follower, ScoreFollower)
        self.assertIsInstance(synchronizer.player, AudioPlayer)
        self.assertIsInstance(synchronizer.PID, PID)

    # Test case 2: Start Functionality
    @mock.patch.object(ScoreFollower, 'start')
    @mock.patch.object(AudioPlayer, 'start')
    def test_synchronizer_start(self, mock_player_start, mock_score_follower_start):
        reference = "path/to/score"
        accompaniment = "path/to/accompaniment"
        synchronizer = Synchronizer(reference, accompaniment)

        synchronizer.start()

        mock_score_follower_start.assert_called_once()
        mock_player_start.assert_called_once()

    # Test case 3: Pause and Unpause Functionality
    @mock.patch.object(ScoreFollower, 'pause')
    @mock.patch.object(AudioPlayer, 'pause')
    @mock.patch.object(ScoreFollower, 'unpause')
    @mock.patch.object(AudioPlayer, 'unpause')
    def test_synchronizer_pause_unpause(self, mock_player_unpause, mock_score_follower_unpause, mock_player_pause, mock_score_follower_pause):
        reference = "path/to/score"
        accompaniment = "path/to/accompaniment"
        synchronizer = Synchronizer(reference, accompaniment)

        synchronizer.pause()
        mock_score_follower_pause.assert_called_once()
        mock_player_pause.assert_called_once()

        synchronizer.unpause()
        mock_score_follower_unpause.assert_called_once()
        mock_player_unpause.assert_called_once()

    # Test case 4: Stop Functionality
    @mock.patch.object(ScoreFollower, 'stop')
    @mock.patch.object(AudioPlayer, 'stop')
    def test_synchronizer_stop(self, mock_player_stop, mock_score_follower_stop):
        reference = "path/to/score"
        accompaniment = "path/to/accompaniment"
        synchronizer = Synchronizer(reference, accompaniment)

        synchronizer.stop()

        mock_score_follower_stop.assert_called_once()
        mock_player_stop.assert_called_once()

    # Test case 5: Update Functionality
    @mock.patch.object(ScoreFollower, 'step', return_value=5)
    @mock.patch.object(Synchronizer, 'accompanist_time', return_value=5.0)
    @mock.patch.object(Synchronizer, 'estimated_time', return_value=4.0)
    def test_synchronizer_update(self, mock_estimated_time, mock_accompanist_time, mock_score_follower_step):
        reference = "path/to/score"
        accompaniment = "path/to/accompaniment"
        synchronizer = Synchronizer(reference, accompaniment)

        synchronizer.update()

        error = synchronizer.accompanist_time() - synchronizer.estimated_time()
        playback_rate = synchronizer.PID(error)
        self.assertEqual(synchronizer.player.playback_rate, playback_rate)

    # Test case 6: Is Active Functionality
    @mock.patch.object(ScoreFollower, 'is_active', return_value=True)
    @mock.patch.object(AudioPlayer, 'is_active', return_value=True)
    def test_synchronizer_is_active(self, mock_player_is_active, mock_score_follower_is_active):
        reference = "path/to/score"
        accompaniment = "path/to/accompaniment"
        synchronizer = Synchronizer(reference, accompaniment)

        self.assertTrue(synchronizer.is_active())

        mock_score_follower_is_active.return_value = False
        self.assertFalse(synchronizer.is_active())

    # Test case 7: Save Performance
    @mock.patch('soundfile.write')
    @mock.patch.object(ScoreFollower, 'mic')
    def test_save_performance(self, mock_mic, mock_soundfile_write):
        reference = "path/to/score"
        accompaniment = "path/to/accompaniment"
        synchronizer = Synchronizer(reference, accompaniment)

        mock_mic_log = np.random.random((1, 1000))
        mock_player_log = np.random.random((1, 1000))

        mock_mic.get_audio.return_value = mock_mic_log
        synchronizer.player.output_log = mock_player_log

        synchronizer.save_performance('path/to/output.wav')

        mock_soundfile_write.assert_called_once_with('path/to/output.wav', np.hstack([mock_mic_log, mock_player_log]), synchronizer.sample_rate)

if __name__ == '__main__':
    unittest.main()
