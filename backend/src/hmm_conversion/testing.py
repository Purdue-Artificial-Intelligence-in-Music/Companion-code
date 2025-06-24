import sys

from music21 import converter

from convert import convert

from pathlib import Path

for filename in sys.argv[1:]:
    # s = converter.parse(filename)
    # s.show()
    convert(Path(filename))
