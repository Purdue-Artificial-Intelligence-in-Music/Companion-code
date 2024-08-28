"""This file contains modules that performs DTW to align musicXML and music recording"""
import music21 as music
import librosa
from AudioBuffer import *


def xml2MIDI(filename: str) -> music.midi.MidiFile:
    """this function returns a MidiFile object from given filename"""
    xml_score = music.converter.parse(filename)
    return music.midi.translate.streamToMidiFile(xml_score)

