import numpy as np

class Piece:
    """
    Represents a single musical piece with its metadata and alignment.
    """
    def __init__(self, score_midi: str, perf_midi: str, bpm: int, alignment: np.ndarray):
        self.score_midi = score_midi
        self.perf_midi = perf_midi
        self.bpm = bpm
        self.alignment = alignment

