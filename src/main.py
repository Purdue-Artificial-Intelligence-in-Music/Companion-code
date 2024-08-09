from Synchronizer import Synchronizer
import time


# create a synchronizer object
synchronizer = Synchronizer(reference='data/bach/synthesized/track0.wav',
                            accompaniment='data/bach/synthesized/track1.wav',
                            source='data/bach/live/constant_tempo.wav',
                            Kp=0.5,
                            Ki=0.001,
                            Kd=0.05,
                            sample_rate=16000,
                            win_length=4096,
                            hop_length=1024,
                            c=20,
                            max_run_count=3,
                            diag_weight=0.5,
                            channels=1,
                            frames_per_buffer=1024)

# start the synchronizer
synchronizer.start()

# wait until the synchronizer is active
while not synchronizer.is_active():
    time.sleep(0.01)

try:
    while synchronizer.update():  # update the playback rate of the accompaniment
        soloist_time = synchronizer.soloist_time()
        predicted_time = synchronizer.estimated_time()
        accompanist_time = synchronizer.accompanist_time()
        playback_rate = synchronizer.player.playback_rate
        print(f'Soloist time: {soloist_time:.2f}, Predicted time: {predicted_time:.2f}, Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}')
        print(synchronizer.score_follower.mic.count)
        alignment_error = predicted_time - soloist_time
        accompaniment_error = accompanist_time - predicted_time

except KeyboardInterrupt:
    synchronizer.stop()

synchronizer.save_performance(path='data/bach/performance.wav')
