from .alignment_eval_tools import calculate_warped_times
import librosa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
import matplotlib.ticker as ticker
import os
from datetime import datetime

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

SAMPLE_RATE = config.get("sample_rate")
CHANNELS = config.get("channels", 1)
WIN_LENGTH = config.get("win_length")
HOP_LENGTH = config.get("hop_length", WIN_LENGTH)
REF_TEMPO = config.get("ref_tempo")

FEATURE_NAME = config.get("feature_type", "CENS")

YIN_FRAME_LEN = HOP_LENGTH * 2


def evaluate_intonation(
    eval_df: pd.DataFrame,
    path_ref_wav: str,
    path_live_wav: str,
    plot: bool,
    path_log_folder: str,
):
    def extract_yin_and_pyin(waveform):
        f0_yin = librosa.yin(
            waveform,
            sr=SAMPLE_RATE,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            frame_length=YIN_FRAME_LEN,
            hop_length=HOP_LENGTH,
            center=False,
        )
        f0_yin_midi = librosa.hz_to_midi(f0_yin)[0]
        valid_yin = ~np.isnan(f0_yin_midi)
        sample_idx_yin = np.arange(len(f0_yin_midi)) * HOP_LENGTH

        f0_pyin, _, _ = librosa.pyin(
            waveform,
            sr=SAMPLE_RATE,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            frame_length=YIN_FRAME_LEN,
            hop_length=HOP_LENGTH,
            center=False,
        )
        f0_pyin_midi = librosa.hz_to_midi(f0_pyin)[0]
        valid_pyin = ~np.isnan(f0_pyin_midi)
        sample_idx_pyin = np.arange(len(f0_pyin_midi)) * HOP_LENGTH

        return {
            "yin_midi": f0_yin_midi,
            "yin_valid": valid_yin,
            "yin_idx": sample_idx_yin,
            "pyin_midi": f0_pyin_midi,
            "pyin_valid": valid_pyin,
            "pyin_idx": sample_idx_pyin,
        }

    def extract_pitch_at_samples(waveform, sample_list):
        pitches = []
        for sample in sample_list:
            segment = waveform[:, sample : sample + YIN_FRAME_LEN]
            f0_vec = librosa.yin(
                segment,
                sr=SAMPLE_RATE,
                fmin=librosa.note_to_hz("C2"),
                fmax=librosa.note_to_hz("C7"),
                frame_length=YIN_FRAME_LEN,
                hop_length=HOP_LENGTH,
                center=False,
            )
            pitch = librosa.hz_to_midi(f0_vec[0][0])
            pitches.append(pitch)
        return pitches

    ref_waveform, _ = librosa.load(path_ref_wav, sr=SAMPLE_RATE)
    ref_waveform = ref_waveform.reshape((CHANNELS, -1))  # reshape audio to 2D array
    live_waveform, _ = librosa.load(path_live_wav, sr=SAMPLE_RATE)
    live_waveform = live_waveform.reshape((CHANNELS, -1))  # reshape audio to 2D array

    ref_pitch = extract_yin_and_pyin(ref_waveform)
    live_pitch = extract_yin_and_pyin(live_waveform)

    ref_samples = (eval_df["baseline time"] * SAMPLE_RATE).astype(int)
    live_samples = (eval_df["predicted live time"] * SAMPLE_RATE).astype(int)

    eval_df["ref note"] = extract_pitch_at_samples(ref_waveform, ref_samples)
    eval_df["predicted live note"] = extract_pitch_at_samples(
        live_waveform, live_samples
    )

    pd.set_option("display.max_rows", None)
    print(eval_df)

    if plot:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
        fig.suptitle("YIN vs pYIN Pitch Estimation (Live vs Reference)", fontsize=16)
        fig.suptitle(
            f"YIN vs pYIN Pitch Estimation + Points from {FEATURE_NAME} Alignment:\n{path_ref_wav} VS {path_live_wav}",
            fontsize=14,
        )

        # Top: Reference waveform pitch
        ax1.plot(
            ref_pitch["yin_idx"][ref_pitch["yin_valid"]],
            ref_pitch["yin_midi"][ref_pitch["yin_valid"]],
            color="orange",
            linewidth=1,
            label="Ref YIN $f_0$",
        )
        ax1.plot(
            ref_pitch["pyin_idx"][ref_pitch["pyin_valid"]],
            ref_pitch["pyin_midi"][ref_pitch["pyin_valid"]],
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
            live_pitch["yin_idx"][live_pitch["yin_valid"]],
            live_pitch["yin_midi"][live_pitch["yin_valid"]],
            color="orange",
            linewidth=1,
            label="Live YIN $f_0$",
        )
        ax2.plot(
            live_pitch["pyin_idx"][live_pitch["pyin_valid"]],
            live_pitch["pyin_midi"][live_pitch["pyin_valid"]],
            color="purple",
            linestyle="--",
            linewidth=1,
            alpha=0.7,
            label="Live pYIN $f_0$",
        )
        ax2.scatter(
            live_samples,
            eval_df["predicted live note"],
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

        # Format shared x-axis
        ax3.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x)}"))
        ax3.xaxis.set_major_locator(ticker.MultipleLocator(HOP_LENGTH * 5))

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

    return eval_df, ref_pitch, live_pitch
