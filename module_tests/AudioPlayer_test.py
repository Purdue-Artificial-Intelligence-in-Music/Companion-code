import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pyaudio
from audio_player_module import AudioPlayer, normalize_audio  # Assume the above code is in audio_player_module.py


class TestNormalizeAudio(unittest.TestCase):
    def test_normalize_audio(self):
        """Test if audio is normalized correctly."""
        audio = np.array([0.5, -0.5, 0.75, -0.75, 1.0, -1.0])
        normalized_audio = normalize_audio(audio)
        self.assertTrue(np.all(normalized_audio <= 1.0))
        self.assertTrue(np.all(normalized_audio >= -1.0))
        np.testing.assert_almost_equal(np.max(np.abs(normalized_audio)), 1.0)


class TestAudioPlayer(unittest.TestCase):
    @patch('librosa.load')
    @patch('pyaudio.PyAudio')
    def setUp(self, mock_pyaudio, mock_librosa):
        """Set up the AudioPlayer with mock dependencies."""
        mock_librosa.return_value = (np.random.randn(16000), 16000)
        mock_pyaudio_instance = mock_pyaudio.return_value
        mock_pyaudio_instance.open.return_value = MagicMock()
        self.mock_stream = mock_pyaudio_instance.open.return_value

        # Create an AudioPlayer object
        self.player = AudioPlayer(path="test.wav")

    def test_initialization(self):
        """Test initialization of AudioPlayer attributes."""
        self.assertEqual(self.player.path, "test.wav")
        self.assertEqual(self.player.sample_rate, 16000)
        self.assertEqual(self.player.channels, 1)
        self.assertEqual(self.player.frames_per_buffer, 1024)

    def test_audio_loading(self):
        """Test if audio is loaded correctly."""
        self.assertIsInstance(self.player.audio, np.ndarray)
        self.assertEqual(self.player.audio.shape[0], 1)  # mono audio reshaped

    def test_get_next_frames(self):
        """Test the time-stretching and frame fetching."""
        frames = self.player.get_next_frames()
        self.assertIsInstance(frames, np.ndarray)
        self.assertEqual(frames.shape, (self.player.channels, self.player.frames_per_buffer))

    def test_pyaudio_stream(self):
        """Test starting and stopping the PyAudio stream."""
        self.player.start()
        self.mock_stream.start_stream.assert_called_once()

        self.player.stop()
        self.mock_stream.close.assert_called_once()

    def test_callback(self):
        """Test the callback function which provides audio frames."""
        self.player.get_next_frames = MagicMock(return_value=np.random.randn(1, 1024))
        output, flag = self.player.callback(None, 1024, None, None)
        self.assertEqual(output.shape, (1, 1024))
        self.assertEqual(flag, pyaudio.paContinue)

    def test_pause_unpause(self):
        """Test pausing and unpausing audio playback."""
        self.player.pause()
        self.assertTrue(self.player.paused)
        
        self.player.unpause()
        self.assertFalse(self.player.paused)

    def test_is_active(self):
        """Test if the stream is active."""
        self.mock_stream.is_active.return_value = True
        self.assertTrue(self.player.is_active())

        self.mock_stream.is_active.return_value = False
        self.assertFalse(self.player.is_active())

    def test_get_time(self):
        """Test getting the current timestamp in the audio being played."""
        self.player.k = 160
        expected_time = (160 * self.player.hop_length) / self.player.sample_rate
        self.assertEqual(self.player.get_time(), expected_time)


if __name__ == '__main__':
    unittest.main()
