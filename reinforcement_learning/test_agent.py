import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import VecNormalize
from gymnasium_env.envs.score_following_env import ScoreFollowingEnv
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv
# Same alignment setup as training
beats = np.arange(0, 64)
note_onsets = 6 / 7 * beats
alignment = (beats, note_onsets)

env_kwargs={
     "midi_path": "ode_beg.mid",
     "audio_path": "ode_beg.mp3",
     "bpm": 70,
     "alignment": alignment,
 }
env_fn = lambda: ScoreFollowingEnv(**env_kwargs)

dummy_vec_env = DummyVecEnv([env_fn])
env = VecNormalize.load("ppo_score_following2_stats.pkl", dummy_vec_env)
env.training = False
# Load the trained PPO model 
model = PPO.load("ppo_score_following2", env=env) 

obs = env.reset() # obs might be dict wrapping numpy array ex) obs['agent'][0]
done = False
i = 0

print("Starting test loop...")
total_reward = 0
i = 0
while not done:
    # Get the action from the model
    action, _ = model.predict(obs, deterministic=True)

    obs, reward, dones, info = env.step(action)
    done = dones[0]
    env.render(mode="human")

    raw_agent_loc = env.get_attr('_agent_location')[0]
    raw_target_loc = env.get_attr('_target_location')[0]
    current_reward = reward[0] # Extract reward for the single env

    # Print the agent's location and reward
    print(f"Step {i}: Action: {action[0]}, "
            f"Agent(raw): {raw_agent_loc:.2f}, Target(raw): {raw_target_loc:.2f}, "
            f"Reward: {current_reward:.3f}, Done: {done}")
    i += 1
    total_reward += reward[0]
print(f"Episode finished at step {i}.")
env.close()
print(f'Total reward: {total_reward}')