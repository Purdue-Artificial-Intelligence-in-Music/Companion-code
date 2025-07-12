import streamlit as st

import os
from datetime import datetime
import librosa
import numpy as np
import matplotlib.pyplot as plt

from src.features_cens import CENSFeatures
from src.features_f0 import F0Features
from src.features_mel_spec import MelSpecFeatures
from src.features_stacked import StackedFeatures
from src.score_follower import ScoreFollower

RESULTS_DIR = os.path.join("data", "debug")


def get_results():
    return [
        d
        for d in os.listdir(RESULTS_DIR)
        if os.path.isdir(os.path.join(RESULTS_DIR, d))
    ]


def render_svg(svg_file):
    with open(svg_file, "r") as f:
        svg_content = f.read()
    st.image(svg_content)


def generate_plot(warping_path, acc_cost_matrix, save_path):
    fig, ax = plt.subplots()
    im = ax.imshow(acc_cost_matrix, origin="lower", cmap="viridis", aspect="equal")
    ref_indices, live_indices = zip(*warping_path)  # unzip into two lists
    ax.plot(
        live_indices,
        ref_indices,
        marker="o",
        color="red",
        linestyle="-",
        linewidth=1.5,
        markersize=2,
        label="Warping Path",
    )
    ax.set_xlim(0, max(live_indices))
    ax.set_ylim(0, max(ref_indices))
    ax.set_title("Accumulated Cost Matrix with Warping Path")
    ax.set_xlabel("Live Time Index")
    ax.set_ylabel("Reference Time Index")
    ax.legend()
    ax.grid(False)

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.text(
        0.5, 0.01, f"Generated on {timestamp}", ha="center", fontsize=9, color="gray"
    )

    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, "align.svg"))
    # plt.show()


selected_result = st.sidebar.selectbox("Select a result", get_results(), index=None)

if selected_result is not None:
    st.header(f"Showing result: {selected_result}")

    result_dir = os.path.join(RESULTS_DIR, selected_result)

    params_path = os.path.join(result_dir, "params.json")
    if os.path.exists(params_path):
        with open(params_path, "r") as f:
            params = json.load(f)
        st.write("Parameters:")
        st.json(params)

    subfolders = [
        d for d in os.listdir(result_dir) if os.path.isdir(os.path.join(result_dir, d))
    ]

    if not subfolders:
        st.warning("No subfolders found in this result.")

    for subfolder in subfolders:
        with st.expander(subfolder):
            subfolder_path = os.path.join(result_dir, subfolder)
            svg_files = [f for f in os.listdir(subfolder_path) if f.endswith(".svg")]

            if not svg_files:
                st.warning("No SVG files found in this subfolder.")
                continue

            for svg_file in svg_files:
                st.subheader(svg_file)
                render_svg(os.path.join(subfolder_path, svg_file))
else:
    ref_path = st.text_input("Reference WAV file", "data/audio/")
    live_path = st.text_input("Live WAV file", "data/audio/")

    sample_rate = st.number_input(
        "Sample Rate", min_value=8000, max_value=96000, value=44100
    )

    win_length = st.number_input(
        "Window Length", min_value=256, max_value=8192, value=1024
    )
    hop_length = st.number_input("Hop Length", min_value=128, max_value=4096, value=512)

    max_run_count = st.number_input("Maximum Run Count", min_value=1, value=3)
    diag_weight = st.slider("Diagonal Weight", min_value=0.1, max_value=2.0, value=0.75)

    if st.button("Run"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        result_dir = os.path.join(RESULTS_DIR, timestamp)
        os.makedirs(result_dir, exist_ok=True)

        params = {
            "ref_path": ref_path,
            "live_path": live_path,
            "sample_rate": sample_rate,
            "win_length": win_length,
            "hop_length": hop_length,
            "max_run_count": max_run_count,
            "diag_weight": diag_weight,
        }
        params_path = os.path.join(result_dir, "params.json")
        with open(params_path, "w") as f:
            json.dump(params, f, indent=4)

        live_audio, _ = librosa.load(live_path, sr=sample_rate)
        live_audio = live_audio.reshape((1, -1))  # reshape soloist audio to 2D array

        for features_cls in [
            StackedFeatures,
            # F0Features,
            # CENSFeatures,
            # MelSpecFeatures,
        ]:
            score_follower = ScoreFollower(
                ref_filename=ref_path,
                c=50,
                max_run_count=max_run_count,
                diag_weight=diag_weight,
                sample_rate=sample_rate,
                win_length=win_length,
                hop_length=hop_length,
                features_cls=features_cls,
            )

            soloist_times = []
            estimated_times = []

            source_index = 0
            while source_index < live_audio.shape[-1]:
                data = live_audio[:, source_index : source_index + win_length]
                source_index += win_length

                estimated_time = score_follower.step(data)

                soloist_times.append(source_index / sample_rate)
                estimated_times.append(estimated_time)

            subfolder = os.path.join(result_dir, features_cls.__name__)

            generate_plot(
                score_follower.path, score_follower.otw.accumulated_cost, subfolder
            )
            # os.makedirs(result_dir)
