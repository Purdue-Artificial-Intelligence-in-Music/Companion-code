import unittest
import numpy as np
from unittest.mock import patch, MagicMock
from audio_buffer import AudioBuffer

class TestAudioBuffer(unittest.TestCase):
    def setUp(self):
        # Instantiate AudioBuffer with default parameters
        self.buffer = AudioBuffer(sample_rate=44100, channels=1, max_duration=10)

    def test_initialization(self):
        # Check that the buffer has been initialized correctly
        self.assertEqual(self.buffer.sample_rate, 44100)
        self.assertEqual(self.buffer.length, 44100 * 10)
        self.assertEqual(self.buffer.buffer.shape, (1, 44100 * 10))
        self.assertEqual(self.buffer.write_index, 0)
        self.assertEqual(self.buffer.read_index, 0)
        self.assertEqual(self.buffer.unread_frames, 0)

    def test_write_to_buffer(self):
        # Create some sample frames to write
        frames = np.random.random((1, 2048)).astype(np.float32)

        # Write frames to the buffer
        self.buffer.write(frames)

        # Verify that the frames were written correctly
        np.testing.assert_array_equal(self.buffer.buffer[:, :2048], frames)
        self.assertEqual(self.buffer.write_index, 2048)
        self.assertEqual(self.buffer.unread_frames, 2048)

    def test_write_to_buffer_exceeding_length(self):
        # Create frames that exceed the buffer's length
        frames = np.random.random((1, self.buffer.length + 1)).astype(np.float32)

        # Verify that writing frames beyond the buffer length raises an exception
        with self.assertRaises(Exception) as context:
            self.buffer.write(frames)
        self.assertTrue('Not enough space left in buffer' in str(context.exception))

    def test_read_from_buffer(self):
        # Write some frames to the buffer
        frames = np.random.random((1, 2048)).astype(np.float32)
        self.buffer.write(frames)

        # Read frames from the buffer
        read_frames = self.buffer.read(2048)

        # Verify that the frames were read correctly
        np.testing.assert_array_equal(read_frames, frames)
        self.assertEqual(self.buffer.read_index, 2048)
        self.assertEqual(self.buffer.unread_frames, 0)

    def test_read_from_buffer_exceeding_unread_frames(self):
        # Attempt to read more frames than are available
        with self.assertRaises(Exception) as context:
            self.buffer.read(2048)
        self.assertTrue('Attempted to read 2048 frames but count is 0' in str(context.exception))

    def test_get_time(self):
        # Write some frames to the buffer
        frames = np.random.random((1, 44100)).astype(np.float32)  # 1 second worth of frames
        self.buffer.write(frames)

        # Verify that get_time returns the correct duration
        self.assertEqual(self.buffer.get_time(), 1.0)

    @patch('soundfile.write')
    def test_save_audio(self, mock_write):
        # Write some frames to the buffer
        frames = np.random.random((1, 2048)).astype(np.float32)
        self.buffer.write(frames)

        # Save the buffer to a file
        self.buffer.save('dummy_path.wav')

        # Verify that soundfile.write was called with the correct parameters
        mock_write.assert_called_once()

if __name__ == '__main__':
    unittest.main()