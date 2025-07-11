from .otw import OnlineTimeWarping as OTW
import numpy as np
from .features_cens import CENSFeatures


class ScoreFollower:
    """
    Performs real-time audio-to-audio alignment using Online Time Warping (OTW).

    This class wraps the OTW algorithm and provides an interface to incrementally
    align a live audio stream (e.g., from a microphone) to a fixed reference audio file.

    Parameters
    ----------
    ref_filename : str
        Path to the reference audio file.
    c:  int, optional
        Width of the DTW search window (default: 10).
    max_run_count : int, optional
        Slope constraint for how many steps can occur in one direction before switching (default: 3).
    diag_weight : float, optional
        Weight for diagonal steps in DTW cost calculation; values < 2 bias toward diagonal steps (default: 0.4).
    sample_rate : int, optional
        Sample rate for audio processing (default: 44100).
    win_length : int, optional
        Number of samples per audio frame (FFT window length, default: 8192).
    features_cls : Type[Features], optional
        Feature extraction class to use (default: CENSFeatures).

    Attributes
    ----------
    ref : np.ndarray
        Matrix of reference CENS feature vectors (shape: [n_frames, 12]).
    otw : OTW
        Online time warping object for matching features.
    path : list of tuple
        List of (ref_index, live_index) alignment points.
    sample_rate : int
        Sample rate of the audio signal.
    win_length : int
        Number of samples per feature frame.
    """

    def __init__(
        self,
        ref_filename: str,
        c: int = 10,
        max_run_count: int = 3,
        diag_weight: float = 0.4,
        sample_rate: int = 44100,
        win_length: int = 8192,
        hop_length: int = 4096,
        features_cls=CENSFeatures,
    ):
        self.sample_rate = sample_rate
        self.win_length = win_length

        self.ref_features = features_cls.from_file(
            filepath=ref_filename,
            sr=sample_rate,
            win_length=win_length,
            hop_length=hop_length,
        )

        # Initialize OTW object
        self.otw = OTW(
            self.ref_features, sample_rate, win_length, c, max_run_count, diag_weight
        )

        # Online DTW alignment path
        self.path = []

    def step(self, frames: np.ndarray) -> float:
        """
        Process the next chunk of mono audio samples and update alignment path.

        Parameters
        ----------
        frames : np.ndarray
            1D array of mono audio samples. Must be at least `win_length` in length.
            If fewer, zero-padding is applied.

        Returns
        -------
        float
            Estimated position in the reference audio (in seconds).
        """
        # If the number of frames is too small, pad with zeros
        if frames.shape[-1] < self.win_length:
            frames = np.pad(
                frames,
                ((0, 0), (0, self.win_length - frames.shape[-1])),
                mode="constant",
                constant_values=((0, 0), (0, 0)),
            )

        # Calculate position in reference audio
        ref_index = self.otw.insert(frames)

        # Record position in alignment path
        self.path.append((ref_index, self.otw.live_index))

        # Return timestamp in the reference audio in seconds
        return (ref_index + 1) * self.win_length / self.sample_rate

    def get_backwards_path(self, b):
        """
        Traces a backwards path from the current alignment position using the accumulated cost matrix.

        Parameters
        ----------
        b : int
            Number of steps to trace backward from the current reference index.

        Returns
        -------
        list of tuple
            A list of (ref_index, live_index) coordinates representing the backward path.

        Notes
        -----
        Used to analyze or visualize local sections of the DTW path.
        """
        cost_matrix = self.otw.accumulated_cost
        ref_index = self.otw.ref_index  # row index
        live_index = self.otw.live_index  # column index

        j = ref_index
        t = live_index
        backwards_path = []

        while j > ref_index - b and (0, 0) not in backwards_path:
            down, left, diagonal = (
                cost_matrix[j - 1, t],
                cost_matrix[j, t - 1],
                cost_matrix[j - 1, t - 1],
            )
            minimum_cost = min(down, left, diagonal)
            if minimum_cost == down:
                backwards_path.append((j - 1, t))
                j -= 1
            elif minimum_cost == left:
                backwards_path.append((j, t - 1))
                t -= 1
            else:
                backwards_path.append((j - 1, t - 1))
                j -= 1
                t -= 1

        return backwards_path

    def get_path_difference(self, back_path):
        return [x for x in self.path if x not in back_path]


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import os
    import librosa

    reference = os.path.join(
        "data", "audio", "twinkle_twinkle", "200bpm", "instrument_0.wav"
    )
    source = os.path.join(
        "data", "audio", "twinkle_twinkle", "200bpm", "instrument_0.wav"
    )

    source_audio = librosa.load(source, sr=44100)
    source_audio = source_audio[0].reshape((1, -1))

    score_follower = ScoreFollower(
        ref_filename=reference,
        c=50,
        max_run_count=3,
        diag_weight=0.5,
        sample_rate=44100,
        win_length=4096,
    )

    for i in range(0, source_audio.shape[-1], 4096):
        frames = source_audio[:, i : i + 4096]
        estimated_time = score_follower.step(frames)
        # print(
        #     f'Live index: {score_follower.otw.live_index}, Ref index: {score_follower.otw.ref_index}')
        print(
            f"Estimated time: {estimated_time}, Ref index: {score_follower.otw.ref_index * score_follower.win_length / score_follower.sample_rate}"
        )

    print(score_follower.path)
