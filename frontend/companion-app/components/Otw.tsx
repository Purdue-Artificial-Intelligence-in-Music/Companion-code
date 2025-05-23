/*
Copyright (c) 2024 Matthew Caren

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

/**
 * OnlineTimeWarping implements Online Time Warping [1], adapted for TypeScript as a streaming algorithm.
 *
 * [1] Simon Dixon: "Live Tracking of Musical Performances Using On-Line Time Warping".
 */

interface Dictionary<T> {
    [key: string]: T;
}

function dot(ref: number[][], live: number[][], refIdx: number, liveIdx: number): number {
    let sum = 0;
    for (let i = 0; i < ref.length; i++) {
    sum += ref[i][refIdx] * live[i][liveIdx];
    }
    return sum;
}

function argmin(arr: number[]): number {
    return arr.reduce((minIdx, val, idx, a) => (val < a[minIdx] ? idx : minIdx), 0);
}

class OnlineTimeWarping {
    ref: number[][];  // Reference sequence (assumed chroma)
    feature_len: number;  // Length of the feature dimension
    ref_len: number;  // Length of the reference sequence
    live: number[][];  // Live input sequence initialized with zeros
    accumulated_cost: number[][];  // Accumulated cost matrix initialized with Infinity
    live_index: number;
    ref_index: number;
    previous_step: string;  // 'ref' | 'live' | 'both'
    run_count: number;
    window_size: number;
    max_run_count: number;
    diag_weight: number;
    last_ref_index: number;
    path_z: number[];  // Chosen path for debugging or tracking

    constructor(ref: number[][], params: Dictionary<number>) {
    this.ref = ref;
    this.feature_len = ref.length;
    this.ref_len = ref[0].length;

    this.live = Array.from({ length: this.feature_len }, () => new Array(this.ref_len * 4).fill(0));
    this.accumulated_cost = Array.from({ length: this.ref_len }, () => new Array(this.ref_len * 4).fill(Infinity));

    this.live_index = -1;
    this.ref_index = 0;
    this.previous_step = "---";
    this.run_count = 1;

    this.window_size = params["c"];
    this.max_run_count = params["max_run_count"];
    this.diag_weight = params["diag_weight"];

    this.last_ref_index = 0;
    this.path_z = [];
    }

    /**
     * Insert a new live input frame (chroma vector) and estimate the current position in the reference time series.
     * @param live_input - Live chroma vector as number[]
     * @returns Estimated position in the reference sequence
     */
    insert(live_input: number[]): number {
    this.live_index += 1;

    for (let i = 0; i < this.feature_len; i++) {
        this.live[i][this.live_index] = live_input[i];
    }

    for (let k = Math.max(0, this.ref_index - this.window_size + 1); k <= this.ref_index; k++) {
        this._update_accumulated_cost(k, this.live_index);
    }

    const path: [number, number][] = [];

    while (true) {
        const [step, path_point] = this._get_best_step();
        path.push(path_point);

        if (step === "live") break;

        this.ref_index = Math.min(this.ref_index + 1, this.ref_len - 1);

        for (let k = Math.max(this.live_index - this.window_size + 1, 0); k <= this.live_index; k++) {
        this._update_accumulated_cost(this.ref_index, k);
        }

        if (step === "both") break;
    }

    let current_ref_position = path[path.length - 1][0];
    this.path_z.push(current_ref_position);

    if (current_ref_position < this.last_ref_index) {
        current_ref_position = this.last_ref_index;
    }

    this.last_ref_index = current_ref_position;
    return current_ref_position;
    }

    /**
     * Determines the best step (ref, live, or both) based on the accumulated cost matrix.
     * @returns A tuple containing the best step and the indices [ref_idx, live_idx].
     */
    private _get_best_step(): [string, [number, number]] {
    const row_costs = this.accumulated_cost[this.ref_index].slice(0, this.live_index + 1);
    const col_costs = this.accumulated_cost.map(row => row[this.live_index]).slice(0, this.ref_index + 1);

    let best_t = argmin(row_costs);
    let best_j = argmin(col_costs);
    let step: string;

    if (this.accumulated_cost[best_j][this.live_index] < this.accumulated_cost[this.ref_index][best_t]) {
        best_t = this.live_index;
        step = "live";
    } else if (this.accumulated_cost[best_j][this.live_index] > this.accumulated_cost[this.ref_index][best_t]) {
        best_j = this.ref_index;
        step = "ref";
    } else {
        best_t = this.live_index;
        best_j = this.ref_index;
        step = "both";
    }

    if (best_t === this.live_index && best_j === this.ref_index) step = "both";
    if (this.live_index < this.window_size) step = "both";
    if (this.run_count >= this.max_run_count) step = this.previous_step === "ref" ? "live" : "ref";

    if (step === "both" || this.previous_step !== step) {
        this.run_count = 1;
    } else {
        this.run_count += 1;
    }

    this.previous_step = step;
    if (this.ref_index === this.ref_len - 1) step = "live";

    return [step, [best_j, best_t]];
    }

    /**
     * Updates the accumulated cost matrix at the given indices using the cost function.
     * The cost is computed as `1 - dot(ref[:, ref_index], live[:, live_index])`.
     * Considers diagonal, vertical, and horizontal transitions.
     * @param ref_index - Index in the reference sequence
     * @param live_index - Index in the live sequence
     */
    private _update_accumulated_cost(ref_index: number, live_index: number): void {
    const cost = 1 - dot(this.ref, this.live, ref_index, live_index);

    if (ref_index === 0 && live_index === 0) {
        this.accumulated_cost[ref_index][live_index] = cost;
        return;
    }

    const steps: number[] = [];

    if (ref_index > 0 && live_index > 0) {
        steps.push(this.accumulated_cost[ref_index - 1][live_index - 1] + this.diag_weight * cost);
    }
    if (ref_index > 0) {
        steps.push(this.accumulated_cost[ref_index - 1][live_index] + cost);
    }
    if (live_index > 0) {
        steps.push(this.accumulated_cost[ref_index][live_index - 1] + cost);
    }

    this.accumulated_cost[ref_index][live_index] = Math.min(...steps);
    }
}

export default OnlineTimeWarping;