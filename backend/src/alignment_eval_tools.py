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
WIN_LENGTH = config.get("win_length")
REF_TEMPO = config.get("ref_tempo")

FEATURE_NAME = config.get("feature_type", "CENS")

STEP_SIZE = WIN_LENGTH / SAMPLE_RATE  # * (REF_TEMPO / 60) for beats

def calculate_warped_times(warping_path, ref_times):
    # map each baseline note time to live_ts
    warped_times = []

    path_times = warping_path * STEP_SIZE

    ref_path_times = path_times[:, 0]
    live_path_times = path_times[:, 1]

    for query_time in ref_times:
        diffs = ref_path_times - query_time
        idx = np.argmin(np.abs(diffs))  # find closest step in warping path to ref_time

        if diffs[idx] >= 0 and idx > 0:
            left_idx = idx - 1
            right_idx = idx
        elif idx + 1 < len(live_path_times):
            left_idx = idx
            right_idx = idx + 1
        else:
            left_idx = right_idx = idx

        if left_idx == right_idx:
            warped_times.append(live_path_times[left_idx])
            continue

        query_ref_offset = query_time - ref_path_times[left_idx]  # must be positive

        query_offset_norm = query_ref_offset
        if query_ref_offset != 0:
            query_offset_norm = query_offset_norm / STEP_SIZE

        live_max_offset = live_path_times[right_idx] - live_path_times[left_idx]
        query_offset_live = live_max_offset * query_offset_norm

        live_time = live_path_times[left_idx] + query_offset_live
        warped_times.append(live_time)

    return warped_times


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
    

