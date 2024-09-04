import sys
import os

# importing AudioBuffer to this script
directory = r'C:\Users\Nick\github\Nick-Ko-Companion-code\src\AudioBuffer.py'
assert os.path.exists(directory), f"{directory} does not exists"
sys.path.append(directory)

from AudioBuffer import AudioBuffer
import numpy as np
import unittest

class AudioBufferTests(unittest.TestCase):
    def setUp(self):
        """ Set up test cases: so AudioBuffer is a class attribute 
            accessible to other class methods
        """
        self.sample_rate = 16000
        self.channels = 2
        self.frames_per_buffer = 1024
        self.max_duration = 600
        self.audio_buffer = AudioBuffer(
            sample_rate=self.sample_rate,
            channels=self.channels,
            frames_per_buffer=self.frames_per_buffer,
            max_duration=self.max_duration)

    def test_AudioBuffer_constructor(self):
        """Test the initialization of the AudioBuffer."""
        self.assertEqual(self.audio_buffer.sample_rate, self.sample_rate)
        self.assertEqual(self.audio_buffer.channels, self.channels)
        self.assertEqual(self.audio_buffer.frames_per_buffer, self.frames_per_buffer)
        self.assertEqual(self.audio_buffer.length, self.max_duration * self.sample_rate)
        self.assertEqual(self.audio_buffer.write_index, 0)
        self.assertEqual(self.audio_buffer.read_index, 0)
        self.assertEqual(self.audio_buffer.count, 0)
        self.assertIsInstance(self.audio_buffer.buffer, np.ndarray)

    def test_write_to_buffer(self):
        """Test writing frames to the buffer."""
        frames = np.random.rand(self.channels, 100).astype(np.float32)
        self.audio_buffer.write(frames)
        self.assertEqual(self.audio_buffer.write_index, 100)
        self.assertEqual(self.audio_buffer.count, 100)
        np.testing.assert_array_equal(self.audio_buffer.buffer[:, :100], frames)
    
