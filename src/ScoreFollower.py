from AudioBuffer import AudioBuffer
import librosa
from otw import OTW
from threading import Thread
import time
import numpy as np
import matplotlib.pyplot as plt
from features import ChromaMaker, audio_to_np_cens


class ScoreFollower:
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
    def __init__(self, reference: str, source: str = None, c: int = 10, max_run_count: int = 3, diag_weight: int = 0.4, sample_rate: int = 16000, win_length: int = 4096, **kwargs, ):

        self.sample_rate = sample_rate
        self.win_length = win_length

        # Create buffer for microphone audio
        self.mic = AudioBuffer(source=source,
                               max_duration=600,
                               **kwargs)

        # Instantiate ChromaMaker object
        self.chroma_maker = ChromaMaker(sr=sample_rate, n_fft=win_length)
        
        # Params for OTW
        params = {
        "sr": sample_rate,
        "n_fft": win_length,
        "ref_hop_len": win_length,
        "c": c,
        "max_run_count": max_run_count,
        "diag_weight": diag_weight
        }

        self.ref = file_to_np_cens(filepath=reference, params=params)

        # Initialize OTW object
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
        if audio.shape[-1] < self.win_length:
            audio = np.pad(audio, ((0, 0), (0, self.win_length - audio.shape[-1])), mode='constant', constant_values=((0, 0), (0, 0)))
        
        # Return a chroma feature for the audio
        return self.chroma_maker.insert(audio)

    def step(self):
        """Calculate next step in the alignment path between the microphone and reference audio """
        
        # While the number of unread frames is less than the window length
        while self.mic.count < self.win_length:
            # If the mic is not active, return the last position in the reference audio
            if not self.mic.is_active():
                print("Microphone is no longer active and all audio has been processed.")
                return None
            # If the mic is active, wait for more audio frames
            time.sleep(0.01)

        # Read audio frames from the buffer
        audio = self.mic.read(self.win_length)

        # Generate chroma feature
        chroma = self.get_chroma(audio)

        # Calculate position in reference audio
        j = self.otw.insert(chroma)

        # Record position in alignment path
        self.path.append((j, self.otw.t))

        # Return position in reference audio
        return j

    def start(self):
        """Start the microphone input stream. """
        self.mic.start()

    def pause(self):
        self.mic.pause()

    def unpause(self):
        self.mic.unpause()

    def stop(self):
        """Stop the microphone input stream. """
        self.mic.stop()

    def is_active(self):
        """Return True if the microphone input stream is active and we have not reached the end of the otw buffer"""
        return self.mic.is_active() and self.otw.t < self.otw.live.shape[-1] - 1
    
    def get_estimated_time(self):
        return self.otw.j * self.win_length / self.sample_rate


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
    score_follower = ScoreFollower(reference='audio/C_Major_Scale_Duet/track0.wav',
                                   source='audio/C_Major_Scale_Tempo_Variation/track0.wav',
                                   c=8,
                                   max_run_count=3,
                                   diag_weight=0.4,
                                   sample_rate=16000,
                                   win_length=8192,
                                   channels=1,
                                   frames_per_buffer=1024)

    score_follower.start()

    while not score_follower.is_active():
        time.sleep(0.01)

    try:
        while score_follower.is_active():
            ref_index = score_follower.step()
            print(f'Live index: {score_follower.otw.t}, Ref index: {ref_index}/{score_follower.ref.shape[-1] - 1}')
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
        score_follower.stop()

    cost_matrix = score_follower.otw.D
    indices = np.asarray(score_follower.path).T
    cost_matrix[(indices[0], indices[1])] = np.inf

    plt.figure()
    plt.imshow(cost_matrix)
    plt.title('OTW Cost Matrix')
    plt.xlabel('Live Sequence')
    plt.ylabel('Reference Sequence')
    plt.show()

    plt.imshow(follower.otw.D)
    path = np.array(back_path)
    plt.plot(path[:, 1], path[:, 0], 'ro-', label='Backwards Path')
    plt.show()
