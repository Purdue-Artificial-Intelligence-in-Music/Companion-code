import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import yaml
import os
import json
from datetime import datetime

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

SAMPLE_RATE = config.get("sample_rate")
HOP_LENGTH = config.get("hop_length")
WIN_LENGTH = config.get("win_length")
REF_TEMPO = config.get("ref_tempo")

FEATURE_NAME = config.get("feature_type", "CENS")

STEP_SIZE = HOP_LENGTH / SAMPLE_RATE  # * (REF_TEMPO / 60) for beats

import numpy as np

def calculate_warped_times(warping_path, ref_times):
    step_size = HOP_LENGTH / SAMPLE_RATE
    ref_ts  = warping_path[:,0].astype(float) * step_size
    live_ts = warping_path[:,1].astype(float) * step_size

    order = np.argsort(ref_ts, kind="stable")
    ref_ts  = ref_ts[order]
    live_ts = live_ts[order]

    warp_times = []
    for q in ref_times:
        # Boundary check
        if q <= ref_ts[0]:
            warp_times.append(live_ts[0])
            continue
        if q >= ref_ts[-1]:
            warp_times.append(live_ts[-1])
            continue

        # Find enclosing segment
        right_idx = np.searchsorted(ref_ts, q, side="right")
        left_idx = right_idx - 1

        lRef, rRef = ref_ts[left_idx], ref_ts[right_idx]
        lLive, rLive = live_ts[left_idx], live_ts[right_idx]

        # Interpolate (or clamp if degenerate)
        if rRef == lRef:
            # degenerate / ref stalled
            warp_times.append((lLive+rLive) / 2)
        else:
            alpha = (q - lRef) / (rRef - lRef)
            warp_times.append(lLive + alpha * (rLive - lLive))

    return warp_times


def evaluate_alignment(
    warping_path,
    path_alignment_csv,
    align_col_note,
    align_col_ref,
    align_col_live,
):
    source_df = pd.read_csv(path_alignment_csv)

    warping_path = np.array(warping_path)

    # map each baseline note time to live_ts
    predicted_times = calculate_warped_times(warping_path, source_df[align_col_ref])

    eval_df = pd.DataFrame(
        {
            "note": source_df[align_col_note],
            "ref_ts": source_df[align_col_ref],
            "warp_ts": predicted_times,
            "live_ts": source_df[align_col_live],
        }
    )

    eval_df["alignment error"] = eval_df["warp_ts"] - eval_df["live_ts"]
    eval_df["sequence diff"] = eval_df["live_ts"] - eval_df["ref_ts"]
    return eval_df


def analyze_eval_df(eval_df):
    # pd.set_option("display.max_rows", None)
    # print(eval_df)

    # get smallest error
    min_idx = eval_df["alignment error"].abs().argmin()
    min_dev = eval_df.loc[min_idx, "alignment error"]

    # get largest error
    max_idx = eval_df["alignment error"].abs().argmax()
    max_dev = eval_df.loc[max_idx, "alignment error"]

    print(f"min error: ", {min_dev})
    print(f"max error: ", {max_dev})
    print(f"mean error: ", {eval_df["alignment error"].mean()})
    print(f"median error: ", {eval_df["alignment error"].median()})
    print(f"variance error: ", {eval_df["alignment error"].var()})


def plot_eval_df(
    eval_df, warping_path, acc_cost_matrix, ref_filename, live_filename, feature_name, path_log_folder, 
    override_filename=None
):
    fig = plt.figure(figsize=(15, 12))
    fig.suptitle(
        f"Alignment with {feature_name} Features:\n{ref_filename} VS {live_filename}",
        fontsize=14,
    )

    gs = gridspec.GridSpec(3, 2, figure=fig)

    # Subplot 1: Alignment Error
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(eval_df["alignment error"], label="Alignment Error (s)", color="blue")
    ax1.axhline(y=0, color="r", linestyle="--")
    ax1.set_title("Alignment Error")
    ax1.set_ylabel("Alignment Error (s)")
    ax1.grid(True)

    # Subplot 2: Histogram
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.hist(eval_df["alignment error"], bins=20, edgecolor="black")
    ax2.set_title("Histogram of Alignment Errors")
    ax2.set_ylabel("Frequency")

    # Subplot 3: Baseline vs live_ts
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(eval_df["sequence diff"], label="sequence diff", color="green")
    ax3.set_title("live_ts - ref_ts")
    ax3.set_ylabel("Time (s)")
    ax3.grid(True)

    # Subplot 4: Note Pitch
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.plot(
        eval_df["note"],
        label="Note Pitch (MIDI)",
        color="orange",
        drawstyle="steps-post",
    )
    ax4.set_title("Note Pitch")
    ax4.set_xlabel("Note No.")
    ax4.set_ylabel("Note Pitch (MIDI)")
    ax4.grid(True)

    # Subplot 5+6 (Right middle and bottom merged): Accumulated Cost Matrix with Warping Path
    ax5 = fig.add_subplot(gs[1:, 1])
    im = ax5.imshow(acc_cost_matrix, origin="lower", cmap="viridis", aspect="equal")
    print(len(warping_path))
    ref_indices, live_indices = zip(*warping_path)  # unzip into two lists
    ax5.plot(
        live_indices,
        ref_indices,
        marker="o",
        color="red",
        linestyle="-",
        linewidth=1.5,
        markersize=2,
        label="Warping Path",
    )
    ax5.set_xlim(0, max(live_indices))
    ax5.set_ylim(0, max(ref_indices))
    ax5.set_title("Accumulated Cost Matrix with Warping Path")
    ax5.set_xlabel("live_ts Index")
    ax5.set_ylabel("Reference Time Index")
    ax5.legend()
    ax5.grid(False)

    plt.colorbar(im, ax=ax5, fraction=0.046, pad=0.04)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.text(
        0.5, 0.01, f"Generated on {timestamp}", ha="center", fontsize=9, color="gray"
    )

    # Final layout
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    if not override_filename:
        override_filename = feature_name
    save_path = os.path.join(
        path_log_folder, "figures", f"eval_{override_filename}_align.png"
    )
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)
    plt.show()

if __name__ == "__main__":
    warping_path_path = "data/alignments/ode_to_joy/ts_CENS_warping_path.json"
    alignment_csv_path = "data/alignments/ode_to_joy_300bpm.csv"
    path_log_folder = "data/YOU_DECIDE"
    
    with open(warping_path_path, 'r') as file:
        warping_path = json.load(file)
    
    eval_df = evaluate_alignment(warping_path,
                                 path_alignment_csv=alignment_csv_path,
                                 align_col_note="midi",
                                 align_col_ref="ref_ts",
                                 align_col_live="live_ts")

    filename = os.path.splitext(os.path.basename(warping_path_path))[0]
    
    plot_eval_df(eval_df,
                 warping_path=warping_path,
                 acc_cost_matrix=np.zeros(shape=warping_path[-1], dtype=float),
                 ref_filename=f"[UNKNOWN] {filename}",
                 live_filename=f"[UNKNOWN] {filename}",
                 feature_name=f"[UNKNOWN] {filename}",
                 path_log_folder=config.get("path_log_folder"),
                 override_filename=filename)
    

