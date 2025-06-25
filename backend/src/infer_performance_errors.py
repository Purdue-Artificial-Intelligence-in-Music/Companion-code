from .evaluate_alignment import calculate_warped_times
import librosa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
import matplotlib.ticker as ticker

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

SAMPLE_RATE = config.get("sample_rate")
WIN_LENGTH = config.get("win_length")
HOP_LENGTH = config.get("hop_length", WIN_LENGTH)
REF_TEMPO = config.get("ref_tempo")

def evaluate_intonation(live_waveform: np.ndarray, eval_df: pd.DataFrame):
    # Parameters
    yin_frame_len = HOP_LENGTH * 2

    warp_samples = []
    warp_pitches = []
    warp_pitch_diffs = []

    for index, row in eval_df.iterrows():
        warp_time = row['predicted live time']
        warp_sample = int(warp_time * SAMPLE_RATE)

        warp_samples.append(warp_sample)
       
        y = live_waveform[:, warp_sample:warp_sample + yin_frame_len]
        f0_vec = librosa.yin(y,
                             fmin=librosa.note_to_hz('C2'),
                             fmax=librosa.note_to_hz('C7'),
                             sr=SAMPLE_RATE,
                             frame_length=yin_frame_len,
                             hop_length=HOP_LENGTH,
                             center=False)
    
        midi_vec = librosa.hz_to_midi(f0_vec[0])

        # print("Taking diff of", midi_vec, row['note'])

        diff = midi_vec - row['note']
        idx = np.argmin(np.abs(diff))
        # print(diff, idx)
        
        min_diff = diff[idx]

        warp_pitches.append(midi_vec[idx])
        warp_pitch_diffs.append(min_diff)

        # print("Pitch", row['note'], "at warp ts", warp_time, "has diff", min_diff)

    eval_df['warp sample'] = warp_samples
    eval_df['predicted live note'] = warp_pitches

    pd.set_option('display.max_rows', None)
    print(eval_df)
    plot_f0(live_waveform, yin_frame_len)


def plot_f0(waveform, yin_frame_len):
    # YIN pitch
    f0_yin = librosa.yin(
        waveform,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        sr=SAMPLE_RATE,
        center=False,
        frame_length=yin_frame_len,
        hop_length=HOP_LENGTH
    )
    f0_yin_midi = librosa.hz_to_midi(f0_yin)[0]
    valid_yin = ~np.isnan(f0_yin_midi)

    # pYIN pitch
    f0_pyin, voiced_flag, voiced_probs = librosa.pyin(
        waveform,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        sr=SAMPLE_RATE,
        frame_length=yin_frame_len,
        hop_length=HOP_LENGTH,
        center=False
    )
    f0_pyin_midi = librosa.hz_to_midi(f0_pyin)[0]
    valid_pyin = ~np.isnan(f0_pyin_midi)

    sample_indices_yin = np.arange(len(f0_yin_midi)) * HOP_LENGTH
    sample_indices_pyin = np.arange(len(f0_pyin_midi)) * HOP_LENGTH

    plt.figure(figsize=(12, 5))

    plt.plot(sample_indices_yin[valid_yin], f0_yin_midi[valid_yin],
            color='purple', linewidth=1, label='YIN $f_0$ (MIDI)')

    plt.plot(sample_indices_pyin[valid_pyin], f0_pyin_midi[valid_pyin],
            color='orange', linewidth=1, label='pYIN $f_0$ (MIDI)', alpha=0.7)

    plt.xlabel('Sample Index')
    plt.ylabel('MIDI Note Number')
    plt.title('YIN vs pYIN Pitch Estimation (MIDI)')

    # Y-axis: semitone steps
    plt.yticks(np.arange(int(np.nanmin(f0_yin_midi)), int(np.nanmax(f0_yin_midi)) + 1, 1))

    # X-axis: no scientific notation, regular ticks
    ax = plt.gca()
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x)}'))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(HOP_LENGTH * 5))

    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()