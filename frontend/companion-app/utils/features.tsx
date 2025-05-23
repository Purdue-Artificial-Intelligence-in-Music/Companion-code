/*
Copyright (c) 2024 Matthew Caren

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

// TypeScript conversion of features.py for chroma extraction
// =========================================================
// This module provides functionality to compute CENS chroma features from audio, 
// equivalent to the Python implementation in features.py. 
// It includes pitch frequency calculation, spectrogram-to-pitch conversion matrix, 
// a ChromaMaker class for streaming chroma calculation, and functions to process 
// whole audio or files into np-CENS chromagrams.

// Required dependencies (to install via npm):
//  - node-wav (to decode WAV files to PCM data)
//  - wave-resampler (to resample audio if needed)
//  - fft-js (for FFT computation on audio frames)

// Import necessary modules
// const fs = require('fs');
const wav = require('node-wav');
const waveResampler = require('wave-resampler');
const { fft } = require('fft-js');
import * as FileSystem from 'expo-file-system';
import { Buffer } from 'buffer';

/**
 * Equivalent to Python function pitch_freqs.
 * Returns the center frequency for each MIDI pitch in the range [start_pitch, end_pitch).
 * @param start_pitch - starting MIDI pitch (inclusive)
 * @param end_pitch - one more than the last MIDI pitch value (exclusive)
 * @returns Array of length (end_pitch - start_pitch) with frequencies in Hz.
 */
function pitch_freqs(start_pitch: number = 0, end_pitch: number = 128): number[] {
    const kTRT = Math.pow(2, 1/12.0);  // 2^(1/12)
    const freqs: number[] = [];
    for (let p = start_pitch; p < end_pitch; p += 1) {
        // Calculate frequency for MIDI pitch p (A4=69 -> 440 Hz)
        const freq = 440 * Math.pow(kTRT, p - 69);
        freqs.push(freq);
    }
    return freqs;
}

/**
 * Equivalent to Python function spec_to_pitch_mtx.
 * Create a conversion matrix from an FFT spectrum vector to a MIDI pitch vector (log-frequency spectrogram).
 * 
 * @param fs - sample rate of the audio
 * @param fft_len - the length of the FFT
 * @param tuning - optional pitch adjustment in semitones (MIDI) for alternate tunings (default 0)
 * @returns A matrix of shape (128, num_bins) where num_bins = fft_len//2 + 1 (number of frequency bins in rfft output).
 * Each row corresponds to a MIDI pitch (0-127) and each column to an FFT bin, representing the contribution of that bin's frequency to the given pitch.
 */
function spec_to_pitch_mtx(fs: number, fft_len: number, tuning: number = 0.0): number[][] {
    const num_bins = Math.floor(fft_len / 2) + 1;
    // Initialize output matrix 128 x num_bins with zeros
    const out: number[][] = Array.from({ length: 128 }, () => new Array(num_bins).fill(0));

    // Frequencies for each FFT bin (from 0 to Nyquist)
    const bin_f: number[] = [];
    for (let i = 0; i < num_bins; i++) {
        bin_f.push(i * fs / fft_len);
    }

    // Frequency center for each MIDI pitch 0-127 (with tuning offset) and edges for each pitch band
    const pitch_center = pitch_freqs(0 + tuning, 128 + tuning);
    const pitch_edges = pitch_freqs(-0.5 + tuning, 128.5 + tuning);

    // Precompute a Hann window of length 128 (for distributing bin contributions across pitch frequencies)
    const windowLength = 128;
    const hann: number[] = new Array(windowLength);
    for (let i = 0; i < windowLength; i++) {
        // Hann (Hanning) window formula
        hann[i] = 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / (windowLength - 1));
    }

    // Fill the conversion matrix
    for (let p = 0; p < 128; p++) {
        const f1 = pitch_edges[p];
        const f3 = pitch_edges[p + 1];
        for (let j = 0; j < num_bins; j++) {
            const x = bin_f[j];
            let value: number;
            if (x <= f1 || x >= f3) {
                // Outside the pitch band - assign 0 (Hann window is zero at edges)
                value = 0;
            } else {
                // Linearly interpolate the Hann window value at frequency x between f1 and f3
                const fraction = (x - f1) / (f3 - f1);
                const idx = fraction * (windowLength - 1);
                const i0 = Math.floor(idx);
                const frac = idx - i0;
                // Ensure index is within [0, windowLength-2] for interpolation
                if (i0 >= windowLength - 1) {
                    // If x is extremely close to f3 (fraction ~1), just use last value
                    value = hann[windowLength - 1];
                } else {
                    value = hann[i0] + frac * (hann[i0 + 1] - hann[i0]);
                }
            }
            out[p][j] = value;
        }
    }
    return out;
}

