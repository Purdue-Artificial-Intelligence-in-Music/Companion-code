from .otw import OnlineTimeWarping as OTW
import numpy as np
from .features_cens import CENSFeatures, file_to_np_cens

class ScoreFollower:
    """Performs online dynamic time warping (DTW) between reference audio and live microphone audio

    Parameters
    ----------
    reference : str
        Path to reference audio file
    c : int, optional
        Width of online DTW search
    max_run_count : int, optional
        Slope constraint for online DTW (1/max_run_count to max_run_count)
    diag_weight : int, optional
        Diagonal weight for OTW. Values less than 2 bias toward diagonal steps.
    sample_rate : int, optional
        Sample rate of the audio buffer

    Attributes
    ----------
    sample_rate : int
        Sample rate of the audio buffer
    win_length : int
        Number of frames per chroma feature
    channels : int
        Number of channels
    frames_per_buffer : int
        Number of frames per buffer for PyAudio stream
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

    def __init__(self, reference: str, c: int = 10, max_run_count: int = 3, diag_weight: int = 0.4, sample_rate: int = 44100, win_length: int = 8192):

        self.sample_rate = sample_rate
        self.win_length = win_length

        # Instantiate ChromaMaker object
        self.chroma_maker = CENSFeatures(sr=sample_rate, n_fft=win_length)

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

    def _get_chroma(self, audio: np.ndarray) -> np.ndarray:
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
            audio = np.pad(audio, ((0, 0), (0, self.win_length -
                           audio.shape[-1])), mode='constant', constant_values=((0, 0), (0, 0)))

        # Return a chroma feature for the audio
        return self.chroma_maker.insert(audio)

    def step(self, frames: np.ndarray) -> float:
        """Calculate next step in the alignment path between the microphone and reference audio """

        # Generate chroma feature
        chroma = self._get_chroma(frames)

        # Calculate position in reference audio
        ref_index = self.otw.insert(chroma)

        # Record position in alignment path
        self.path.append((ref_index, self.otw.live_index))

        # Return timestamp in the reference audio in seconds
        return (ref_index+1) * self.win_length / self.sample_rate 

    def get_backwards_path(self, b):
        cost_matrix = self.otw.accumulated_cost
        ref_index = self.otw.ref_index  # row index
        live_index = self.otw.live_index  # column index

        j = ref_index
        t = live_index
        backwards_path = []

        while j > ref_index - b and (0, 0) not in backwards_path:
            down, left, diagonal = cost_matrix[j-1,
                                               t], cost_matrix[j, t-1], cost_matrix[j-1, t-1]
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

    def get_path_difference(self, back_path):
        return [x for x in self.path if x not in back_path]


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import os
    import librosa
    reference = os.path.join('data', 'audio', 'twinkle_twinkle', '200bpm', 'instrument_0.wav')
    source = os.path.join('data', 'audio', 'twinkle_twinkle', '200bpm', 'instrument_0.wav')

    source_audio = librosa.load(source, sr=44100)
    source_audio = source_audio[0].reshape((1, -1))

    score_follower = ScoreFollower(reference=reference,
                                   c=50,
                                   max_run_count=3,
                                   diag_weight=0.5,
                                   sample_rate=44100,
                                   win_length=4096)

    for i in range(0, source_audio.shape[-1], 4096):
        frames = source_audio[:, i:i+4096]
        estimated_time = score_follower.step(frames)
        # print(
        #     f'Live index: {score_follower.otw.live_index}, Ref index: {score_follower.otw.ref_index}')
        print(
            f'Estimated time: {estimated_time}, Ref index: {score_follower.otw.ref_index * score_follower.win_length / score_follower.sample_rate}')


    print(score_follower.path)
