from audio_generator import AudioGenerator
from otw import OnlineTimeWarping as OTW
from features import ChromaMaker, file_to_np_cens
from score_follower import ScoreFollower
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import librosa

from scipy.interpolate import interp1d

def convertMidi(path, output_dir):
    SAMPLE_RATE = 44100
    TEMPO = 100
    generator = AudioGenerator(score_path = path)
    generator.generate_audio(output_dir=output_dir, tempo=TEMPO, sample_rate=SAMPLE_RATE)


'''
    reference = os.path.join('data', 'audio', 'twinkle_twinkle', '200bpm', 'instrument_0.wav')
    source = os.path.join('data', 'audio', 'twinkle_twinkle', '200bpm', 'instrument_0.wav')

    source_audio = librosa.load(source, sr=44100)
    source_audio = source_audio[0].reshape((1, -1))

    score_follower = ScoreFollower(reference=reference,
                                   c=50,
                                   max_run_count=3,
                                   diag_weight=0.5,
                                   sample_rate=44100,
                                   win_length=4096)

    for i in range(0, source_audio.shape[-1], 4096):
        frames = source_audio[:, i:i+4096]
        estimated_time = score_follower.step(frames)
        # print(
        #     f'Live index: {score_follower.otw.live_index}, Ref index: {score_follower.otw.ref_index}')
        print(
            f'Estimated time: {estimated_time}, Ref index: {score_follower.otw.ref_index * score_follower.win_length / score_follower.sample_rate}')


    print(score_follower.path)
'''
def x_to_y(num, xData, yData):
    location = xData.index(int(num))
    if xData[location+1] == xData[location]:
        return yData[location]
    slope = (yData[location+1] - yData[location])/(xData[location+1] - xData[location])
    if slope == 0:
        return yData[location]
    b = yData[location] - slope*xData[location]
    y_value = slope * xData[location] + b
    print(y_value)
    return y_value