/**
 * Class equivalent to Python class ChromaMaker.
 * Streaming implementation to convert audio frames (of length n_fft) into 12-dimensional CENS chroma vectors.
 * Initialize with sample rate `sr` and FFT length `n_fft`. Then call `insert(y)` where y is an audio buffer of length n_fft.
 */
class ChromaMaker {
    sr: number;
    n_fft: number;
    window: number[];
    c_fc: number[][];  // conversion matrix from FFT bins to chroma (12) bins

    constructor(sr: number, n_fft: number) {
        // Equivalent to Python ChromaMaker.__init__
        // sr: sample rate, n_fft: FFT length (window size)
        this.sr = sr;
        this.n_fft = n_fft;
        // 1) Create Hann (Hanning) window for FFT
        this.window = new Array(n_fft);
        for (let i = 0; i < n_fft; i++) {
            this.window[i] = 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / (n_fft - 1));
        }
        // 2) Compute frequency-to-pitch conversion matrix (c_fp) for this sr and n_fft
        const tuning = 0.0;
        const c_fp = spec_to_pitch_mtx(this.sr, this.n_fft, tuning);  // shape 128 x (n_fft/2+1)
        // 3) Compute pitch-to-chroma (class) conversion matrix (c_pc)
        //    c_pc is a 12x128 matrix mapping 128 MIDI pitches to 12 pitch classes.
        const c_pc: number[][] = Array.from({ length: 12 }, () => new Array(128).fill(0));
        for (let p = 0; p < 128; p++) {
            const pitch_class = p % 12;
            c_pc[pitch_class][p] = 1;
        }
        // 4) Compute full conversion from FFT bins to chroma: c_fc = c_pc * c_fp (matrix multiply)
        const num_bins = Math.floor(n_fft / 2) + 1;
        this.c_fc = Array.from({ length: 12 }, () => new Array(num_bins).fill(0));
        for (let chroma = 0; chroma < 12; chroma++) {
            for (let j = 0; j < num_bins; j++) {
                let sum = 0;
                // sum over all pitches that map to this chroma class
                for (let pitch = chroma; pitch < 128; pitch += 12) {
                    sum += c_fp[pitch][j];
                }
                this.c_fc[chroma][j] = sum;
            }
        }
    }

    /**
     * Insert a new audio frame and compute its CENS chroma vector.
     * @param y - audio frame of length n_fft (samples)
     * @returns An array of length 12 representing the CENS chroma features for this frame.
     */
    insert(y: Float32Array | number[]): number[] {
        // Equivalent to Python ChromaMaker.insert
        if (y.length !== this.n_fft) {
            throw new Error(`Input frame length ${y.length} does not match expected length ${this.n_fft}.`);
        }
        // 1) Apply Hann window to the audio frame
        const sig = new Array(this.n_fft);
        for (let i = 0; i < this.n_fft; i++) {
            sig[i] = (y as any)[i] * this.window[i];
        }
        // 2) Compute magnitude spectrum using FFT (real FFT since input is real)
        // Use fft-js to compute FFT. It returns an array of [real, imag] pairs.
        const phasors = fft(sig);
        const num_bins = Math.floor(this.n_fft / 2) + 1;
        // Take the magnitude (absolute value) of FFT output for bins 0..num_bins-1
        const X: number[] = new Array(num_bins);
        for (let k = 0; k < num_bins; k++) {
            const re = phasors[k][0];
            const im = phasors[k][1];
            X[k] = Math.sqrt(re * re + im * im);
        }
        // Convert to chroma by projecting the power spectrum onto pitch classes:
        // We use X**2 (power) for projection (as in Python code X**2).
        const chromaVec: number[] = new Array(12).fill(0);
        for (let i = 0; i < 12; i++) {
            let sum = 0;
            for (let j = 0; j < num_bins; j++) {
                // use power = X[j]^2
                sum += this.c_fc[i][j] * (X[j] * X[j]);
            }
            chromaVec[i] = sum;
        }

        // CENS post-processing steps:
        // Step 1) Normalize by L1 norm (sum of absolute values)
        let L1 = 0;
        for (let i = 0; i < 12; i++) {
            L1 += Math.abs(chromaVec[i]);
        }
        if (L1 === 0) {
            // if all zeros, set each to 1 (to avoid division by zero)
            chromaVec.fill(1);
            L1 = 12;
        }
        for (let i = 0; i < 12; i++) {
            chromaVec[i] /= L1;
        }

        // Step 2) Quantize according to a logarithmic scheme (resulting values 0–4)
        const quantized: number[] = new Array(12).fill(0);
        const values = [1, 2, 3, 4];
        const thresholds = [0.05, 0.1, 0.2, 0.4, 1.0];
        for (let idx = 0; idx < values.length; idx++) {
            const v = values[idx];
            const lower = thresholds[idx];
            const upper = thresholds[idx + 1];
            for (let i = 0; i < 12; i++) {
                if (chromaVec[i] > lower && chromaVec[i] <= upper) {
                    quantized[i] = v;
                }
            }
        }
        // Any chroma value <= 0.05 remains 0 in quantized (above loop doesn't set it)

        // Step 3) (Optional smoothing step would be here - omitted as in Python code)

        // Step 4) Normalize by L2 norm
        let L2 = 0;
        for (let i = 0; i < 12; i++) {
            L2 += quantized[i] * quantized[i];
        }
        L2 = Math.sqrt(L2);
        if (L2 === 0) {
            // if all zero (shouldn't happen after step 1 unless all were exactly 0),
            // set each to 1 (so each value is 1) and adjust L2 to sqrt(12)
            quantized.fill(1);
            L2 = Math.sqrt(12);
        }
        const chromaNorm: number[] = new Array(12);
        for (let i = 0; i < 12; i++) {
            chromaNorm[i] = quantized[i] / L2;
        }
        return chromaNorm;
    }
}

