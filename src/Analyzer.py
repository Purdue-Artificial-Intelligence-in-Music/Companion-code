from Synchronizer import Synchronizer
import time
import matplotlib.pyplot as plt
import numpy as np
from librosa.display import specshow, waveshow
import librosa
from features import audio_to_np_cens


class Analyzer:
    def __init__(self, sync: Synchronizer):
        self.sync = sync
        self.score_follower = sync.score_follower
        self.mic = self.score_follower.mic
        self.player = sync.player

        self.log = {
            "soloist_time": [],
            "predicted_time": [],
            "accompanist_time": [],
            "alignment_error": [],
            "accompaniment_error": [],
        }

    def get_ref_audio(self):
        return self.score_follower.ref_audio
    
    def get_ref(self):
        return self.score_follower.ref
    
    def get_ref_index(self):
        return self.score_follower.otw.j
    
    def get_live(self):
        return self.score_follower.otw.live
    
    def get_live_index(self):
        return self.score_follower.otw.t
    
    def get_cost_matrix(self):
        return self.score_follower.otw.D
    
    def plot_cost_matrix(self, filename, show_path=False):
        cost_matrix = self.get_cost_matrix()
        if show_path:
            print('showing path')
            indices = np.asarray(self.score_follower.path).T
            cost_matrix[(indices[0], indices[1])] = np.inf

        plt.figure()
        plt.imshow(cost_matrix)
        plt.title('OTW Cost Matrix')
        plt.xlabel('Live Sequence')
        plt.ylabel('Reference Sequence')
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.5, dpi=400)
        plt.close()

    def plot_accompaniment_error(self, filename):
        error = self.log["accompaniment_error"]
        predicted_time = self.log["predicted_time"]
        
        plt.figure()
        plt.plot(predicted_time, error)
        plt.xlabel("Predicted Time (s)")
        plt.ylabel("Accompaniment Error (s)")
        plt.title('Accompaniment Error')
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)

    def plot_alignment_error(self, filename):
        error = self.log["alignment_error"]
        soloist_time = self.log["soloist_time"]
        
        plt.figure()
        plt.plot(soloist_time, error)
        plt.xlabel("Soloist Time (s)")
        plt.ylabel("Alignment Error (s)")
        plt.title('Alignment Error')
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)

    def plot_alignment(self, filename):
        plt.figure()
        plt.plot(self.log["soloist_time"], self.log["predicted_time"])
        plt.title("Alignment Path")
        plt.xlabel("Soloist Time (s)")
        plt.ylabel("Reference Time (s)")
        plt.grid(visible=True)
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)

    def plot_accompaniment(self, filename):
        plt.figure()
        plt.plot(self.log["predicted_time"], self.log["accompanist_time"])
        plt.title("Accompaniment Path")
        plt.xlabel("Reference Time (s)")
        plt.ylabel("Accompanist Time (s)")
        plt.grid(visible=True)
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)

    def plot_total_error(self, filename):
        total_error = np.asarray(self.log["alignment_error"]) + np.asarray(self.log["accompaniment_error"])
        plt.figure()
        plt.plot(self.log["soloist_time"], total_error)
        plt.title("Total Error")
        plt.xlabel("Soloist Time (s)")
        plt.ylabel("Total Error (s)")
        plt.grid(visible=True)
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)

    def plot_both(self, filename):
        plt.figure()
        plt.plot(self.log["soloist_time"], self.log["predicted_time"], c='b', label='Solo')
        plt.plot(self.log["soloist_time"], self.log["accompanist_time"], c='r', label='Accompaniment')
        plt.legend()
        plt.title('Solo ')
        plt.xlabel("Soloist Time (s)")
        plt.ylabel("Time (s)")
        plt.grid(visible=True)
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.1, dpi=400)
    
    def update_log(self):
        self.log["soloist_time"].append(self.sync.soloist_time())
        self.log["predicted_time"].append(self.sync.predicted_time())
        self.log["accompanist_time"].append(self.sync.accompanist_time())
        self.log["alignment_error"].append(self.sync.predicted_time() - self.sync.soloist_time())
        self.log["accompaniment_error"].append(self.sync.accompanist_time() - self.sync.predicted_time())


if __name__ == '__main__':
    # create a synchronizer object
    sync = Synchronizer(score='midi/Twelve_Duets.mid',
                        source='audio/Twelve_Duets/cello0.wav',
                        sample_rate=16000,
                        channels=1,
                        frames_per_buffer=1024,
                        window_length=4096,
                        c=8,
                        max_run_count=3,
                        diag_weight=0.4,
                        Kp=0.2,
                        Ki=0.01,
                        Kd=0.05)

    analyzer = Analyzer(sync)

    # start the synchronizer
    sync.start()

    # wait until the synchronizer is active
    while not sync.is_active():
        time.sleep(0.01)

    try:
        while sync.is_active():
            # update the playback rate of the accompaniment
            sync.update()
            analyzer.update_log()
            print(sync.player.playback_rate)

    except KeyboardInterrupt:
        sync.stop()
        sync.join()

    sync.save_performance()
    analyzer.plot_cost_matrix('cost_matrix.png', show_path=True)
    analyzer.plot_accompaniment_error('accompaniment_error.png')
    analyzer.plot_alignment_error('alignment_error.png')
    analyzer.plot_total_error('total_error.png')
    analyzer.plot_alignment('alignment.png')
    analyzer.plot_accompaniment('accompaniment.png')
    analyzer.plot_both('both.png')
