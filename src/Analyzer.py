from Synchronizer import Synchronizer
import time
import matplotlib.pyplot as plt
import numpy as np
import os
import librosa
import pandas as pd


class Analyzer:
    def __init__(self, sync: Synchronizer, log_dir: str, figure_dir: str):
        self.sync = sync
        self.score_follower = sync.score_follower
        self.mic = self.score_follower.mic
        self.player = sync.player
        self.log_dir = log_dir
        self.figure_dir = figure_dir

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.time_log = {
            "live_time": [],  # timestamps of live features
            "estimated_time": [],  # score follower estimates for live features
            "accompanist_time": [],  # timestamps marking where companion was in accompaniment
        }

        self.measure_log = {
            "live_measure_onsets": [],  # closet live times hand annotated timestamps of measure onsets in live audio
            "ref_measure_onsets": [],  # closet ref_times to hand annotated timestamps of measure onsets in reference audio
            "estimated_measure_onsets": [],  # score follower estimates for measure onsets
            "accompanist_measure_onsets": [],  # timestamps of where Companion was when the soloist started each measure
        }

        self.error_log = {
            "alignment_error": [],
            "accompaniment_error": [],
            "total_error": []
        }

        plt.rcParams.update({'font.size': 18})
    
    def get_ref(self):
        '''Get the reference features from the score follower'''
        return self.score_follower.ref
    
    def get_ref_index(self):
        return self.score_follower.otw.j
    
    def get_live(self):
        return self.score_follower.otw.live
    
    def get_live_index(self):
        return self.score_follower.otw.t
    
    def indices_to_time(self, indices):
        return indices * sync.win_length / sync.sample_rate
    
    def get_cost_matrix(self):
        return self.score_follower.otw.D[:, :self.score_follower.otw.t+1]
    
    def get_annotations(self, path, key):
        df = pd.read_excel(path)
        live_times = df[key].to_numpy()
        ref_times = df["ref"].to_numpy()

        return ref_times, live_times
    
    def get_nearest_indices(self, array1, array2):
        '''For each value in array1, find the index of the nearest value in array 2.'''
        differences = np.abs(array1[:, np.newaxis] - array2)

        # Find the index of the minimum difference for each value in array1
        nearest_indices = np.argmin(differences, axis=1)

        return nearest_indices
    
    def create_time_log(self):
        # get the references and live indices from the score follower's alignment path
        estimated_indices, live_indices = np.asarray(self.score_follower.path, dtype=np.float32).T

        # convert all indices to timestamps
        self.time_log["live_time"] = self.indices_to_time(live_indices)
        self.time_log["estimated_time"] = self.indices_to_time(estimated_indices)

        # Get the log of accompanist timestamps from the synchronizer
        self.time_log["accompanist_time"] = np.asarray(self.sync.accompanist_time_log, dtype=np.float32)

    def create_measure_log(self, ref_measure_onsets, live_measure_onsets):
        # In the reference audio, measure i starts at time true_measure_onsets[i]
        # In the live audio, measure i starts at time annotated_measure_onset[i]
        # ref_measure_onsets, live_measure_onsets = self.get_annotations(alignment)
        self.measure_log["ref_measure_onsets"] = ref_measure_onsets

        # For each measure, look at when it starts and find the index of the nearest time in the "soloist_time" log.
        measure_indices = self.get_nearest_indices(live_measure_onsets, self.time_log["live_time"])

        # measure_onset_indices contains the indices of the data that were recorded when the soloist
        # started playing a new measure

        # Get the live times that are closest to the measure onsets
        self.measure_log["live_measure_onsets"] = self.time_log["live_time"][measure_indices]

        # Get the corresponding estimated times
        self.measure_log["estimated_measure_onsets"] = self.time_log["estimated_time"][measure_indices]

        # accompanist_onset_indices = self.get_nearest_indices(ref_measure_onsets, self.time_log["accompanist_time"])
        self.measure_log["accompanist_measure_onsets"] = self.time_log["accompanist_time"][measure_indices]

    def create_error_log(self):
        # Calculate the difference beteween predicted and actual measure onset times
        self.error_log["alignment_error"] = self.measure_log["estimated_measure_onsets"] - self.measure_log["ref_measure_onsets"]

        # The accompaniment measure onsets are the same as the reference
        self.error_log["accompaniment_error"] = self.measure_log["accompanist_measure_onsets"] - self.measure_log["estimated_measure_onsets"]

        self.error_log["total_error"] = self.measure_log["accompanist_measure_onsets"] - self.measure_log["ref_measure_onsets"]

    def export_logs(self, time=True, measure=True, error=True):
        if time:
            time_df = pd.DataFrame.from_dict(self.time_log)
            time_df.to_csv(os.path.join(self.log_dir, 'time_log.csv'))

        if measure:
            measure_df = pd.DataFrame.from_dict(self.measure_log)
            measure_df.to_csv(os.path.join(self.log_dir, 'measure_log.csv'))
        
        if error:
            error_df = pd.DataFrame.from_dict(self.error_log)
            error_df.to_csv(os.path.join(self.log_dir, 'error_log.csv'))
    
    def print_last(self):
        soloist_time = self.sync.soloist_time()
        predicted_time = self.sync.predicted_time()
        accompanist_time = self.sync.accompanist_time()
        playback_rate = self.sync.player.playback_rate
        print(f"Soloist time: {soloist_time:.2f}, Predicted time: {predicted_time:.2f}, Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}")
    
    def plot_cost_matrix(self, show_path=False):
        cost_matrix = self.get_cost_matrix()
        if show_path:
            indices = np.asarray(self.score_follower.path).T
            cost_matrix[(indices[0], indices[1])] = np.inf
        
        filename = os.path.join(self.figure_dir, 'cost_matrix.png')

        plt.figure()
        plt.imshow(cost_matrix)
        plt.title('OTW Cost Matrix')
        plt.xlabel('Live Sequence')
        plt.ylabel('Reference Sequence')
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.5, dpi=400)
        plt.close()

    def plot_alignment(self):
        filename = os.path.join(self.figure_dir, 'alignment_path.png')

        plt.figure()
        plt.plot(self.measure_log["live_measure_onsets"], self.measure_log["ref_measure_onsets"], label='Ground Truth')
        plt.plot(self.measure_log["live_measure_onsets"], self.measure_log["estimated_measure_onsets"], label='Prediction')
        plt.title("Alignment Path")
        plt.xlabel("Live Time (s)")
        plt.ylabel("Reference Time (s)")
        plt.grid(visible=True)
        plt.legend()
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)

    def plot_alignment_error(self):
        filename = os.path.join(self.figure_dir, 'alignment_error.png')

        plt.figure(figsize=(8, 6))
        plt.plot(self.measure_log["live_measure_onsets"], self.error_log["alignment_error"])
        plt.xlabel("Live Time (s)")
        plt.ylabel("Alignment Error (s)")
        plt.title('Alignment Error')
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)

    def plot_accompaniment(self):
        filename = os.path.join(self.figure_dir, 'accompaniment_path.png')

        plt.figure()
        plt.plot(self.measure_log["estimated_measure_onsets"], self.measure_log["estimated_measure_onsets"], label='Target')
        plt.plot(self.measure_log["estimated_measure_onsets"], self.measure_log["accompanist_measure_onsets"], label='Actual')
        plt.xlabel("Reference Time (s)")
        plt.ylabel("Accompanist Time (s)")
        plt.title("Accompaniment Path")
        plt.grid(visible=True)
        plt.legend()
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)

    def plot_accompaniment_error(self):
        filename = os.path.join(self.figure_dir, 'accompaniment_error.png')

        plt.figure(figsize=(8, 6))
        plt.plot(self.measure_log["estimated_measure_onsets"], self.error_log["accompaniment_error"])
        plt.xlabel("Reference Time (s)")
        plt.ylabel("Accompaniment Error (s)")
        plt.title('Accompaniment Error')
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)

    def plot_total_error(self):
        filename = os.path.join(self.figure_dir, 'total_error.png')

        plt.figure(figsize=(8, 6))
        plt.plot(self.measure_log["live_measure_onsets"], self.error_log["total_error"])
        plt.title("Total Error")
        plt.xlabel("Live Time (s)")
        plt.ylabel("Total Error (s)")
        plt.grid(visible=True)
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)
        plt.close()

    def offline_dtw(self):
        cost_matrix, wp = librosa.sequence.dtw(X=self.score_follower.ref, Y=self.score_follower.otw.live[:, :self.score_follower.otw.t+1], metric='cosine')
        filename = os.path.join(self.figure_dir, 'offline_dtw.png')
        ref_indices = wp[:, 0]
        live_indices = wp[:, 1]

        cost_matrix[ref_indices, live_indices] = np.inf

        plt.figure()
        plt.imshow(cost_matrix)
        plt.title('Cost Matrix')
        plt.xticks(np.arange(0, cost_matrix.shape[1], 250))
        plt.yticks(np.arange(0, cost_matrix.shape[0], 250))
        plt.xlabel('Sequence B')
        plt.ylabel('Sequence A')
        plt.grid(visible=False)
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)
        plt.close()