def main():
    #baseline_path = "backend/src/evaluation_framework/URMP_altered/24_Pirates_vn_vn/24_Pirates_altered_pieces/baseline.mid"
    #rubato_path = "backend/src/evaluation_framework/URMP_altered/24_Pirates_vn_vn/24_Pirates_altered_pieces/rubato.mid"
    baseline = "backend/src/evaluation_framework/URMP_altered/24_Pirates_vn_vn/24_Pirates_altered_solos/baseline.wav"

    baseline_audio = librosa.load(baseline)
    y, sr = baseline_audio
    tempo, beat_frames_temp = librosa.beat.beat_track(y=y, sr=sr)
    print("Estimated Tempo (BPM):", tempo)
    WIN_LENGTH = 4096
    SAMPLE_RATE = 44100
    STATED_TEMPO = tempo

    source = "backend/src/evaluation_framework/URMP_altered/24_Pirates_vn_vn/24_Pirates_altered_solos/pauses.wav"
    source_audio = librosa.load(source, sr=44100)
    source_audio = source_audio[0].reshape((1, -1))
    score_follower = ScoreFollower(reference=baseline,
                                   c=50,
                                   max_run_count=3,
                                   diag_weight=0.5,
                                   sample_rate=44100,
                                   win_length=4096)
    estimated_time_list = []
    live_index_list = []
    ref_index_list = []
    temp_ref = []
    temp_live = []

    duration_sec = source_audio.shape[-1] / score_follower.sample_rate
    print(f"Source audio duration: {duration_sec:.2f} seconds")


    for i in range(0, source_audio.shape[-1], 4096):
        frames = source_audio[:, i:i+4096]
        estimated_time = score_follower.step(frames)
        # print(
        #     f'Live index: {score_follower.otw.live_index}, Ref index: {score_follower.otw.ref_index}')
        estimated_time_list.append(estimated_time)
        #ref_index, live_index = score_follower.path[-1]
        #ref_beat = ref_index * WIN_LENGTH / SAMPLE_RATE * STATED_TEMPO / 60
        #live_beat = live_index * WIN_LENGTH / SAMPLE_RATE * STATED_TEMPO / 60
        ref_index_list.append(score_follower.otw.ref_index * score_follower.win_length / score_follower.sample_rate)
        live_index_list.append(score_follower.otw.live_index * score_follower.win_length / score_follower.sample_rate)

        #temp_ref.append(score_follower.otw.ref_index)
        #temp_live.append(score_follower.otw.live_index)
        #temp_ref, temp_live = score_follower.path[i]
        '''
        live_index_list.append(score_follower.otw.live_index * score_follower.win_length / score_follower.sample_rate)
        ref_index_list2.append(score_follower.otw.ref_index * score_follower.win_length / score_follower.sample_rate)
        '''
        '''
        print(
            f'Estimated time: {estimated_time}, Ref index: {score_follower.otw.ref_index * score_follower.win_length / score_follower.sample_rate}')
        '''
    #print(score_follower.path)
    print(f"path length: ", {len(score_follower.path)})
    '''
    tempDF = pd.DataFrame({
        'ref_index beat': temp_ref * WIN_LENGTH / SAMPLE_RATE * 100 / 60,
        'live_index beat': temp_live * WIN_LENGTH / SAMPLE_RATE * 100 / 60,
        'ref_beat': ref_index_list,
        'live_beat': live_index_list
    })
    print(tempDF.head(n=15))
    '''
    df = pd.DataFrame()
    df['estimated time'] = estimated_time_list
    df['ref_beat'] = ref_index_list
    df['live_beat'] = live_index_list
    df['estimated time (beats?)'] = df['estimated time'] / 60 * STATED_TEMPO
    df['deviation'] = df['live_beat'] - df['ref_beat']
    print(df.head(n=15))
    #Ignore df

    # solo_note_timings contains note timings for baseline audio, rubato audio, etc
    analysis = "backend/src/evaluation_framework/URMP_altered/24_Pirates_vn_vn/24_Pirates_analysis/solo_note_timings.csv"

    # reading solo_note_timings csv
    testDF = pd.read_csv(analysis)
    #testDF['rubato_deviation'] = testDF['rubato_beat'] - testDF['baseline_beat']

    # converting baseline beat to time in seconds and saving these times in baseline_time_s column
    # seconds_per_beat = 60 / tempo
    testDF['baseline_time_sec'] = testDF['baseline_beat'] *  60/100 #seconds_per_beat
    print(testDF.head(n=10))

    # warping path is an attribute of score_follower object, "Alignment path between live and reference sequences"
    warping_path = np.array(score_follower.path)
    x1 = warping_path[:, 0] # use .tolist() if using x_to_y()
    y1 = warping_path[:, 1] # use .tolist() if using x_to_y()

    warping_path_x = len(x1)
    warping_path_y = len(y1)
    print(f"x1 length: ", {warping_path_x})
    print(f"y1 length: ", {warping_path_y})
    print(f"testDF (baseline) length", {len(testDF['baseline_beat'])})

    # alignment path is sequence of index pairs, this calculation gets them as time in seconds
    #ref_time = x1 * WIN_LENGTH / SAMPLE_RATE # all time steps in baseline, seconds?
    #live_time = y1 * WIN_LENGTH / SAMPLE_RATE # their aligned counterparts in rubato, seconds?
    ref_time = x1 * WIN_LENGTH / SAMPLE_RATE * 100 / 60 #beats?
    #print(f"ref_time = x1 * WIN_LENGTH...: ", {ref_time})
    live_time = y1 * WIN_LENGTH / SAMPLE_RATE * 100 / 60 #beats?
    #ref_time = x1 #????? #indices?
    #live_time = y1 #???? #indices?


    
    # map each baseline note time to rubato time
    predicted_source_times = []
    for time in testDF['baseline_beat']: #testDF['baseline_time_s] - expected time of each note in the baseline
        idx = np.argmin(np.abs(ref_time - time))  # find closest time in warping path (closest point in ref_time, which is the ref time sequence that DTW aligned)
        predicted_source_times.append(live_time[idx]) # append corresponding live time as the predicted rubato time
        # predicted_rubato_times.append(x_to_y(time, x1, y1))
    



    newDF = pd.DataFrame({
        'baseline': testDF['baseline_beat'],
        'predicted rubato time': predicted_source_times, #predicted_rubato_times,
        'actual rubato time': testDF['pauses_beat'] #* seconds_per_beat
    })

    newDF['rubato devation'] = newDF['predicted rubato time'] - newDF['actual rubato time']
    print(newDF.head(n=20))

    #convertMidi(baseline_path, output_dir)
    #convertMidi(rubato_path, output_dir)
    return

main()
'''
def main():
    input = "backend/src/evaluation_framework/URMP_altered/02_Sonata_vn_vn/02_Sonata_analysis/solo_note_timings.csv"
    testDF = pd.read_csv(input)
    labels = ['rubato', 'pauses', 'accelerando', 'ritardando', 'sine_wave_tempo']
    differencesDF = pd.DataFrame()
    for i in labels:
        #print(f"{i}_beat")
        differencesDF[f"{i}_difference"] = testDF['baseline_beat'] - testDF[f"{i}_beat"]
    print(testDF.head(n=10))
    print(differencesDF.head(n=10))

main()
'''
