import get_notes_and_start_end_times as parse
from music21 import *

if __name__ == '__main__':
    print(f'executing {__file__}')
    score = converter.parse("/home/shay/a/ko109/Companion-code/get_notes_and_start_end_times/Abide by Me.midi")

    print('the piece contains the following parts')
    for i,part in enumerate(score.parts,start=1):
        print(f'\t{i}: ',end='')
        print(part)

    print(f"the piece is in the key of {score.analyze('key')}")
    n_measures = parse.find_num_measures_in_score(score=score)
    print(f'the piece has {n_measures} measures')

    """this part looks a little off, but may be resolved by fixing the function 
    collect_all_notes_from_score:
        just find number of measures for only a part, as other parts should play in harmony"""
    all_notes_set = parse.collect_all_notes_from_score(score)

    print(f"there are {len(all_notes_set)} measures in the piece, which contains notes: ")
    for i,s in enumerate(all_notes_set, start=1):
        print(f'measure {i}: ')
        for n in s:
            print(f'\t{n}')

    flatten_notes_set = set()
    parse.flatten_frozenset_in_sets(all_notes_set, flatten_notes_set)
    print(f'there are {len(flatten_notes_set)} notes involved with the piece, namely: ')
    for i,note in enumerate(flatten_notes_set, start=1):
        print(f"\tnote #{i}: {note}")

    n1 = list(flatten_notes_set)[4]
    n2 =list(flatten_notes_set)[8]
    #viewing their full names: try to see difference between these objects
    print(n1.fullName)
    print(n2.fullName)
    print(n1.pitches)
    print(n2.pitches)
    print(n1 is n2)
    print(f'end of executing {__file__}')