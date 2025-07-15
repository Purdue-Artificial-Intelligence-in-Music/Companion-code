from .alignment_eval_tools import calculate_warped_times
import librosa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
import os
from datetime import datetime
from typing import List

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

SAMPLE_RATE = config.get("sample_rate")
CHANNELS = config.get("channels", 1)
REF_TEMPO = config.get("ref_tempo")

YIN_FRAME_LEN = 1024
HOP_LENGTH = 512

FEATURE_NAME = config.get("feature_type", "CENS")

def _extract_pyin(waveform):
    f0_pyin, _, _ = librosa.pyin(
        waveform,
        sr=SAMPLE_RATE,
        fmin=librosa.note_to_hz("C2"), # type: ignore
        fmax=librosa.note_to_hz("C7"), # type: ignore
        frame_length=YIN_FRAME_LEN,
        hop_length=HOP_LENGTH,
        center=False,
    )
    f0_pyin_midi = librosa.hz_to_midi(f0_pyin)[0]
    valid_pyin = ~np.isnan(f0_pyin_midi)
    sample_idx_pyin = np.arange(len(f0_pyin_midi)) * HOP_LENGTH

    return {
        "pyin_midi": f0_pyin_midi,
        "pyin_valid": valid_pyin,
        "pyin_idx": sample_idx_pyin,
    }

def _pitches_at_timestamps(ts_list, pitch_per_window: List[float]):
    # Convert timestamp -> sample no., sample no. -> window no. using hop len
    _windows = [int(ts * SAMPLE_RATE) // HOP_LENGTH for ts in ts_list]
    pitches = []

    for idx in range(0, len(ts_list)):
        window = _windows[idx]
        aggregate_len = 10

        if idx + 1 < len(_windows):
            nxt_win_num = _windows[idx + 1]
            aggregate_len = (nxt_win_num - window) // 2
        if window + aggregate_len > len(pitch_per_window):
            aggregate_len = len(pitch_per_window) - window
        
        aggregate = pitch_per_window[window:window+aggregate_len]
        aggregate = [x for x in aggregate if x is not None and not np.isnan(x)]
        
        pitch = np.median(aggregate)
        print(f"Pitch #{idx}: Window num: {window} -> Direct Pitch: {pitch_per_window[window]}")
        print(f"Median {pitch}, Aggr {aggregate}")
        # print(f"... Aggregate length {aggregate_len}, Median /{pitch}")

        pitches.append(pitch)

    return pitches

def evaluate_intonation(
    eval_df: pd.DataFrame,
    path_ref_wav: str,
    path_live_wav: str,
    plot: bool,
    path_log_folder: str,
):

    ref_waveform, _ = librosa.load(path_ref_wav, sr=SAMPLE_RATE)
    ref_waveform = ref_waveform.reshape((CHANNELS, -1))  # reshape audio to 2D array
    live_waveform, _ = librosa.load(path_live_wav, sr=SAMPLE_RATE)
    live_waveform = live_waveform.reshape((CHANNELS, -1))  # reshape audio to 2D array

    ref_pyin = _extract_pyin(ref_waveform)
    live_pyin = _extract_pyin(live_waveform)
    
    eval_df["ref note"] = _pitches_at_timestamps(eval_df["ref_ts"], ref_pyin["pyin_midi"])
    eval_df["warp note"] = _pitches_at_timestamps(eval_df["warp_ts"], live_pyin["pyin_midi"])
    eval_df["live note"] = _pitches_at_timestamps(eval_df["live_ts"], live_pyin["pyin_midi"])

    pd.set_option("display.max_rows", None)
    print(eval_df)

    ref_samples = (eval_df["ref_ts"] * SAMPLE_RATE).astype(int)
    live_samples = (eval_df["live_ts"] * SAMPLE_RATE).astype(int)

    if plot:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
        fig.suptitle("pYIN Pitch Estimation (Live vs Reference)", fontsize=16)
        fig.suptitle(
            f"pYIN Pitch Estimation + Points from {FEATURE_NAME} Alignment:\n{path_ref_wav} VS {path_live_wav}\n"
            + f"Frame length: {YIN_FRAME_LEN}, hop length: {HOP_LENGTH}",
            fontsize=14,
        )

        # Top: Reference waveform pitch
        ax1.plot(
            ref_pyin["pyin_idx"][ref_pyin["pyin_valid"]],
            ref_pyin["pyin_midi"][ref_pyin["pyin_valid"]],
            color="purple",
            linestyle="--",
            linewidth=1,
            alpha=0.7,
            label="Ref pYIN $f_0$",
        )
        ax1.scatter(
            ref_samples,
            eval_df["ref note"],
            color="black",
            s=5,
            label="DTW Ref Points",
            zorder=3,
        )
        ax1.set_ylabel("MIDI Note (Ref)")
        ax1.set_title(f"Reference ({path_ref_wav}) Pitch")
        ax1.grid(True, linestyle="--", alpha=0.6)
        ax1.legend()

        # Middle: Live waveform pitch
        ax2.plot(
            live_pyin["pyin_idx"][live_pyin["pyin_valid"]],
            live_pyin["pyin_midi"][live_pyin["pyin_valid"]],
            color="purple",
            linestyle="--",
            linewidth=1,
            alpha=0.7,
            label="Live pYIN $f_0$",
        )
        ax2.scatter(
            live_samples,
            eval_df["warp note"],
            color="black",
            s=5,
            label="DTW Live Points",
            zorder=3,
        )
        ax2.set_ylabel("MIDI Note (Live)")
        ax2.set_title(f"Live {path_live_wav} Pitch")
        ax2.grid(True, linestyle="--", alpha=0.6)
        ax2.legend()

        # Bottom: Note Pitch over Baseline Sample Time
        ax3.plot(
            eval_df["ref_ts"] * SAMPLE_RATE,
            eval_df["note"],
            marker="o",
            linestyle="-",
            color="green",
            label="Score Note (MIDI)",
            markersize=3,
            drawstyle="steps-post",
        )
        ax3.set_ylabel("MIDI Note (Score)")
        ax3.set_xlabel("Sample Index")
        ax3.set_title("Score Notes over ref_ts")
        ax3.grid(True, linestyle="--", alpha=0.6)
        ax3.legend()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(
            0.5,
            0.01,
            f"Generated on {timestamp}",
            ha="center",
            fontsize=9,
            color="gray",
        )

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        save_path = os.path.join(
            path_log_folder, "figures", f"eval_{FEATURE_NAME}_pitch.png"
        )
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        plt.show()

    return eval_df, ref_pyin, live_pyin
