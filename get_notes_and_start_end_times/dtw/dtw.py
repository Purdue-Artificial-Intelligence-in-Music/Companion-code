"""This file contains modules that performs DTW to align musicXML and music recording"""
import music21 as music
import librosa

def xml2MIDI(filename: str) -> music.midi.MidiFile:
    xml_score = music.converter.parse(filename)
    return music.midi.streamToMidiFile(xml_score)