if __name__ == '__main__':
    # create a synchronizer object
    sync = Synchronizer(reference='data/bach/synthesized/track0.wav',
                        accompaniment='data/bach/synthesized/track1.wav',
                        source='data/bach/live/variable_tempo.wav',
                        sample_rate=16000,
                        channels=1,
                        frames_per_buffer=1024,
                        window_length=4096,
                        c=30,
                        max_run_count=3,
                        diag_weight=0.4,
                        Kp=0.0,
                        Ki=0.00,
                        Kd=0.0)

#0.5, 0.001, 0.05

    analyzer = Analyzer(sync, log_dir='data/bach/logs', figure_dir='data/bach/figures')

    # start the synchronizer
    sync.start()

    # wait until the synchronizer is active
    while not sync.is_active():
        time.sleep(0.01)

    try:
        while sync.update():
            analyzer.print_last()
            print(sync.score_follower.mic.count)

    except KeyboardInterrupt:
        sync.stop()

    sync.save_performance('data/bach/performance.wav')

    df = pd.read_excel("data/bach/alignment.xlsx")
    ref_measure_onsets = df["ref"].to_numpy()
    live_measure_onsets = df["variable"].to_numpy()

    analyzer.create_time_log()
    analyzer.create_measure_log(ref_measure_onsets, live_measure_onsets)
    analyzer.create_error_log()
    analyzer.export_logs()
    
    analyzer.plot_cost_matrix(show_path=True)
    analyzer.plot_alignment_error()
    analyzer.plot_alignment()
    analyzer.plot_accompaniment()
    analyzer.plot_accompaniment_error()
    analyzer.plot_total_error()
    analyzer.offline_dtw()
