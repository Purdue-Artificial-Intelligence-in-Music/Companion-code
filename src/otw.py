"""
Copyright (c) 2024 Matthew Caren

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import numpy as np
from typing import Dict, Tuple

def find_key(d: Dict, k: str):
    """Returns the value of key `k` in dictionary `d`, or None if key is not found."""
    return d.get(k)


class OnlineTimeWarping:
    """
    Implements Online Time Warping [1], adapted for Python as a streaming algorithm 
    with a few modifications for clarity.

    Parameters:
    - ref: np.ndarray - Reference time series (assumed chroma).
    - params: Dict - Dictionary of configuration parameters.

    [1] Simon Dixon: "Live Tracking of Musical Performances Using On-Line Time Warping".
    """
    def __init__(self, ref: np.ndarray, params: Dict[str, float]):
        self.ref = ref  # Reference sequence (assumed chroma)
        self.feature_len, self.ref_len = self.ref.shape
        self.live = np.zeros((self.feature_len, self.ref_len * 4), dtype=np.float32)  # Live input
        self.accumulated_cost = np.full((self.ref_len, self.ref_len * 4), np.inf, dtype=np.float32)

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

        - live_input: np.ndarray - Live chroma vector.
        Returns:
        - int: Estimated position in the reference sequence.
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
                break

            self.ref_index = min(self.ref_index + 1, self.ref_len - 1)
            for k in range(max(self.live_index - self.window_size + 1, 0), self.live_index + 1):
                self._update_accumulated_cost(self.ref_index, k)

            if step == "both":
                break

        current_ref_position = path[-1][0]
        self.path_z.append(current_ref_position)

        if current_ref_position < self.last_ref_index:
            current_ref_position = self.last_ref_index

        self.last_ref_index = current_ref_position
        return current_ref_position

    def _get_best_step(self) -> Tuple[str, Tuple[int, int]]:
        """
        Determines the best step (ref, live, or both) based on the accumulated cost matrix.
        Returns:
        - Tuple[str, Tuple[int, int]]: Best step ('ref', 'live', or 'both') and corresponding indices.
        """
        row_costs = self.accumulated_cost[self.ref_index, : self.live_index + 1]
        col_costs = self.accumulated_cost[: self.ref_index + 1, self.live_index]

        best_t = np.argmin(row_costs)
        best_j = np.argmin(col_costs)

        if self.accumulated_cost[best_j, self.live_index] < self.accumulated_cost[self.ref_index, best_t]:
            best_t = self.live_index
            step = "live"
        else:
            best_j = self.ref_index
            step = "ref"

        if best_t == self.live_index and best_j == self.ref_index:
            step = "both"

        if self.live_index < self.window_size:
            step = "both"

        if self.run_count >= self.max_run_count:
            step = "live" if self.previous_step == "ref" else "ref"

        if step == "both" or self.previous_step != step:
            self.run_count = 1
        else:
            self.run_count += 1

        self.previous_step = step

        if self.ref_index == self.ref_len - 1:
            step = "live"

        return step, (best_j, best_t)

    def _update_accumulated_cost(self, ref_index: int, live_index: int):
        """
        Updates the accumulated cost matrix at the given indices using the cost function.
        """
        cost = 1 - np.dot(self.ref[:, ref_index], self.live[:, live_index])

        if ref_index == 0 and live_index == 0:
            self.accumulated_cost[ref_index, live_index] = cost
            return

        steps = []
        if ref_index > 0 and live_index > 0:
            steps.append(self.accumulated_cost[ref_index - 1, live_index - 1] + self.diag_weight * cost)
        if ref_index > 0:
            steps.append(self.accumulated_cost[ref_index - 1, live_index] + cost)
        if live_index > 0:
            steps.append(self.accumulated_cost[ref_index, live_index - 1] + cost)

        self.accumulated_cost[ref_index, live_index] = min(steps)
