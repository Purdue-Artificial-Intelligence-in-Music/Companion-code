import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from gymnasium_env.envs.score_following_env import ScoreFollowingEnv
from stable_baselines3.common.env_util import make_vec_env
from tqdm import tqdm
import matplotlib.pyplot as plt

# Create some dummy alignment data.
# Your alignment is expected to be a tuple: (beats, note_onsets)
# For example, let's assume the beats are 0 to 100, and note onsets are evenly spaced in seconds.

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
# model = PPO("MultiInputPolicy", env, verbose=1)
# model = PPO("MultiInputPolicy", vec_env, verbose=1)

# Train the model for a specified number of timesteps.
# model.learn(total_timesteps=1_000_000, progress_bar=tqdm)
# mean_reward, std_reward = evaluate_policy(model, vec_env, n_eval_episodes=100, warn=False)
# print(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")

# Save the trained model.
# model.save("ppo_score_following")

model = PPO.load("ppo_score_following")
obs = vec_env.reset()
done = [False]

env = vec_env.envs[0]
errors = []
# play one episode
while not done[0]:
    action, _states = model.predict(obs)
    obs, reward, done, info = vec_env.step(action)
    # vec_env.render(mode="human")
    errors.append(info[0]["distance"])



vec_env.close()

# Plot the rewards.
plt.hist(errors)
plt.title("Error Distribution")
plt.show()