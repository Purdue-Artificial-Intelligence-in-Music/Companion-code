import torch
import torch.nn as nn
import torch.nn.functional as F
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

import numpy as np
from stable_baselines3 import PPO
from gymnasium_env.envs.score_following_env import ScoreFollowingEnv
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize 
from tqdm import tqdm
MODEL_SAVE_NAME = "ppo_score_following2"
TENSORBOARD_LOG_DIR = "./tensorboard_logs/"
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
print("Normalizing environment observations...")
vec_env = VecNormalize(vec_env, norm_obs=True, norm_reward=False)
print("Normalization wrapper applied.")
model = PPO(
    "MultiInputPolicy",
    vec_env,
    verbose=1,
    tensorboard_log=TENSORBOARD_LOG_DIR
    # ent_coef=ENT_COEF
)
# Train the model for a specified number of timesteps.
model.learn(total_timesteps=1_000_000, log_interval=10, progress_bar=tqdm)
# Save the trained model and VecNormalize obejct
model.save(MODEL_SAVE_NAME)
vec_env.save(f"{MODEL_SAVE_NAME}_stats.pkl")
vec_env.close()


