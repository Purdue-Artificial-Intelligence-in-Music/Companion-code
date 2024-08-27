from AudioBuffer import AudioBuffer
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
        Diagonal weight for OTW. Values less than 2 bias toward diagonal steps.

    Attributes
    ----------
    sample_rate : int
        Sample rate of the audio buffer
    channels : int
        Number of channels
    frames_per_buffer : int
        Number of frames per buffer for PyAudio stream
    window_length : int
        Number of frames per chroma feature
    mic : int
        AudioBuffer object to store microphone audio
    chroma_maker : ChromaMaker
        ChromaMaker object to create CENS features
    ref_audio : np.ndarray
        Reference audio
    ref : np.ndarray
        Reference sequence of CENS feaures
    otw : OTW
        OTW object to align live features with reference sequence
    path : list
        Alignment path between live and reference sequences

    """
    def __init__(self, path, source=None, sample_rate=16000, channels=1, frames_per_buffer=1024, window_length=4096, c=10, max_run_count=3, diag_weight=0.4):
        # Initialize parent class
        super(ScoreFollower, self).__init__(daemon=True)

        self.sample_rate = sample_rate
        self.channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.window_length = window_length

        # Create buffer for microphone audio
        self.mic = AudioBuffer(source=source,
                               sample_rate=sample_rate,
                               channels=channels,
                               frames_per_buffer=frames_per_buffer,
                               num_chunks=100)
        
        # Load reference audio
        mono = channels == 1
        self.ref_audio, _ = librosa.load(path, sr=sample_rate, mono=mono)
        self.chroma_maker = ChromaMaker(sr=sample_rate, n_fft=window_length)

        # Generate chroma features for reference audio with no over lap
        self.ref = audio_to_np_cens(y=self.ref_audio, sr=sample_rate, n_fft=window_length, hop_len=window_length)

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
                return self.otw.j, self.otw.t
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
        return j, self.otw.t

    def run(self):
        """Start the microphone input stream. """
        self.mic.start()

    def stop(self):
        """Stop the microphone input stream. """
        self.mic.stop()
        self.mic.join()

    def is_active(self):
        """Return True if the microphone input stream is active and we have not reached the end of the otw buffer"""
        return self.mic.is_active() and self.otw.t < self.otw.live.shape[-1] - 1
        # return self.otw.j < self.ref.shape[-1] - 1

    def get_backwards_path(self, b):
        cost_matrix = self.otw.D
        ref_index = self.otw.j # row index
        live_index = self.otw.t # column index

        j = ref_index
        t = live_index
        backwards_path = []

        while j > ref_index - b and (0, 0) not in backwards_path:
            down, left, diagonal = cost_matrix[j-1, t], cost_matrix[j, t-1], cost_matrix[j-1, t-1]
            minimum_cost = min(down, left, diagonal)
            if minimum_cost == down:
                backwards_path.append((j-1, t))
                j -= 1
            elif minimum_cost == left:
                backwards_path.append((j, t-1))
                t -= 1
            else:
                backwards_path.append((j-1, t-1))
                j -= 1
                t -= 1
        
        return backwards_path
        

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    follower = ScoreFollower(path='youtube_X5KoiE_u1iE_audio.wav', 
                             sample_rate=16000,
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
            print(follower.mic.count)
            print(f'Live index: {follower.otw.t}, Ref index: {follower.otw.j}/{follower.ref.shape[-1] - 1}')
    except KeyboardInterrupt:
        follower.stop()
        follower.join()

    # indices = np.asarray(follower.path).T
    # follower.otw.D[(indices[0], indices[1])] = np.inf
    # plt.imshow(follower.otw.D)
    # plt.show()
    
    t = follower.otw.t
    fig, axes = plt.subplots(3, 1, sharex=False, sharey=True)
    mic_chroma = np.flip(follower.otw.live[:, :t], axis=0)
    ref_chroma = np.flip(follower.otw.ref, axis=0)
    
    j = (follower.otw.j)/(follower.ref.shape[-1] - 1)
    if t > j:
        back_path = follower.get_backwards_path(t)
    else:
        back_path = follower.get_backwards_path(j)

    print(f'Backwards path: {back_path}')
    print(mic_chroma.shape)
    print(ref_chroma.shape)
    axes[0].imshow(mic_chroma)
    axes[1].imshow(ref_chroma)
    plt.show()

    plt.imshow(follower.otw.D)
    path = np.array(back_path)
    plt.plot(path[:, 1], path[:, 0], 'ro-', label='Backwards Path')
    plt.show()
