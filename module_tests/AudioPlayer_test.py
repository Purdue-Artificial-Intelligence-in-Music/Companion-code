import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pyaudio

# relative import
# from src.AudioPlayer import AudioPlayer, normalize_audio
from src.AudioPlayer import AudioPlayer, normalize_audio


class TestNormalizeAudio(unittest.TestCase):
    def test_normalize_audio(self):
        """Test if audio is normalized correctly."""
        # all audio inputs should be non-empty
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
        # Create an AudioPlayer object
        self.player = AudioPlayer(path="test.wav")
        # with patch, self.player.p is already a MagicMock, just need to ensure the open method is also a mock
        assert isinstance(self.player.p.open, MagicMock), f"is of type {type(self.player.p.open)}"
        # assertion seems not failing

    def test_initialization(self):
        """Test initialization of AudioPlayer attributes."""
        self.assertEqual(self.player.path, "test.wav")
        self.assertEqual(self.player.sample_rate, 16000)
        self.assertEqual(self.player.channels, 1)
        self.assertEqual(self.player.frames_per_buffer, 2048)

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
        # first ensure self.player.p.open is a MagicMock
        self.assertTrue(isinstance(self.player.p.open, MagicMock))

        """Test if PyAudio.open() is called once in AudioPlayer.start() method"""
        self.player.start()
        self.player.p.open.assert_called_once()

        """Test if PyAudio.close() is called once in AudioPlayer.start() method"""
        self.player.stop()
        self.player.stream.close.assert_called_once()   # .close() closes PortAudio's stream (a small resource offered by PortAudio)
        self.player.p.terminate.assert_called_once()    # .terminate() releases entire PortAudio's resource

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
        """When there isn't a pyAudio stream object"""
        self.assertTrue(self.player.stream is None)
        self.assertFalse(self.player.is_active())

        """When there is a pyAudio stream object"""
        # instantiate a pyAudio stream
        self.player.start()
        self.assertTrue(self.player.is_active())

    def test_get_time(self):
        """Test getting the current timestamp in the audio being played."""
        self.player.get_next_frames()

# maybe focus a little more about get_next_frames

if __name__ == '__main__':
    unittest.main()
