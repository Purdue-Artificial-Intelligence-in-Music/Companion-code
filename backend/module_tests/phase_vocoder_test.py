import unittest
from unittest.mock import patch
import numpy as np
from src.phase_vocoder import PhaseVocoder, normalize_audio        # what is this normalize_audio?


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
    def setUp(self, mock_librosa):
        """Set up the AudioPlayer with mock dependencies."""
        mock_librosa.return_value = (np.random.randn(16000), 16000)

        # Create a PhaseVocoder object
        self.phase_vocoder = PhaseVocoder(path="test.wav")

    def test_initialization(self):
        """Test initialization of AudioPlayer attributes."""
        self.assertEqual(self.phase_vocoder.path, "test.wav")
        self.assertEqual(self.phase_vocoder.sample_rate, 16000)
        self.assertEqual(self.phase_vocoder.channels, 1)

    def test_audio_loading(self):
        """Test if audio is loaded correctly."""
        self.assertIsInstance(self.phase_vocoder.audio, np.ndarray)
        self.assertEqual(self.phase_vocoder.audio.shape[0], 1)  # mono audio reshaped

    def test_get_next_frames(self):
        """Test the time-stretching and frame fetching."""
        frames = self.phase_vocoder.get_next_frames()
        self.assertIsInstance(frames, np.ndarray)
        self.assertEqual(frames.shape, (self.phase_vocoder.channels, self.phase_vocoder.hop_length))

    def test_get_time(self):
        """Test getting the current timestamp in the audio being played."""
        self.assertEqual(self.phase_vocoder.get_time(), self.phase_vocoder.audio_index / self.phase_vocoder.sample_rate)

    def test_set_playback_rate(self):
        """Test setting the playback rate of the audio."""
        self.phase_vocoder.set_playback_rate(2)
        self.assertEqual(self.phase_vocoder.playback_rate, 2)

if __name__ == '__main__':
    unittest.main()
