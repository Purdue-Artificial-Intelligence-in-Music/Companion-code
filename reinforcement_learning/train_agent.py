import numpy as np
from stable_baselines3 import PPO
from gymnasium_env.envs.score_following_env import ScoreFollowingEnv
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from tqdm import tqdm


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
        "training": True
    },
)

vec_env = VecNormalize(vec_env, norm_obs=True, norm_reward=False, gamma=0.99)

# Create the PPO model using MultiInputPolicy to handle the Dict observation space.
model = PPO("MultiInputPolicy", vec_env, verbose=1)

# Train the model for a specified number of timesteps.
model.learn(total_timesteps=100_000, progress_bar=tqdm)

# Save the trained model.
model.save("ppo_score_following4")
vec_env.save("ppo_score_following_env4")
vec_env.close()
