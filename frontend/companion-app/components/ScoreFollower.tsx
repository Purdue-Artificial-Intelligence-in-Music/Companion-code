import OnlineTimeWarping from './Otw';
import { ChromaMaker, file_to_np_cens } from '../utils/features';

/**
 * Performs online dynamic time warping (DTW) between reference audio and live microphone audio.
 */
export class ScoreFollower {
  sampleRate: number;
  winLength: number;
  chromaMaker: ChromaMaker;
  ref: number[][];
  otw: OnlineTimeWarping;
  path: Array<[number, number]>;

  /**
   * @param reference Path to reference audio file
   * @param c Width of online DTW search (default 10)
   * @param maxRunCount Slope constraint for online DTW (default 3)
   * @param diagWeight Diagonal weight for OTW (default 0.4)
   * @param sampleRate Sample rate of the audio buffer (default 44100)
   * @param winLength Number of frames per chroma feature (default 8192)
   */
  constructor(
    reference: string,
    c = 10,
    maxRunCount = 3,
    diagWeight = 0.4,
    sampleRate = 44100,
    winLength = 8192
  ) {
    this.sampleRate = sampleRate;
    this.winLength = winLength;

    // Instantiate ChromaMaker object
    this.chromaMaker = new ChromaMaker(sampleRate, winLength);

    // Params for OTW
    const params = {
      sr: sampleRate,
      n_fft: winLength,
      ref_hop_len: winLength,
      c,
      max_run_count: maxRunCount,
      diag_weight: diagWeight,
    };

    // Load reference sequence of CENS features
    this.ref = file_to_np_cens(reference, params);

    // Initialize OTW object
    this.otw = new OnlineTimeWarping(this.ref, params);

    // Online DTW alignment path
    this.path = [];
  }

  /**
   * Converts audio frames to chroma feature.
   * Pads with zeros if too short.
   * @param audio Audio frames
   * @returns Chroma feature
   */
  private getChroma(audio: number[]): number[] {
    if (audio.length < this.winLength) {
      const padding = Array(this.winLength - audio.length).fill(0);
      audio = audio.concat(padding);
    }
    return this.chromaMaker.insert(audio);
  }

  /**
   * Calculate next step in the alignment path between microphone and reference audio.
   * @param frames Live audio frames
   * @returns Estimated position in the reference audio in seconds
   */
  step(frames: number[]): number {
    const chroma = this.getChroma(frames);
    const refIndex = this.otw.insert(chroma);
    this.path.push([refIndex, this.otw.live_index]);
    return (refIndex * this.winLength) / this.sampleRate;
  }

  /**
   * Retrieves a backward path of given length through the cost matrix.
   * @param b Number of steps to go back
   * @returns Backwards path as list of (refIndex, liveIndex)
   */
  getBackwardsPath(b: number): Array<[number, number]> {
    const costMatrix = this.otw.accumulated_cost;
    let j = this.otw.ref_index;
    let t = this.otw.live_index;
    const backwardsPath: Array<[number, number]> = [];

    while (j > this.otw.ref_index - b && !backwardsPath.includes([0, 0])) {
      const down = costMatrix[j - 1][t];
      const left = costMatrix[j][t - 1];
      const diag = costMatrix[j - 1][t - 1];

      const minimum = Math.min(down, left, diag);

      if (minimum === down) {
        backwardsPath.push([j - 1, t]);
        j -= 1;
      } else if (minimum === left) {
        backwardsPath.push([j, t - 1]);
        t -= 1;
      } else {
        backwardsPath.push([j - 1, t - 1]);
        j -= 1;
        t -= 1;
      }
    }

    return backwardsPath;
  }

  /**
   * Computes the difference between the forward path and a backward path.
   * @param backPath Backwards path
   * @returns Path elements in forward path but not in backPath
   */
  getPathDifference(backPath: Array<[number, number]>): Array<[number, number]> {
    return this.path.filter(([r, l]) => !backPath.some(([br, bl]) => br === r && bl === l));
  }
}