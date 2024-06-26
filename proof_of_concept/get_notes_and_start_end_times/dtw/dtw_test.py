import unittest
import music21 as music
from dtw import *


class DTW_XML_To_MIDI_Tests(unittest.TestCase):
    def test_convert_music21_obj(self):
        score_name = r"../bourree.xml"
        bourreeMIDI = xml2MIDI(score_name)
        self.assertTrue(isinstance(bourreeMIDI, music.midi.MidiFile))

