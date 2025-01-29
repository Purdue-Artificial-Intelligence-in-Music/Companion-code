import numpy as np
import soundfile


class AudioBuffer:
    """Thread to save microphone audio to a buffer.

    Parameters
    ----------
    sample_rate : int, optional
        Sample rate of the audio buffer
    channels : int, optional
        Number of channels
    max_duration: int, optional
        Maximum duration of the recorded audio in seconds

    Attributes
    ----------
    sample_rate : int
        Sample rate of the audio buffer
    channels : int
        Number of channels
    length : int
        Maximum number of frames in buffer
    buffer : np.ndarray
        Array containing audio frames
    write_index : int
        Index of the next element in which audio frames will be stored
    read_index : int
        Index of the next element from which audio frames will be read
    count : int
        Number of unread frames in the buffer
    """

    def __init__(self, sample_rate: int = 44100, channels: int = 1, max_duration: int = 600):

        # Params
        self.sample_rate = sample_rate
        self.length = max_duration * self.sample_rate

        # Create buffer
        self.buffer = np.empty(shape=(channels, self.length), dtype=np.float32)

        # Track buffer
        self.write_index = 0
        self.read_index = 0
        self.unread_frames = 0  # Number of unread frames in the buffer

    def write(self, frames: np.ndarray):
        """Write audio frames to buffer.

        Parameters
        ----------
        frames : np.ndarray
            Audio frames to write to the buffer.

        Returns
        -------
        None

        """

        # Get the number of frames to write
        num_frames = frames.shape[-1]

        # If the buffer will exceed its length, raise exception
        if self.write_index + num_frames > self.length:
            raise Exception('Error: Not enough space left in buffer')

        # Write frames
        self.buffer[:, self.write_index:self.write_index + num_frames] = frames

        # Increment the write index
        self.write_index += num_frames

        # Increase the count
        self.unread_frames += num_frames

    def read(self, num_frames: int) -> np.ndarray:
        """Returns the specified number of frames from the buffer starting at the read index.

        Parameters
        ----------
        num_frames : int
            Number of frames to read from the buffer
        num_frames: int :


        Returns
        -------
        np.ndarray
            Array of audio frames with shape (channels, num_frames)

        """

        # If the number of frames to read exceeds the number of unread frames, raise exception
        if num_frames > self.unread_frames:
            print('AudioBuffer read error')
            raise Exception(
                f'Error: Attempted to read {num_frames} frames but count is {self.unread_frames}')

        # Read frames
        frames = self.buffer[:, self.read_index:self.read_index+num_frames]

        self.read_index += num_frames
        self.unread_frames -= num_frames

        return frames

    def get_time(self) -> int:
        """Get the length of the audio written to the buffer in seconds. """
        return self.write_index / self.sample_rate

    def get_audio(self) -> np.ndarray:
        """Get all the audio written to the buffer so far. """
        return self.buffer[:, :self.write_index]

    def save(self, path):
        """
        Parameters
        ----------
        path : str
            Filepath to save the audio to.

        Returns
        -------
            None
        """
        audio = self.get_audio()
        audio = audio.reshape((-1, ))
        soundfile.write(path, audio, self.sample_rate)


if __name__ == '__main__':
    import librosa

    source = 'data/audio/bach/live/variable_tempo.wav'
    audio = librosa.load(source, sr=44100)
    audio = audio[0].reshape((1, -1))
    audio = audio.astype(np.float32)

    buffer = AudioBuffer(sample_rate=44100,
                         channels=1,
                         max_duration=600)

    for i in range(0, audio.shape[-1], 2048):
        frames = audio[:, i:i+2048]
        buffer.write(frames)

    buffer.save('buffer_audio.wav')
