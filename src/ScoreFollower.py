from buffer import AudioBuffer
import librosa
from otw import OTW
from threading import Thread
import time
import numpy as np
import matplotlib.pyplot as plt
from features import ChromaMaker, audio_to_np_cens


class ScoreFollower(Thread):
    """Performs online dynamic time warping (DTW) between reference audio and live microphone audio

    Parameters
    ----------
    path : str
        Path to reference audio file
    sample_rate : int, optional
        Sample rate of the audio buffer
    channels : int, optional
        Number of channels
    frames_per_buffer : int, optional
        Number of frames per buffer for PyAudio stream
    window_length : int, optional
        Number of frames per chroma feature
    c : int, optional
        Width of online DTW search
    max_run_count : int, optional
        Slope constraint for online DTW (1/max_run_count to max_run_count)
    diag_weight : int, optional
        Index of the next element from which audio frames will be read

    Attributes
    ----------
    sample_rate : int, optional
        Sample rate of the audio buffer
    channels : int, optional
        Number of channels
    frames_per_buffer : int, optional
        Number of frames per buffer for PyAudio stream
    window_length : int, optional
        Number of frames per chroma feature
    c : int, optional
        Width of online DTW search
    max_run_count : int, optional
        Slope constraint for online DTW (1/max_run_count to max_run_count)
    diag_weight : int, optional
        Index of the next element from which audio frames will be read

    """
    def __init__(self, path, sample_rate=22050, channels=1, frames_per_buffer=1024, window_length=4096, c=10, max_run_count=3, diag_weight=0.4):
        # Initialize parent class
        super(ScoreFollower, self).__init__()
        self.daemon = True

        self.sample_rate = sample_rate
        self.channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.window_length = window_length

        # Create buffer for microphone audio
        self.mic = AudioBuffer(sample_rate=sample_rate,
                               channels=channels,
                               frames_per_buffer=frames_per_buffer,
                               num_chunks=100)
        
        # Load reference audio
        ref_audio, _ = librosa.load(path, sr=22050)
        self.chroma_maker = ChromaMaker(sr=sample_rate, n_fft=window_length)

        # Generate chroma features for reference audio with no over lap
        self.ref = audio_to_np_cens(y=ref_audio, sr=sample_rate, n_fft=window_length, hop_len=window_length)

        # Params for online DTW
        params = {
        "c": c,
        "max_run_count": max_run_count,
        "diag_weight": diag_weight
        }

        # Initialize online DTW object
        self.otw = OTW(ref=self.ref, params=params)

        # Online DTW alignment path
        self.path = []

    def get_chroma(self, audio):
        """

        Parameters
        ----------
        audio : np.ndarray
            Audio frames to convert to a chroma feature

        Returns
        -------
        np.ndarray
            Chroma feature
        """
        # If the number of frames is too small, pad with zeros
        if audio.shape[-1] < self.window_length:
            audio = np.pad(audio, ((0, 0), (0, self.window_length - audio.shape[-1])), mode='constant', constant_values=((0, 0), (0, 0)))
        
        # Return a chroma feature for the audio
        return self.chroma_maker.insert(audio)

    def step(self):
        """Calculate next step in the alignment path between the microphone and reference audio """
        
        # While the number of unread frames is less than the window length
        while self.mic.count < self.window_length:
            # If the mic is not active, return the last position in the reference audio
            if not self.mic.is_active():
                return self.otw.j
            # If the mic is active, wait for more audio frames
            time.sleep(0.01)

        # Read audio frames from the buffer
        audio = self.mic.read(self.window_length)
        # print(f'Read index: {self.mic.read_index}, Write index: {self.mic.write_index}, Count: {self.mic.count}')
        
        # Generate chroma feature
        chroma = self.get_chroma(audio)

        # Calculate position in reference audio
        j = self.otw.insert(chroma)

        # Record position in alignment path
        self.path.append((j, self.otw.t))

        # Return position in reference audio
        return j

    def run(self):
        """Start the microphone input stream. """
        self.mic.start()

    def stop(self):
        """Stop the microphone input stream. """
        self.mic.stop()

    def is_active(self):
        """Return True if the microphone input stream is active and we have not reached the end of the otw buffer"""
        return self.mic.is_active() and self.otw.t < self.otw.live.shape[-1] - 1

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    follower = ScoreFollower(path='soloist.wav', 
                             sample_rate=22050,
                             channels=1,
                             frames_per_buffer=1024,
                             window_length=4096,
                             c=10,
                             max_run_count=3,
                             diag_weight=2)

    follower.start()

    while not follower.is_active():
        time.sleep(0.01)

    try:
        while follower.is_active():
            follower.step()
    except KeyboardInterrupt:
        follower.stop()

    indices = np.asarray(follower.path).T
    follower.otw.D[(indices[0], indices[1])] = np.inf
    plt.imshow(follower.otw.D)
    plt.show()
