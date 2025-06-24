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

    for n in score.flatten().notes:
        for p in n.pitches:
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

