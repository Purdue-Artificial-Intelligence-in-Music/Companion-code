import gymnasium as gym
import numpy as np
import librosa
import matplotlib.pyplot as plt
import pretty_midi
import os
import imageio
import pygame
import matplotlib.pyplot as plt

def calculate_piano_roll_fps(columns_per_beat: int, BPM: float) -> float:
    """
    Calculate frames per second (fps) for a piano roll given a resolution in columns per beat
    and a tempo in beats per minute (BPM).

    Parameters:
        columns_per_beat (int): The number of columns per beat.
        BPM (float): Tempo in beats per minute.

    Returns:
        float: Frames per second (columns per second) for the piano roll.
    """
    beats_per_second = BPM / 60.0
    fps = columns_per_beat * beats_per_second
    return fps

def midi_to_piano_roll(midi_path: str, fps: int = 20) -> np.ndarray:
    """
    Convert a MIDI file into a piano roll representation.

    Parameters
    ----------
    midi_path : str
        Path to the MIDI file.
    fps : int
        Frames per second for the output piano roll.

    Returns
    -------
    np.ndarray
        A 2D numpy array representing the piano roll.
    """
    # Load the MIDI file
    pm = pretty_midi.PrettyMIDI(midi_path)

    # Get the solo instrument (first instrument in the MIDI file)
    solo: pretty_midi.Instrument = pm.instruments[0]

    # Get the piano roll representation
    # The piano roll is a 2D array where rows correspond to MIDI pitches and columns to time frames
    # The values in the array are the velocities of the notes at that time frame
    piano_roll = solo.get_piano_roll(fs=fps)  # fs is the sampling rate (frames per second)

    return piano_roll


