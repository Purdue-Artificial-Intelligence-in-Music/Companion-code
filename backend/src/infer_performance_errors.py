from .alignment_eval_tools import calculate_warped_times
import librosa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
import os
from datetime import datetime

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

SAMPLE_RATE = config.get("sample_rate")
CHANNELS = config.get("channels", 1)
REF_TEMPO = config.get("ref_tempo")

YIN_FRAME_LEN = 512
HOP_LENGTH = 512

FEATURE_NAME = config.get("feature_type", "CENS")

def extract_pyin(waveform):
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

def pitch_at_sample(pitches: list, sample: int):
    window_idx = sample // HOP_LENGTH
    print(len(pitches), window_idx, pitches[window_idx])
    return pitches[window_idx]

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

    ref_pyin = extract_pyin(ref_waveform)
    live_pyin = extract_pyin(live_waveform)

    ref_samples = (eval_df["baseline time"] * SAMPLE_RATE).astype(int)
    warp_samples = (eval_df["predicted live time"] * SAMPLE_RATE).astype(int)
    live_samples = (eval_df["live time"] * SAMPLE_RATE).astype(int)
    
    eval_df["ref note"] = list(map(lambda x: pitch_at_sample(ref_pyin["pyin_midi"], x), ref_samples))
    eval_df["warp note"] = list(map(lambda x: pitch_at_sample(live_pyin["pyin_midi"], x), warp_samples))
    eval_df["live note"] = list(map(lambda x: pitch_at_sample(live_pyin["pyin_midi"], x), live_samples))

    pd.set_option("display.max_rows", None)
    print(eval_df)

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
            eval_df["baseline time"] * SAMPLE_RATE,
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
        ax3.set_title("Score Notes over Baseline Time")
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
