import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from gymnasium_env.envs.score_following_env import ScoreFollowingEnv
from stable_baselines3.common.env_util import make_vec_env
from tqdm import tqdm
import matplotlib.pyplot as plt


beats = np.arange(0, 64)
note_onsets = 6 / 7 * beats
alignment = (beats, note_onsets)

vec_env = make_vec_env(
    ScoreFollowingEnv,
    n_envs=4,
    env_kwargs={
        "midi_path": "ode_beg.mid",
        "audio_path": "ode_beg.mp3",
        "bpm": 70,
        "alignment": alignment,
    },
)

# Create the PPO model using MultiInputPolicy to handle the Dict observation space.
model = PPO("MultiInputPolicy", vec_env, verbose=1)

# Train the model for a specified number of timesteps.
model.learn(total_timesteps=1_000_000, progress_bar=tqdm)

# Save the trained model.
model.save("ppo_score_following")
