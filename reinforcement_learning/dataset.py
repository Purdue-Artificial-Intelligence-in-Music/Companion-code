import os
import random
import json
from typing import List
import numpy as np

from .piece import Piece

class Dataset:
    """
    Loads all Pieces from a directory. Expects for each piece:
      - <name>.mid
      - <name>.mp3 (or .wav)
      - <name>_alignment.npy
      - <name>.json containing at least {"bpm": <int>}
    """
    def __init__(self, data_dir: str):
        self.pieces: List[Piece] = []
        for dir_name in os.listdir(data_dir):
            base: str = os.path.splittext(dir_name)[0]
            piece_name = base.replace('_vn_vn', '')
            score_path = os.path.join(data_dir, base, piece_name, "baseline.mid")
            ref_path = os.path.join(data_dir, f"{base}.mp3")
            alignment_path = os.path.join(data_dir, f"{base}_alignment.npy")
            meta_path = os.path.join(data_dir, f"{base}.json")

            # skip if any required file is missing
            if not all(os.path.exists(p) for p in [audio_path, alignment_path, meta_path]):
                continue

            # load alignment and metadata
            alignment = np.load(alignment_path)
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            bpm = meta['bpm']

            # create and store the piece
            piece = Piece(midi_path, audio_path, bpm, alignment)
            self.pieces.append(piece)

    def __len__(self):
        return len(self.pieces)

    def __getitem__(self, idx: int) -> Piece:
        return self.pieces[idx]

    def sample(self) -> Piece:
        """Return a random Piece from the dataset."""
        return random.choice(self.pieces)