/**
 * Convert an entire audio signal to an np-CENS chromagram (12 x M matrix).
 * Equivalent to Python function audio_to_np_cens.
 * 
 * @param y - audio samples (mono) as Float32Array or number[].
 * @param sr - sample rate of the audio.
 * @param n_fft - FFT window size to use for frames.
 * @param hop_len - hop length (stride) in samples between successive frames.
 * @returns A 2D array of shape [12][M], where M is the number of chroma vectors (frames).
 */
function audio_to_np_cens(y: Float32Array | number[], sr: number, n_fft: number, hop_len: number): number[][] {
    // Calculate number of full frames of length n_fft that fit in the signal with given hop length
    const M = Math.floor((y.length - n_fft) / hop_len) + 1;
    const chromagram: number[][] = Array.from({ length: 12 }, () => new Array(M).fill(0));
    const cm = new ChromaMaker(sr, n_fft);
    // Process each frame
    for (let m = 0; m < M; m++) {
        const start = m * hop_len;
        const frame = (y instanceof Float32Array) 
                        ? y.subarray(start, start + n_fft) 
                        : (y as number[]).slice(start, start + n_fft);
        const chromaVec = cm.insert(frame);
        for (let i = 0; i < 12; i++) {
            chromagram[i][m] = chromaVec[i];
        }
    }
    return chromagram;
}

/**
 * Load an audio file and convert it to an np-CENS chromagram.
 * Equivalent to Python function file_to_np_cens.
 * 
 * @param filepath - path to the audio file (WAV format expected).
 * @param params - object containing parameters: 
 *        { sr: desired sample rate (Hz), n_fft: FFT length, ref_hop_len: hop length in samples }.
 * @returns A 12 x M chromagram matrix as a 2D array of numbers.
 */
async function file_to_np_cens(
    fileUri: string,
    params: { sr: number; n_fft: number; ref_hop_len: number }
  ): Promise<number[][]> {
    // Verify the file exists
    const info = await FileSystem.getInfoAsync(fileUri, { size: true });
    if (!info.exists) {
      throw new Error(`File not found at ${fileUri}`);
    }
  
    // Read the file as a Base64‑encoded string
    const base64 = await FileSystem.readAsStringAsync(fileUri, {
      encoding: FileSystem.EncodingType.Base64
    });
    const buffer = Buffer.from(base64, 'base64');
  
    // Decode WAV buffer
    const result = wav.decode(buffer.buffer as ArrayBuffer);
    let audioData = result.channelData[0];
  
    // Convert to mono if needed
    if (result.channelData.length > 1) {
      const numCh = result.channelData.length;
      const len = audioData.length;
      const mono = new Float32Array(len);
      for (let i = 0; i < len; i++) {
        let sum = 0;
        for (let ch = 0; ch < numCh; ch++) sum += result.channelData[ch][i];
        mono[i] = sum / numCh;
      }
      audioData = mono;
    }
  
    // Resample if sample rates differ
    if (result.sampleRate !== params.sr) {
      const resampled = waveResampler.resample(
        audioData,
        result.sampleRate,
        params.sr
      );
      audioData =
        resampled instanceof Float32Array
          ? resampled
          : Float32Array.from(resampled as number[]);
    }
  
    // Compute and return the chromagram
    return audio_to_np_cens(
      audioData,
      params.sr,
      params.n_fft,
      params.ref_hop_len
    );
  }
  

// Export functions and class for external use
export { pitch_freqs, spec_to_pitch_mtx, ChromaMaker, audio_to_np_cens, file_to_np_cens };
