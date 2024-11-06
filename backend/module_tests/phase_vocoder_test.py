import unittest
from unittest.mock import patch
import numpy as np
from phase_vocoder import PhaseVocoder, normalize_audio


class TestNormalizeAudio(unittest.TestCase):
    def test_normalize_audio(self):
        """Test if audio is normalized correctly."""
        # all audio inputs should be non-empty
        audio = np.array([0.5, -0.5, 0.75, -0.75, 1.0, -1.0])
        normalized_audio = normalize_audio(audio)
        self.assertTrue(np.all(normalized_audio <= 1.0))
        self.assertTrue(np.all(normalized_audio >= -1.0))
        np.testing.assert_almost_equal(np.max(np.abs(normalized_audio)), 1.0)

class TestPhaseVocoder(unittest.TestCase):
    @patch('librosa.load')
    def setUp(self, mock_load):
        # Mock librosa.load to avoid loading an actual file
        mock_load.return_value = (np.random.random(44100), 44100)
        
        # Instantiate the PhaseVocoder
        self.phase_vocoder = PhaseVocoder(path='dummy_path.wav',
                                          playback_rate=1.0,
                                          sample_rate=44100,
                                          channels=1,
                                          n_fft=8192,
                                          win_length=8192,
                                          hop_length=2048)

    def test_initialization(self):
        # Test if the PhaseVocoder is initialized properly
        self.assertEqual(self.phase_vocoder.sample_rate, 44100)
        self.assertEqual(self.phase_vocoder.playback_rate, 1.0)
        self.assertEqual(self.phase_vocoder.channels, 1)
        self.assertEqual(self.phase_vocoder.n_fft, 8192)
        self.assertEqual(self.phase_vocoder.win_length, 8192)
        self.assertEqual(self.phase_vocoder.hop_length, 2048)
        
        # Check if audio is normalized between [-1, 1]
        self.assertTrue(np.max(np.abs(self.phase_vocoder.audio)) <= 1.0)

    @patch('librosa.load')
    @patch('librosa.core.stft')
    def test_stft_computation(self, mock_stft, mock_load):
        # Mock librosa.load to avoid loading an actual file
        mock_load.return_value = (np.random.random(44100), 44100)
        
        # Mock STFT to return a predefined complex array
        mock_stft.return_value = np.random.random((1, 4096)) + 1j * np.random.random((1, 4096))
        
        # Reinitialize PhaseVocoder to trigger STFT computation
        self.phase_vocoder = PhaseVocoder(path='dummy_path.wav',
                                          playback_rate=1.0,
                                          sample_rate=44100,
                                          channels=1,
                                          n_fft=8192,
                                          win_length=8192,
                                          hop_length=2048)
        
        # Verify STFT was called
        mock_stft.assert_called_once_with(self.phase_vocoder.audio,
                                          n_fft=8192,
                                          hop_length=2048,
                                          win_length=8192,
                                          window='hann')

    def test_get_next_frames(self):
        # Mock the STFT to have a known value
        self.phase_vocoder.stft = np.random.random((1, 4096)) + 1j * np.random.random((1, 4096))
        
        # Get the next frames
        frames = self.phase_vocoder.get_next_frames()
        
        # Check the output shape
        self.assertIsInstance(frames, np.ndarray)
        self.assertEqual(frames.shape, (1, 2048))

    def test_get_time(self):
        # Check if get_time returns the correct timestamp
        self.assertEqual(self.phase_vocoder.get_time(), 0.0)
        
        # Simulate advancing in the audio
        self.phase_vocoder.audio_index = 44100  # 1 second worth of samples
        self.assertEqual(self.phase_vocoder.get_time(), 1.0)

    def test_set_playback_rate(self):
        # Set a new playback rate and verify
        self.phase_vocoder.set_playback_rate(1.5)
        self.assertEqual(self.phase_vocoder.playback_rate, 1.5)

if __name__ == '__main__':
    unittest.main()
