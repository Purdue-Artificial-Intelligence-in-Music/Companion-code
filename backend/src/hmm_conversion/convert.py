from music21 import converter
from music21.meter.base import TimeSignature
from os import path
from pathlib import Path

from music21 import stream
from fractions import Fraction


def convert(filepath: Path):
    name = path.basename(filepath)
    score = converter.parse(filepath)

    bar = []
    solo = []

    ts = TimeSignature()  # 4/4 by default
    for m in score.recurse().getElementsByClass(stream.Measure):
        if m.timeSignature is not None:  # otherwise time signature continues
            ts = m.timeSignature
        bar.append(str(m.number) + "\t" + ts.ratioString)

    # DEALING WITH RESTS
    index = 0
    sI = score.flatten().notesAndRests
    length = len(sI)
    for n in sI:
        for p in n.pitches:
            if index >= length-1:
                break
            buffer = index
            # change all the rests to be absorbed into the previous note
            while sI[buffer+1].isRest:
                n.duration.quarterLength = n.duration.quarterLength + sI[buffer+1].duration.quarterLength
                buffer = buffer + 1
                if buffer==length-1: 
                    break
        index = index + 1

    for n in score.flatten().notes:
        for p in n.pitches:
            # if tie type = stop (end of tie) --> skip onset
            if n.tie is None or n.tie.type != 'stop':
                solo.append(
                    "{:<15}\t{}\t{}\t{}\t{}".format(
                        "{}+{}/{}".format(
                            n.measureNumber,
                            *((n.beat - 1.0) / n.beatDuration.quarterLength).as_integer_ratio(),
                        ),
                        "{}/{}".format(*(n.offset / 4.0).as_integer_ratio()),
                        n.volume.velocity if n.volume.velocity is not None else 90,
                        p.midi,
                        1,  # note on
                    )
                )
            # if tie type = start (start of tie) --> skip offset
            if n.tie is None or n.tie.type != 'start':
                solo.append(
                    "{:<15}\t{}\t{}\t{}\t{}".format(
                        "{}+{}/{}".format(
                            n.measureNumber,
                            *(
                                ((n.beat - 1.0) / n.beatDuration.quarterLength)
                                + n.quarterLength / 4.0
                            ).as_integer_ratio(),
                        ),
                        "{}/{}".format(
                            *((n.offset + n.quarterLength) / 4.0).as_integer_ratio()
                        ),
                        n.volume.velocity if n.volume.velocity is not None else 90,
                        p.midi,
                        0,  # note off
                    )
                )

    bar_path = Path(name).with_suffix(".bar")
    solo_path = Path(name).with_suffix(".solo")

    with open(bar_path, "w") as bar_file, open(solo_path, "w") as solo_file:
        bar_file.writelines(f"{line}\n" for line in bar)
        solo_file.writelines(f"{line}\n" for line in solo)


# TODO
# - chords

import sys

if __name__ == '__main__':
    for filename in sys.argv[1:]:
        s = converter.parse(filename)
        s.show()
        convert(Path(filename))

