import sys
import os

# importing AudioBuffer to this script
# Add the directory to sys.path
module_path = os.path.abspath(os.path.join('..', 'src/AudioBuffer.py'))
if module_path not in sys.path:
    sys.path.append(module_path)
import AudioBuffer

import unittest

class AudioBufferTests(unittest.TestCase):
    def test_AudioBuffer_constructor():
        pass
