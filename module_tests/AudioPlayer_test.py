import unittest
import numpy as np
from unittest.mock import patch, MagicMock

try:
  from src.AudioPlayer import AudioPlayer, normalize_audio  # Assuming the class is in a module named `audioplayer`
except:
  print("something went wrong with importing")
  exit(1)
  
class TestAudioPlayer(unittest.TestCase):
    
    @patch('librosa.load')
    @patch('pyaudio.PyAudio')
    def setUp(self, mock_pyaudio, mock_librosa_load):
        # Mock the librosa load function to return dummy data
        audio_data = np.random.randn(16000)  # 1 second of dummy audio data at 16kHz
        mock_librosa_load.return_value = (audio_data, 16000)
        
        # Mock pyaudio
        mock_pyaudio_instance = MagicMock()
        mock_pyaudio.return_value = mock_pyaudio_instance
        
        # Instantiate the AudioPlayer with test parameters
        self.player = AudioPlayer(path="test_audio.wav", sample_rate=16000, channels=1)
    
    def test_audio_normalization(self):
        """Test if the audio is normalized to the range [-1, 1]."""
        max_value = np.max(np.abs(self.player.audio))
        self.assertEqual(max_value, 1.0)
    
    @patch('pyaudio.Stream')
    def test_audio_playback(self, mock_stream):
        """Test starting and stopping audio playback."""
        self.player.start()
        
        # Ensure that the PyAudio stream has been opened
        self.player.p.open.assert_called_once_with(
            format=pyaudio.paFloat32,
            channels=1,
            rate=16000,
            input=False,
            output=True,
            stream_callback=self.player.callback,
            frames_per_buffer=1024
        )
        
        # Test if the stream is active
        mock_stream.is_active.return_value = True
        self.assertTrue(self.player.is_active())
        
        # Test stopping the player
        self.player.stop()
        mock_stream.close.assert_called_once()
        self.player.p.terminate.assert_called_once()
    
    def test_pause_unpause(self):
        """Test pausing and unpausing the audio playback."""
        # Initially not paused
        self.assertFalse(self.player.paused)
        
        # Pause the audio
        self.player.pause()
        self.assertTrue(self.player.paused)
        
        # Unpause the audio
        self.player.unpause()
        self.assertFalse(self.player.paused)
    
    def test_get_next_frames(self):
        """Test the time-stretching logic in get_next_frames."""
        # Simulate playback
        frames = self.player.get_next_frames()
        self.assertEqual(frames.shape, (1, 1024))  # One channel, frames_per_buffer = 1024
    
    def test_playback_rate_changes(self):
        """Test the behavior when changing playback rate."""
        initial_rate = self.player.playback_rate
        self.assertEqual(initial_rate, 1.0)  # Default playback rate
        
        # Change playback rate and check
        self.player.playback_rate = 1.5
        self.assertEqual(self.player.playback_rate, 1.5)

    def test_callback_audio_segment(self):
        """Test the callback function behavior when audio is playing and paused."""
        in_data = None
        frame_count = 1024
        time_info = {}
        status = None

        # Test callback when not paused
        self.player.paused = False
        output, flag = self.player.callback(in_data, frame_count, time_info, status)
        self.assertEqual(output.shape, (1, 1024))  # Ensure output has correct shape
        self.assertEqual(flag, pyaudio.paContinue)

        # Test callback when paused
        self.player.paused = True
        output, flag = self.player.callback(in_data, frame_count, time_info, status)
        self.assertTrue(np.array_equal(output, np.zeros((1, 1024))))  # Should return silence
        self.assertEqual(flag, pyaudio.paContinue)
    
    def test_get_time(self):
        """Test the get_time function returns correct timestamp."""
        self.player.index = 16000  # Fake playing 1 second of audio
        current_time = self.player.get_time()
        self.assertEqual(current_time, 1.0)

if __name__ == '__main__':
    unittest.main()
