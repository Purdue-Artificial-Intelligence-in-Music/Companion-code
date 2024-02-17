"""This will be the python file where the main logic of my task would be implemented"""
from music21 import *
import numpy as np
import math
import os
import time

"""Helper that extract all notes from a given measure, returned notes are collected in a set
    input:  measure (music21.stream.Measure)
    output: (frozenset(music21.note.Note)): a set containing all notes present in the mxml file
"""
def collect_all_notes_from_measure(measure):
    return frozenset(note for note in measure.notes)


"""Isacc's code refactored into a function. This is a helper that computes how many measures are in a given score
    (a score can be a music21.stream.Measure, music21.stream.Score, music21.stream.Part...)
    input: score (music21.stream.Score)
    output: num_measures (int)
"""
def find_num_measures_in_score(score) -> int:
    #might have to iterate through this part if there are multiple time signatures in a given score
    beats = score.getTimeSignatures(recurse=False)[0].denominator       #retrieve the time signature of object score and save only the denominator (duration of each beat)
    num_measures = int(math.ceil(score.highestTime / beats))            #find the when the last note finishes playing in object stream, divide it by duration of each beat, and take the ceiling
    return num_measures

"""This function recursively flattens a set that can contain frozensets
    input: input_set (set(frozen_set(music21.stream.Note)))
    output: final (set(music21.stream.Note))
"""
def flatten_frozenset_in_sets(input_set:set, final:set) -> set:
    for elem in input_set:
        if type(elem) is frozenset:
            flatten_frozenset_in_sets(set(elem), final)
        else:
            final.add(elem)

"""The "main" function that parses all the notes contained in the score out, stil need to figure out how (and is neccessary)
    to  remove duplicates
    input:  score (music21.stream.Score)
    output: final (set(music21.stream.Note))
"""
def collect_all_notes_from_score(score) -> set:
    all_notes = set()
    # only compute the number of measures for the first part (if this works the program might run a little faster)
    num_measures = find_num_measures_in_score(score.parts[0])
    for part in score.parts:    #I am collect all notes for every part in the score, is this neccessary?
        for i in range(1, num_measures+1, 1):
            all_notes.add(collect_all_notes_from_measure(part.measure(i)))
    return all_notes