class ScoreFollowingEnv(gym.Env):
    def __init__(self, midi_path: str, audio_path: str, bpm: int, alignment: np.ndarray):
        super(ScoreFollowingEnv, self).__init__()

        self.alignment = alignment

        # Define audio processing parameters
        sr = 22050                   # Sample rate in Hz
        n_fft = 2048                 # FFT window size
        spec_fps = 20                     # Frames per second
        self.hop_length = int(sr / spec_fps)   # Hop length; ~1102 samples per frame
        n_mels = 78                  # Number of mel bins (log-frequency bands)
        fmin = 60                    # Minimum frequency (Hz)
        fmax = 6000                  # Maximum frequency (Hz)

        # Load audio and compute its spectrogram
        audio, self.sr = librosa.load(audio_path, sr=sr)
        spec = librosa.feature.melspectrogram(
                            y=audio,
                            sr=sr,
                            n_fft=n_fft,
                            hop_length=self.hop_length,
                            n_mels=n_mels,
                            fmin=fmin,
                            fmax=fmax
                        )
        # Convert the power spectrogram to a logarithmic (dB) scale
        self.spectrogram = librosa.power_to_db(spec, ref=np.max)

        # Initial agent and target positions
        self._agent_location = 0
        self._target_location = 0
        self.num_steps = 0

        # Define window sizes (in quarter notes)
        self.score_window_beats = 10  # Number of beats for score context
        columns_per_beat = 1  # Number of columns per beat in the piano roll
        score_fps = calculate_piano_roll_fps(columns_per_beat, bpm)  # Calculate fps based on BPM

        # Get the piano roll representation of the MIDI file
        # This is the "world" the agent will be navigating
        self.piano_roll = midi_to_piano_roll(midi_path, fps=score_fps)
        self.size = self.piano_roll.shape[1]

        self.tracking_window = 5  # max distance from target to agent before termination

        # Define dimensions for our fixed-size representations
        # Score window length is a fixed number of beats
        self.score_window_frames = self.score_window_beats * columns_per_beat
        # Spectrogram window length is a fixed number of seconds
        self.spectrogram_window_frames = 40  # Number of spectrogram frames in our context window

        score_window_shape = (self.piano_roll.shape[0], self.score_window_frames)
        spectrogram_window_shape = (self.spectrogram.shape[0], self.spectrogram_window_frames)

        self.score_window = np.zeros(score_window_shape, dtype=np.float32)
        self.spectrogram_window = np.zeros(spectrogram_window_shape, dtype=np.float32)

        # Define the observation space as a dictionary with fixed shapes
        self.observation_space = gym.spaces.Dict({
            # Agent's position in the score (piano_roll column index)
            "agent": gym.spaces.Box(low=0, high=self.size - 1, shape=(1,), dtype=np.float32),
            # Score: fixed-size matrix for the context window (each row is a beat)
            "score": gym.spaces.Box(low=0, high=np.inf,
                                    shape=score_window_shape, dtype=np.float32),
            # Spectrogram: fixed-size slice of the spectrogram (mel bins x frames)
            "spectrogram": gym.spaces.Box(low=0, high=np.inf,
                                        shape=spectrogram_window_shape, dtype=np.float32)
        })
        # We have 3 actions, corresponding to "left", "right", "stay"
        self.action_space = gym.spaces.Discrete(3)


        # Initialize pygame
        pygame.init()

        # Set screen dimensions
        screen_width, screen_height = (800, 600)
        self.screen = pygame.display.set_mode((screen_width, screen_height))

        self.clock = pygame.time.Clock()

        self.cmap = plt.get_cmap('viridis')

    def get_score_window(self):
        """
        Extract a score window centered around the agent's location.

        Returns
        -------
        np.ndarray
            A slice of the piano roll corresponding to the window.
        """
        # Calculate start and end indices for the score window
        start = max(0, self._agent_location - self.score_window_frames // 2)
        end = min(self.size, start + self.score_window_frames)

        # Extract the score window
        window = self.piano_roll[:, start:end]

        # If the window is smaller than expected (at the beginning), pad it.
        if window.shape[1] < self.score_window_frames:
            pad_width = self.score_window_frames - window.shape[1]
            window = np.pad(window, ((0, 0), (0, pad_width)), mode='constant')
        
        return window
    
    def get_spectrogram_window(self):
        """
        Extract a spectrogram window ending at the most recently processed column.

        Returns
        -------
        np.ndarray
            A slice of the spectrogram corresponding to the window.
        """
        # Calculate start and end indices for the spectrogram window
        start = max(0, self.num_steps - self.spectrogram_window_frames)
        end = min(self.spectrogram.shape[1], self.num_steps)

        # Extract the spectrogram window
        window = self.spectrogram[:, start:end]

        # If the window is smaller than expected (at the beginning), pad it.
        if window.shape[1] < self.spectrogram_window_frames:
            pad_width = self.spectrogram_window_frames - window.shape[1]
            window = np.pad(window, ((0, 0), (pad_width, 0)), mode='constant')
        
        return window
    
    def get_live_time(self):
        """
        Get the current time in the audio stream.

        Returns
        -------
        float
            The current time in seconds.
        """
        return self.num_steps * self.hop_length / self.sr
    
    def update_target_location(self):
        live_time = self.get_live_time()  # get the current time in seconds
        beats, note_onsets = self.alignment  # get the alignment data
        # Find the first note onset that is greater than the current time
        target_index = np.where(note_onsets > live_time)[0]
        if target_index.size > 0:  # if there are note onsets after the current time
            target_index = target_index[0]  # get the first one
            self._target_location = beats[target_index]  # get the corresponding beat
        else:
            # If no note onsets are found, set target_location to the end of the audio
            self._target_location = beats[-1]

    def _get_obs(self):

        # Agent's position: wrap it in an array if needed (shape=(1,))
        agent_obs = np.array([self._agent_location], dtype=np.float32)

        # Get a window of the score around the agent's position (self._agent_location)
        self.score_window = self.get_score_window()

        # Get a window of the spectrogram ending at the current time step
        # (self.num_steps is the current time step in the audio)
        self.spectrogram_window = self.get_spectrogram_window()

        return {
            "agent": agent_obs,
            "score": self.score_window,
            "spectrogram": self.spectrogram_window
        }
    
    def _get_info(self):
        return {"distance": abs(self._agent_location - self._target_location)}
    
    def reset(self, seed=None):
        self._agent_location = 0
        self._target_location = 0
        self.num_steps = 0
        observation = self._get_obs()
        info = self._get_info()
        return observation, info
    
    def step(self, action):
        # Update the agent's location based on the action taken
        # action == 0 corresponds to "left", action == 1 to "right", and action == 2 to "stay"
        if action == 0:
            self._agent_location -= 1
        elif action == 1:
            self._agent_location += 1

        # Clip the agent's location to be within the valid range
        self._agent_location = np.clip(self._agent_location, 0, self.size - 1)

        offtrack = abs(self._agent_location - self._target_location) > self.tracking_window
        end_of_score = self._agent_location >= self.size
        end_of_spectrogram = self.num_steps >= self.spectrogram.shape[1]
        terminated = offtrack or end_of_score or end_of_spectrogram

        truncated = False
        tracking_error = self._agent_location - self._target_location
        reward = 1 - abs(tracking_error) / self.tracking_window  # Compute reward based on tracking error
        self.num_steps += 1  # Increment the number of steps
        self.update_target_location()
        observation = self._get_obs()
        info = self._get_info()
        return observation, reward, terminated, truncated, info
    
    def render(self, mode="human"):
        if mode == "human":
            # Convert the array to a pygame Surface.
            spec_img = self.spectrogram_window
            spec_img = (spec_img - np.min(spec_img)) / (np.max(spec_img) - np.min(spec_img))  # Normalize to [0, 1]
            spec_img = self.cmap(spec_img)
            spec_img = (spec_img[:, :, :3] * 255).astype(np.uint8)
            spec_img = np.transpose(spec_img, (1, 0, 2))  # Transpose because pygame expects shape (width, height, channels)
            spec_img = np.flip(spec_img, axis=1)  # Flip the image vertically
            spec_surface = pygame.surfarray.make_surface(spec_img)
            scaled_spec_surface = pygame.transform.scale(spec_surface, (800, 300))

            piano_img = self.score_window[50:75]
            piano_img = (piano_img - np.min(piano_img)) / (np.max(piano_img) - np.min(piano_img))  # Normalize to [0, 1]
            piano_img = self.cmap(piano_img)
            piano_img = (piano_img[:, :, :3] * 255).astype(np.uint8)
            piano_img = np.transpose(piano_img, (1, 0, 2))  # Transpose because pygame expects shape (width, height, channels)
            piano_img = np.flip(piano_img, axis=1)  # Flip the image vertically
            piano_img = pygame.surfarray.make_surface(piano_img)
            scaled_piano_surface = pygame.transform.scale(piano_img, (800, 300))

            self.screen.blit(scaled_spec_surface, (0, 0))
            self.screen.blit(scaled_piano_surface, (0, 300))
            pygame.display.flip()
            self.clock.tick(20)
        else:
            raise NotImplementedError(f"Render mode '{mode}' is not supported.")


# Example usage:
if __name__ == "__main__":
    alignment = [(i, 6 / 7 * i) for i in range(0, 64)]
    alignment = np.array(alignment).T
    print(alignment.shape)
    env = ScoreFollowingEnv(midi_path="ode_beg.mid", audio_path="ode_beg.mp3", bpm=70, alignment=alignment)

    # Reset the environment
    obs, info = env.reset()
    terminated = False

    # Get the initial agent location
    agent_location = obs["agent"][0]


    filenames = []
    if not os.path.exists("frames"):
        os.makedirs("frames")

    i = 0
    while not terminated:
        if env._target_location > agent_location:
            action = 1  # agent moves right
        else:
            action = 2  # agent stays

        # Take a step in the environment
        obs, reward, terminated, truncated, info = env.step(action)
        env.render()
        agent_location, score_window, spectrogram_window = obs["agent"][0], obs["score"], obs["spectrogram"]

        # plot the score window and spectrogram window
        plt.subplot(2, 1, 1)
        plt.imshow(score_window[50:75], aspect='auto', origin='lower')
        # plt.title("Score Window")
        plt.subplot(2, 1, 2)
        plt.imshow(spectrogram_window, aspect='auto', origin='lower')
        # plt.title("Spectrogram Window")
        filename = f"frames/frame_{i:03d}.png"
        i += 1
        plt.savefig(filename)
        plt.close()
        filenames.append(filename)

        # Print the agent's location and reward
        print(f"Step {i}: Agent location: {agent_location}, Reward: {reward}, Info: {info}")


    # Use imageio to create an animated GIF from the saved frames.
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave('animation.mp4', images, fps=20)  # duration is the time per frame in seconds