from parse_audio import *
from parse_score import *
from music21 import *
import numpy as np
import librosa

if __name__ == '__main__':
    print(f'executing {__file__}')

    # Load audio as numpy array
    audio, sr = librosa.load('Abide by Me.wav')

    #parse score
    score = converter.parse('Abide by Me.midi')
    all_notes_set = collect_all_notes_from_score(score)
    flatten_notes_set = set()
    flatten_frozenset_in_sets(all_notes_set, flatten_notes_set) #has all note names
    freq_list : list[float] = translate_note_to_freq(flatten_frozenset_in_sets)

    # parse audio
    set_sampling_rate(sr=sr)
    freq_to_time : dict[float:tuple[float, float]] = get_start_end_time_of_notes(freq_keys=freq_list,audio=audio)

    # log parsed result onto a separate file