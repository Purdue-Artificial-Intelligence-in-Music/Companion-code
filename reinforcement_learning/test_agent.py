from gymnasium_env.envs.score_following_env import ScoreFollowingEnv
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env  
from stable_baselines3.common.vec_env import VecNormalize

alignment = [(i, 6 / 7 * i) for i in range(0, 64)]
alignment = np.array(alignment).T

env_kwargs={
     "midi_path": "ode_beg.mid",
     "audio_path": "ode_beg.mp3",
     "bpm": 70,
     "alignment": alignment,
 }
vec_env = make_vec_env(lambda: ScoreFollowingEnv(**env_kwargs), n_envs=1)
env = VecNormalize.load("ppo_score_following_env2", vec_env)
# env = ScoreFollowingEnv(midi_path="ode_beg.mid", audio_path="ode_beg.mp3", bpm=70, alignment=alignment, training=False)

model = PPO.load("ppo_score_following2", env=env)

# Reset the environment
obs = env.reset()
terminated = False

# Get the initial agent location
agent_location = obs["agent"][0]

total_reward = 0
i = 0
while not terminated:
    # Get the action from the model
    action, _ = model.predict(obs, deterministic=True)

    # Take a step in the environment
    obs, reward, terminated, truncated = env.step(action)
    agent_location, score_window, spectrogram_window = obs["agent"][0], obs["score"], obs["spectrogram"]
    env.render(mode="human")

    # Print the agent's location and reward
    current_agent_loc = obs["agent"][0][0] # Adjust indexing based on actual obs structure
    current_reward = reward[0]
    target_loc = env.get_attr('_target_location')[0]
    agent_loc= env.get_attr('_agent_location')[0]
    print(f"Step {i}: Action: {action[0]}, Agent loc: {agent_loc:.2f}, target loc: {target_loc:.2f}, Reward: {current_reward:.3f}")  
    i += 1
    total_reward += reward

print(f'Total reward: {total_reward}')
