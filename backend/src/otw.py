"""
Copyright (c) 2024 Matthew Caren

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# Variable names have been modified for clarity

from .features import Features
import numpy as np
from typing import Dict, Tuple


def find_key(d: Dict, k: str):
    """Returns the value of key `k` in dictionary `d`, or None if key is not found."""
    return d.get(k)


class OnlineTimeWarping:
    def __init__(
        self,
        ref: Features,
        sr: int,
        n_fft: int,
        big_c: int,
        max_run_count: int,
        diag_weight: float,
    ):
        """
        Initialize the Online Time Warping [1] algorithm for streaming alignment
        of live audio features to a reference feature sequence.

        Parameters
        ----------
        ref : Features
            Precomputed feature sequence of the reference audio (e.g., CENS chroma).
            Each feature vector corresponds to a window of mono audio frames.
        sr : int
            Sampling rate of audio in Hz.
        n_fft : int
            Number of audio samples per feature window (FFT size).
        big_c : int
            Width of the search window for constrained DTW.
        max_run_count : int
            Maximum consecutive steps allowed in one direction (slope constraint).
        diag_weight : float
            Weight applied to diagonal moves in the accumulated cost matrix.

        Attributes
        ----------
        ref : Features
            Reference feature sequence.
        live : Features
            Buffer for live audio features of same type as `ref`.
        feature_len : int
            Dimensionality of the feature vectors.
        ref_len : int
            Number of feature frames in the reference sequence.
        accumulated_cost : np.ndarray
            Dynamic programming matrix storing cumulative alignment costs.
        live_index : int
            Index of current live feature frame.
        ref_index : int
            Index of current reference feature frame.
        previous_step : str
            Last alignment step taken ('ref', 'live', or 'both').
        run_count : int
            Count of consecutive steps taken in the same direction.
        window_size : int
            DTW search window size.
        max_run_count : int
            Maximum allowed consecutive steps in one direction.
        diag_weight : float
            Weight factor for diagonal steps.
        last_ref_index : int
            Last matched reference frame index, prevents backward jumps.
        path_z : list[int]
            History of matched reference indices for debugging or tracking.

        Notes
        -----
        This implementation is adapted from:
        [1] Dixon, Simon. "Live Tracking of Musical Performances Using On-Line Time Warping"
        """

        self.ref = ref  # Reference sequence (Features object)

        self.feature_len = self.ref.FEATURE_LEN
        self.ref_len = self.ref.num_features

        live_size = self.ref_len * 4

        self.live = type(self.ref)(
            sr, n_fft, live_size
        )  # Live input, same Features subclass as ref

        self.accumulated_cost = np.full(
            (self.ref_len, live_size), np.inf, dtype=np.float32
        )

        self.live_index = -1  # Index in live sequence
        self.ref_index = 0  # Index in ref sequence
        self.previous_step = "---"  # 'ref' | 'live' | 'both'
        self.run_count = 1  # Run count for controlling step switching

        # Parameters
        self.window_size = big_c
        self.max_run_count = max_run_count
        self.diag_weight = diag_weight

        self.last_ref_index = (
            0  # Track the last reference index to prevent backward steps
        )
        self.path_z = []  # Chosen path for debugging or tracking

    def insert(self, live_frames: np.ndarray) -> int:
        """
        Insert a new frame of live audio features and update alignment position.

        Parameters
        ----------
        live_frames : np.ndarray
            1D array representing a single live feature vector computed from a
            mono audio window of length `n_fft` samples (shape: [feature_len]).

        Returns
        -------
        int
            Estimated frame index in the reference feature sequence that best matches
            the current live input.

        Notes
        -----
        This method updates the accumulated cost matrix with the new live frame,
        performs online DTW steps, and returns the current estimated alignment position.
        """
        self.live_index += 1
        self.live.insert(live_frames)

        for k in range(
            max(0, self.ref_index - self.window_size + 1), self.ref_index + 1
        ):
            self._update_accumulated_cost(k, self.live_index)

        path = []
        while True:
            step, path_point = self._get_best_step()
            path.append(path_point)

            if step == "live":
                break  # Stop if the best step is to move in the live sequence

            # Increment referene index, but keep it in bounds
            self.ref_index = min(self.ref_index + 1, self.ref_len - 1)

            # Calculate a new reference column
            for k in range(
                max(self.live_index - self.window_size + 1, 0), self.live_index + 1
            ):
                self._update_accumulated_cost(self.ref_index, k)

            if step == "both":
                break

        # Update the path with the new reference index
        current_ref_position = path[-1][0]
        self.path_z.append(current_ref_position)

        # Prevent backward steps
        if current_ref_position < self.last_ref_index:
            current_ref_position = self.last_ref_index

        self.last_ref_index = current_ref_position

        # Return the current reference index
        return current_ref_position

    def _get_best_step(self) -> Tuple[str, Tuple[int, int]]:
        """
        Determines the optimal next step in the DTW alignment path
        using the current accumulated cost matrix.

        Returns
        -------
        step : str
            Best step direction: 'ref', 'live', or 'both'.
        indices : Tuple[int, int]
            Indices (ref_index, live_index) representing the alignment point for this step.

        Notes
        -----
        Considers slope constraints, run counts, and weighting factors in decision.
        """

        row_costs = self.accumulated_cost[self.ref_index, : self.live_index + 1]
        col_costs = self.accumulated_cost[: self.ref_index + 1, self.live_index]

        best_t = np.argmin(row_costs)
        best_j = np.argmin(col_costs)

        # Check if the best step is to move in the live sequence
        if (
            self.accumulated_cost[best_j, self.live_index]
            < self.accumulated_cost[self.ref_index, best_t]
        ):
            best_t = self.live_index
            step = "live"
        elif (
            self.accumulated_cost[best_j, self.live_index]
            > self.accumulated_cost[self.ref_index, best_t]
        ):  # Otherwise, move in the reference sequence
            best_j = self.ref_index
            step = "ref"
        else:
            best_t = self.live_index
            best_j = self.ref_index
            step = "both"

        # If the best step is to move in both sequences, choose the one with the lowest cost
        if best_t == self.live_index and best_j == self.ref_index:
            step = "both"

        # At the start, move in both sequences
        if self.live_index < self.window_size:
            step = "both"

        # If the run count exceeds the maximum run count, switch steps
        if self.run_count >= self.max_run_count:
            step = "live" if self.previous_step == "ref" else "ref"

        # Reset the run count if the step changes
        if step == "both" or self.previous_step != step:
            self.run_count = 1
        else:  # Otherwise, increment the run count
            self.run_count += 1

        self.previous_step = step

        # If the reference index is at the end, move in the live sequence
        if self.ref_index == self.ref_len - 1:
            step = "live"

        # Return the best step and indices
        return step, (best_j, best_t)

    def _update_accumulated_cost(self, ref_index: int, live_index: int):
        """
        Updates the dynamic programming cost matrix at a specific (ref_index, live_index)
        position based on the similarity between live and reference features.

        Parameters
        ----------
        ref_index : int
            Frame index in the reference sequence.
        live_index : int
            Frame index in the live sequence.

        Notes
        -----
        The local cost is calculated as 1 minus the similarity measure defined in
        `Features.compare_features()`, which may vary depending on the feature subclass.
        The accumulated cost matrix is updated considering diagonal,
        vertical, and horizontal transitions.
        """
        cost = 1 - self.ref.compare_features(self.live, ref_index, live_index)

        if ref_index == 0 and live_index == 0:
            self.accumulated_cost[ref_index, live_index] = cost
            return

        steps = []

        # Calculate the cost of moving diagonally, vertically, and horizontally
        if ref_index > 0 and live_index > 0:
            steps.append(
                self.accumulated_cost[ref_index - 1, live_index - 1]
                + self.diag_weight * cost
            )
        if ref_index > 0:
            steps.append(self.accumulated_cost[ref_index - 1, live_index] + cost)
        if live_index > 0:
            steps.append(self.accumulated_cost[ref_index, live_index - 1] + cost)
        self.accumulated_cost[ref_index, live_index] = min(steps)
