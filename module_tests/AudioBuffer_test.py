import sys
import os

# importing AudioBuffer to this script
try:
    from src.AudioBuffer import AudioBuffer
except:
    print("something went wrong with importing")
    exit(1)

import numpy as np
import pyaudio
import unittest
import unittest.mock as mock
from unittest.mock import patch

class AudioBufferTests(unittest.TestCase):
    # use patch to mock PyAudio class for the entire test suite
    @patch('pyaudio.PyAudio')
    def setUp(self, mock_pyaudio):
        """ Set up test cases: so audio_buffer is a class attribute 
            accessible to other class methods
        """
        # mock PyAudio class used in AudioBuffer
        self.sample_rate = 16000
        self.channels = 2
        self.frames_per_buffer = 1024
        self.max_duration = 600

        # mock this function and give it a dummy return value
        mock_pyaudio.return_value.get_device_info_by_index.return_value = {
            'name': 'Test Device', 
            'maxInputChannels': 2, 
            'defaultSampleRate': 16000
        }

        self.audio_buffer = AudioBuffer(sample_rate=self.sample_rate,
                                        channels=self.channels,
                                        frames_per_buffer=self.frames_per_buffer,
                                        max_duration=self.max_duration)
    def test_pyAudio_mock(self):
        """ Test that the PyAudio class is being mocked correctly """
        self.assertTrue(isinstance(self.audio_buffer.p, mock.MagicMock))
        self.assertTrue(isinstance(self.audio_buffer.p.get_device_info_by_index(), dict))

    def test_AudioBuffer_constructor(self):
        # Test the initialization of the AudioBuffer
        self.assertEqual(self.audio_buffer.sample_rate, self.sample_rate)
        self.assertEqual(self.audio_buffer.channels, self.channels)
        self.assertEqual(self.audio_buffer.frames_per_buffer, self.frames_per_buffer)
        self.assertEqual(self.audio_buffer.length, self.max_duration * self.sample_rate)
        self.assertEqual(self.audio_buffer.write_index, 0)
        self.assertEqual(self.audio_buffer.read_index, 0)
        self.assertEqual(self.audio_buffer.count, 0)
        self.assertIsInstance(self.audio_buffer.buffer, np.ndarray)

    def test_write_to_buffer(self):
        # Test writing frames to the buffer
        frames = np.random.rand(self.channels, 100).astype(np.float32)
        self.audio_buffer.write(frames)
        self.assertEqual(self.audio_buffer.write_index, 100)
        self.assertEqual(self.audio_buffer.count, 100)
        np.testing.assert_array_equal(self.audio_buffer.buffer[:, :100], frames)

    def test_write_to_buffer_overflow(self):
        # test writing more frames than alloted
        frames = np.random.rand(self.channels, self.audio_buffer.length + 1).astype(np.float32)
        with self.assertRaises(Exception) as context:   #ensure Exception is raised at overflow
                self.audio_buffer.write(frames)
                self.assertTrue('Not enough space left in buffer' in str(context.exception))

    def test_read_from_buffer(self):
        # Test reading frames from the buffer
        frames = np.random.rand(self.channels, 100).astype(np.float32)
        self.audio_buffer.write(frames)
        read_frames = self.audio_buffer.read(50)
        self.assertEqual(self.audio_buffer.read_index, 50)
        self.assertEqual(self.audio_buffer.count, 50)
        np.testing.assert_array_equal(read_frames, frames[:, :50])
    
    def test_read_from_buffer_overflow(self):
        # Test reading more frames than alloted
        frames = np.random.rand(self.channels, 100).astype(np.float32)
        self.audio_buffer.write(frames)
        with self.assertRaises(Exception) as context:
            self.audio_buffer.read(101)
            self.assertTrue('Not enough frames in buffer' in str(context.exception))


    
