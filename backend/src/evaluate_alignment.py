import pretty_midi
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yaml
from .score_follower import ScoreFollower

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

SAMPLE_RATE = config.get("sample_rate")
WIN_LENGTH = config.get("win_length")
REF_TEMPO = config.get("ref_tempo")

STEP_SIZE = (WIN_LENGTH / SAMPLE_RATE) # * (REF_TEMPO / 60) for beats

def create_alignment_csv(baseline_file, altered_file, csv_out_path):
    midi_baseline = pretty_midi.PrettyMIDI(baseline_file)
    midi_altered = pretty_midi.PrettyMIDI(altered_file)
    pitch = []
    baseline_time = []
    
    for instruments in midi_baseline.instruments:
        for note in instruments.notes:
            pitch.append(note.pitch)
            baseline_time.append(note.start)

    altered_time = []
    for instruments in midi_altered.instruments:
        for note in instruments.notes:
            altered_time.append(note.start)

    df = pd.DataFrame({
        'note pitch': pitch,
        'baseline_time': baseline_time,
        'altered_time': altered_time
    })

    df['Serial No.'] = df.index
    df = df[['Serial No.', 'note pitch', 'baseline_time', 'altered_time']]

    print(df.head(n=10))

    df.to_csv(csv_out_path, sep=',', index=False)
    #df.to_csv(midi_out, sep=';', quoting=2, float_format='%.3f', index=False)
    
def calculate_warped_times(warping_path, ref_times):
    # map each baseline note time to live time
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

def evaluate_alignment(score_follower: ScoreFollower, path_alignment_csv, align_col_note, align_col_ref, align_col_live, force_diagonal=False):
    source_df = pd.read_csv(path_alignment_csv)

    warping_path = np.array(score_follower.path)

    if (force_diagonal):
        warping_path = np.array([(i, i) for i in range(len(score_follower.path))])
  
    # map each baseline note time to live time
    predicted_times = calculate_warped_times(warping_path, source_df[align_col_ref])
 
    eval_df = pd.DataFrame({
        'note': source_df[align_col_note],
        'baseline': source_df[align_col_ref],
        'predicted live time': predicted_times,
        'actual live time': source_df[align_col_live]
    })

    eval_df['live deviation'] = eval_df['predicted live time'] - eval_df['actual live time']
    return eval_df

def analyze_eval_df(eval_df):
    pd.set_option('display.max_rows', None)
    # print(eval_df)

    # get smallest deviation
    min_idx = eval_df['live deviation'].abs().argmin()
    min_dev = eval_df.loc[min_idx, 'live deviation']

    # get largest deviation 
    max_idx = eval_df['live deviation'].abs().argmax()
    max_dev = eval_df.loc[max_idx, 'live deviation']

    print(f"min deviation: ", {min_dev})
    print(f"max deviation: ", {max_dev})
    print(f"mean deviation: ", {eval_df['live deviation'].mean()})
    print(f"median deviation: ", {eval_df['live deviation'].median()})
    print(f"variance deviation: ", {eval_df['live deviation'].var()})

def plot_eval_df(eval_df):
    plt.figure(figsize=(15, 10))

    # Histogram of alignment errors
    plt.subplot(2, 2, 1)
    plt.hist(eval_df['live deviation'], bins=20, edgecolor='black')
    plt.title('Histogram of Alignment Errors')
    plt.xlabel('Alignment Error (seconds)')
    plt.ylabel('Frequency')

    # Alignment error over notes (using positive and negative instances)
    plt.subplot(2, 2, 2)
    plt.plot(eval_df['live deviation'])
    plt.title('Alignment Error')
    plt.xlabel('Note No.')
    plt.ylabel('Alignment Error (seconds)')
    plt.axhline(y=0, color='r', linestyle='--')

    plt.tight_layout()
    plt.savefig('error_analysis.png')
    plt.show()

 