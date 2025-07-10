from music21 import converter
from music21.meter.base import TimeSignature
from os import path
from pathlib import Path

from music21 import stream
from fractions import Fraction

# Important Note: Need to fix 1st column of .solo file and see Google Doc about Dr. Raphael's library for more details)

def get_quarterLength(graceNote):
    if graceNote.duration.getGraceDuration().quarterLength != 0.0:
        return graceNote.duration.getGraceDuration().quarterLength

    duration_map = {
        "whole": Fraction(1, 1),
        "half": Fraction(1, 2),
        "quarter": Fraction(1, 4),
        "eighth": Fraction(1, 8),
        "16th": Fraction(1, 16),
        "32nd": Fraction(1, 32),
        "64th": Fraction(1, 64)
    }
    
    graceType = graceNote.duration.getGraceDuration().type
    return duration_map[graceType]

def sum_duration(grace_notes):
    duration = 0.0
    for note in grace_notes:
        duration += get_quarterLength(note)
    return duration


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

    i = 0
    notes = list(score.flatten().notes)
    while i < len(notes):
        n = notes[i]
        if n.duration.isGrace:
            grace_notes = []
            while i < len(notes) and notes[i].duration.isGrace:
                grace_notes.append(notes[i])
                i += 1
            if i < len(notes):
                main_offset = notes[i].offset
                i -= 1
            else:
                main_offset = grace_notes[-1].offset

            #total_grace_duration = sum_duration(grace_notes)
            total_grace_duration = sum_duration(grace_notes) * 2.0 
            # NOTE: Multiply duration sum by 2.0 for measures 5, 9, 39 of vieuxtemps
            # NOTE: Multiply duration sum by 1.0 for measures 31, 42 of vieuxtemps
            # Could be grace note duration / predecing note duration or something similar?
            grace_offset = main_offset - total_grace_duration

            # adjusting offset of note before grace note
            measure, offset, velocity, pitch, marker = solo[-1].split('\t')
            offset = grace_offset
            solo[-1] = "{:<15}\t{}\t{}\t{}\t{}".format(
                                measure,
                                "{}/{}".format(*(offset / 4.0).as_integer_ratio()),
                                velocity,
                                pitch,
                                marker,
                            )

            for grace in grace_notes:
                duration = get_quarterLength(grace) * 2.0
                # NOTE: Multiply duration by 2.0 for measures 5, 9, 39 of vieuxtemps
                # NOTE: Multiply duration by 1.0 for measures 31, 42 of vieuxtemps
                # Could be grace note duration / predecing note duration or something similar?
                for p in grace.pitches:
                    # if tie type = stop (end of tie) --> skip onset
                    if n.tie is None or n.tie.type != 'stop':
                        # TODO: Fix measure number+beat formatting for both onset and offset
                        solo.append(
                            "{:<15}\t{}\t{}\t{}\t{}".format(
                                "{}+{}/{}".format(
                                    grace.measureNumber,
                                    *((n.beat - 1.0) / n.beatDuration.quarterLength).as_integer_ratio(),
                                ),
                                "{}/{}".format(*(grace_offset / 4.0).as_integer_ratio()),
                                grace.volume.velocity if grace.volume.velocity is not None else 90,
                                p.midi,
                                1,  # note on
                            )
                        )
                        if grace.measureNumber == 5: # just trying to print certain measure to check, don't need
                            # print("grace note onset")
                            print("grace onset: {}/{}".format(*(grace_offset / 4.0).as_integer_ratio()))

                    # if tie type = start (start of tie) --> skip offset
                    if n.tie is None or n.tie.type != 'start':
                        solo.append(
                            "{:<15}\t{}\t{}\t{}\t{}".format(
                                "{}+{}/{}".format(
                                    grace.measureNumber,
                                    *(
                                        ((n.beat - 1.0) / n.beatDuration.quarterLength)
                                        + n.quarterLength / 4.0
                                    ).as_integer_ratio(),
                                ),
                                "{}/{}".format(
                                    *((grace_offset + duration) / 4.0).as_integer_ratio()
                                ),
                                n.volume.velocity if n.volume.velocity is not None else 90,
                                p.midi,
                                0,  # note off
                            )
                        )
                        if grace.measureNumber == 5: # just trying to print certain measure to check, don't need
                            print("grace offset: {}/{}".format(*((grace_offset + duration) / 4.0).as_integer_ratio()))
                grace_offset += duration

        else:
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
                    if n.measureNumber == 5: # just trying to print certain measure to check, don't need
                        print("note onset: {}/{}".format(*(n.offset / 4.0).as_integer_ratio()))

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
                    if n.measureNumber == 5: # just trying to print certain measure to check, don't need
                        print("note offset: {}/{}".format(*((n.offset + n.quarterLength) / 4.0).as_integer_ratio()))
        i += 1
    
    bar_path = Path(name).with_suffix(".bar")
    solo_path = Path(name).with_suffix(".solo")

    with open(bar_path, "w") as bar_file, open(solo_path, "w") as solo_file:
        bar_file.writelines(f"{line}\n" for line in bar)
        solo_file.writelines(f"{line}\n" for line in solo)
    


# TODO
# - chords

import sys

if __name__ == '__main__':
    filename = "vieuxtemps_viola_sonata_op36_mvmt2.xml"
    convert(Path(filename))
    # for filename in sys.argv[1:]:
        # print(filename)
        # s = converter.parse(filename)
        # s.show()
        # convert(Path(filename))

