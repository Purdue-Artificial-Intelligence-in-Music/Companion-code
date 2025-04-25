"""
Copyright (c) 2024 Matthew Caren

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# Variable names have been modified for clarity

import numpy as np
from typing import Dict, Tuple


def find_key(d: Dict, k: str):
    """Returns the value of key `k` in dictionary `d`, or None if key is not found."""
    return d.get(k)


class OnlineTimeWarping:
    def __init__(self, ref: np.ndarray, params: Dict[str, float]):
        """
        Implements Online Time Warping [1], adapted for Python as a streaming algorithm 
        with a few modifications for clarity.

        Parameters
        ----------
        ref : np.ndarray
            Reference time series (assumed chroma).
        params : Dict[str, float]
            Dictionary of configuration parameters. Expected keys are:
            - "c": int - Search width for the time warping.
            - "max_run_count": int - Maximum run count for controlling step switching.
            - "diag_weight": float - Weight for the diagonal step in the cost calculation.

        Attributes
        ----------
        ref : np.ndarray
            Reference sequence (assumed chroma).
        feature_len : int
            Length of the feature dimension of the reference sequence.
        ref_len : int
            Length of the reference sequence.
        live : np.ndarray
            Live input sequence initialized with zeros.
        accumulated_cost : np.ndarray
            Accumulated cost matrix initialized with infinity.
            Index in the live sequence.
            Index in the reference sequence.
        previous_step : str
            Previous step taken ('ref', 'live', or 'both').
        run_count : int
            Run count for controlling step switching.
        window_size : int
            Window size for the time warping.
        max_run_count : int
            Maximum run count for controlling step switching.
        diag_weight : float
            Weight for the diagonal step in the cost calculation.
        last_ref_index : int
            Tracks the last reference index to prevent backward steps.
        path_z : list
            Chosen path for debugging or tracking.

        [1] Simon Dixon: "Live Tracking of Musical Performances Using On-Line Time Warping".
        """
        self.ref = ref  # Reference sequence (assumed chroma)
        self.feature_len, self.ref_len = self.ref.shape
        self.live = np.zeros(
            (self.feature_len, self.ref_len * 4), dtype=np.float32)  # Live input
        self.accumulated_cost = np.full(
            (self.ref_len, self.ref_len * 4), np.inf, dtype=np.float32)

        self.live_index = -1  # Index in live sequence
        self.ref_index = 0  # Index in ref sequence
        self.previous_step = "---"  # 'ref' | 'live' | 'both'
        self.run_count = 1  # Run count for controlling step switching

        # Parameters
        self.window_size = params["c"]
        self.max_run_count = params["max_run_count"]
        self.diag_weight = params["diag_weight"]

        self.last_ref_index = 0  # Track the last reference index to prevent backward steps
        self.path_z = []  # Chosen path for debugging or tracking

    def insert(self, live_input: np.ndarray) -> int:
        """
        Insert a new live input frame (chroma vector) and estimate the current position 
        in the reference time series.

        Parameters
        ----------
        live_input : np.ndarray
            Live chroma vector.

        Returns
        -------
        int
            Estimated position in the reference sequence.
        """
        self.live_index += 1
        self.live[:, self.live_index] = live_input

        for k in range(max(0, self.ref_index - self.window_size + 1), self.ref_index + 1):
            self._update_accumulated_cost(k, self.live_index)

        path = []
        while True:
            step, path_point = self._get_best_step()
            path.append(path_point)

            if step == "live":
                break  # Stop if the best step is to move in the live sequence

            # Increment reference index, but keep it in bounds
            self.ref_index = min(self.ref_index + 1, self.ref_len - 1)

            # calculate a new reference column
            for k in range(max(self.live_index - self.window_size + 1, 0), self.live_index + 1):
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
        Determines the best step (ref, live, or both) based on the accumulated cost matrix.

        Returns
        -------
        step : str
            The best step, which can be 'ref', 'live', or 'both'.
        indices : Tuple[int, int]
            The corresponding indices for the best step in the accumulated cost matrix.
        """

        row_costs = self.accumulated_cost[self.ref_index,
                                          : self.live_index + 1]
        col_costs = self.accumulated_cost[: self.ref_index +
                                          1, self.live_index]

        best_t = np.argmin(row_costs)
        best_j = np.argmin(col_costs)

        # Check if the best step is to move in the live sequence
        if self.accumulated_cost[best_j, self.live_index] < self.accumulated_cost[self.ref_index, best_t]:
            best_t = self.live_index
            step = "live"
        else:
            best_j = self.ref_index
            step = "ref"
        # elif self.accumulated_cost[best_j, self.live_index] > self.accumulated_cost[self.ref_index, best_t]:  # Otherwise, move in the reference sequence
        #     best_j = self.ref_index
        #     step = "ref"
        # else:
        #     best_t = self.live_index
        #     best_j = self.ref_index
        #     step = "both"

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
        Updates the accumulated cost matrix at the given indices using the cost function.
        Parameters
        ----------
        ref_index : int
            The index in the reference sequence.
        live_index : int
            The index in the live sequence.

        Returns
        -------
        None
            This function updates the accumulated cost matrix in place and does not return any value.

        Notes
        -----
        The accumulated cost matrix is updated based on the minimum cost path from the previous indices.
        The cost is computed as `1 - dot_product(ref[:, ref_index], live[:, live_index])`.
        The function considers three possible steps: diagonal, vertical, and horizontal, and chooses the one with the minimum cost.
        """
        cost = 1 - np.dot(self.ref[:, ref_index], self.live[:, live_index])

        if ref_index == 0 and live_index == 0:
            self.accumulated_cost[ref_index, live_index] = cost
            return

        steps = []

        # Calculate the cost of moving diagonally, vertically, and horizontally
        if ref_index > 0 and live_index > 0:
            steps.append(
                self.accumulated_cost[ref_index - 1, live_index - 1] + self.diag_weight * cost)
        if ref_index > 0:
            steps.append(
                self.accumulated_cost[ref_index - 1, live_index] + cost)
        if live_index > 0:
            steps.append(
                self.accumulated_cost[ref_index, live_index - 1] + cost)
        self.accumulated_cost[ref_index, live_index] = min(steps)


if __name__ == '__main__':
    # Example usage
    ref = np.random.rand(12, 20)  # Example reference sequence
    # Normalize each column of the reference sequence
    ref = ref / np.linalg.norm(ref, axis=0, keepdims=True)
    params = {
        "c": 5,
        "max_run_count": 3,
        "diag_weight": 2
    }
    otw = OnlineTimeWarping(ref, params)

    live_input = ref  # Example live input
    for col in range(ref.shape[1] - 2):
        live_input = ref[:, col + 2]
        estimated_position = otw.insert(live_input)
        print(estimated_position, end=" ")
    # print(f"Estimated position in reference sequence: {estimated_position}")
