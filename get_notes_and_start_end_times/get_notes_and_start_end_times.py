"""This will be the python file where the main logic of my task would be implemented"""
from music21 import *
import numpy as np
import math
import os
import time

"""
    input:  measure (music21.stream.Measure)
    output: (set(music21.note.Note)): a set containing all notes present in the mxml file
"""
def collect_all_notes_from_measure(measure):
    return frozenset(note for note in measure.notes)


"""Isacc's code refactored into a function. This is a helper for the main function collect_all_notes_from_score
    input: score (music21.stream.Score)
    output: num_measures (int)
"""
def find_num_measures_in_score(score) -> int:
    #might have to iterate through this part if there are multiple time signatures in a given score
    # beats = [timeSig.denominator for timeSig in score.getTimeSignatures(recurse=False)]   #the multiple time sig version
    beats = score.getTimeSignatures(recurse=False)[0].denominator       
    num_measures = int(math.ceil(score.highestTime / beats))
    return num_measures

"""This is a helper for the main function collect_all_notes_from_score: recursively flatten a set that can contain frozensets
    input: input_set (set)
    output: final (set)
"""
def flatten_frozenset_in_sets(input_set:set, final:set) -> set:
    for elem in input_set:
        if type(elem) == frozenset:
            flatten_frozenset_in_sets(set(elem), final)
        else:
            final.add(elem)

def collect_all_notes_from_score(score):
    all_notes = set()
    for part in score.parts:
        num_measures = find_num_measures_in_score(part)
        for i in range(1, num_measures+1, 1):
            all_notes.add(collect_all_notes_from_measure(part.measure(i)))
    final = set()
    flatten_frozenset_in_sets(all_notes, final)
    return final