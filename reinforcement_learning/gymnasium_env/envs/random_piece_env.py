import gymnasium as gym
import random
import numpy as np
import pandas as pd
from pathlib import Path
from .score_following_env import ScoreFollowingEnv
import json

class RandomPieceEnv(gym.Env):
    def __init__(self, data_root: str):
        super().__init__()
        self.data_root = Path(data_root)
        # collect all the piece directories
        self.piece_dirs = [d for d in self.data_root.iterdir() if d.is_dir()]

        # to satisfy Gym API, create a dummy inner env so
        # action_space & observation_space exist immediately:
        self.current_env = self._make_env(self.piece_dirs[0])

        self.action_space = self.current_env.action_space
        self.observation_space = self.current_env.observation_space

    def _make_env(self, piece_dir: Path) -> ScoreFollowingEnv:
        # load piano roll
        piano_roll = np.load(piece_dir / "piano_roll.npy")

        # pick one of the spectrograms at random
        specs = list(piece_dir.glob("spec_*.npy"))
        random_spec = random.choice(specs)
        spectrogram = np.load(random_spec)
        name = random_spec.stem.replace("spec_", "").replace(".npy", "")

        # load timing CSV → build alignment array [2×N]
        df = pd.read_csv(piece_dir / "solo_note_timings.csv")
        baseline   = df["baseline_beat"].to_numpy()
        altered  = df[f"{name}_beat"].to_numpy()
        alignment = np.vstack((baseline, altered))

        # load BPM from a metadata file, or hard-code if you like
        # with open(piece_dir / "meta.json") as f:
        #     bpm = json.load(f)["bpm"]

        return ScoreFollowingEnv(
            piano_roll=piano_roll,
            spectrogram=spectrogram,
            alignment=alignment,
            bpm=120,  # hard-coded for now
        )

    def reset(self, **kwargs):
        # sample a new piece after every episode
        piece_dir     = random.choice(self.piece_dirs)
        self.current_env = self._make_env(piece_dir)
        return self.current_env.reset(**kwargs)

    def step(self, action):
        return self.current_env.step(action)

    def render(self, *args, **kwargs):
        return self.current_env.render(*args, **kwargs)
