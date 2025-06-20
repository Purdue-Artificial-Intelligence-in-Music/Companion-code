import pandas as pd
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

def evaluate_alignment(score_follower: ScoreFollower, path_alignment_csv, align_col_ref, align_col_live):
    source_times_df = pd.read_csv(path_alignment_csv)

    warping_path = np.array(score_follower.path)
    path_times = warping_path * STEP_SIZE
    
    ref_times = path_times[:, 0] 
    live_times = path_times[:, 1] 
  
    # map each baseline note time to live time
    predicted_times = []
    for time in source_times_df[align_col_ref]: #testDF['baseline_time_s] - expected time of each note in the baseline
        diffs = ref_times - time
        ind = np.argmin(np.abs(diffs))  # find closest time in warping path (closest point in ref_time, which is the ref time sequence that DTW aligned)
        
        if diffs[ind] < 0:
            live_time_left = live_times[ind]
            live_time_right = live_time_left
            if ind + 1 < len(live_times):   
                live_time_right = live_times[ind + 1]
        else:
            live_time_right = live_times[ind]
            live_time_left = live_time_right
            if ind - 1 >= 0:   
                live_time_left = live_times[ind - 1]

        interpolation = (live_time_right - live_time_left) * (diffs[ind] / STEP_SIZE)
        live_time = live_time_left + interpolation
        
        predicted_times.append(live_time) # append corresponding live time as the predicted rubato time
        
    eval_df = pd.DataFrame({
        'baseline': source_times_df[align_col_ref],
        'predicted live time': predicted_times,
        'actual live time': source_times_df[align_col_live]
    })

    eval_df['live deviation'] = eval_df['predicted live time'] - eval_df['actual live time']
    return eval_df

def analyze_eval_df(eval_df):
    pd.set_option('display.max_rows', None)
    print(eval_df)

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
