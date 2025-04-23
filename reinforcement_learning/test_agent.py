from gymnasium_env.envs.score_following_env import ScoreFollowingEnv
import numpy as np
from stable_baselines3 import PPO

alignment = [(i, 6 / 7 * i) for i in range(0, 64)]
alignment = np.array(alignment).T

env = ScoreFollowingEnv(midi_path="ode_beg.mid", audio_path="ode_beg.mp3", bpm=70, alignment=alignment, training=False)
model = PPO.load("ppo_score_following2", env=env)

# Reset the environment
obs, info = env.reset()
terminated = False

# Get the initial agent location
agent_location = obs["agent"][0]

total_reward = 0
i = 0
while not terminated:
    # Get the action from the model
    action, _ = model.predict(obs, deterministic=True)

    # Take a step in the environment
    obs, reward, terminated, truncated, info = env.step(action)
    agent_location, score_window, spectrogram_window = obs["agent"][0], obs["score"], obs["spectrogram"]
    env.render(mode="human")

    # Print the agent's location and reward
    print(f"Step {i}: Agent location: {agent_location}, Reward: {reward}, Dist from real: {info['distance']}, Target: {info['target']}, Action taken: {action}")
    i += 1
    total_reward += reward

print(f'Total reward: {total_reward}')
