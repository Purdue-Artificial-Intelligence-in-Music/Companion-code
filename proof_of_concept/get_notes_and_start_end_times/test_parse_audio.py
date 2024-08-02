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
    freq_list : list[float] = translate_note_to_freq(flatten_notes_set)

    # parse audio
    set_sampling_rate(sr=sr)
    print(len(audio))
    print(audio[:10])
    freq_to_time : dict[float:tuple[float, float]] = get_start_end_time_of_notes(freq_keys=freq_list,audio=audio)

    # log parsed result onto a separate file
    with open('audio_parse.log', 'w') as writer:
        writer.write('Note Name \t start-time \t end-time\n')
        for name, freq in zip(flatten_notes_set, freq_to_time.keys()):
            out_str = name + ' \t' + str(freq_to_time[freq][0]) + ' \t' + \
            str(freq_to_time[freq_to_time[freq]]) + '\n'
            writer.write(out_str)