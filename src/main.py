from Synchronizer import Synchronizer
import time
import os

# Paths to reference, accompaniment, and source audio files
reference = "data/audio/air_on_the_g_string/synthesized/solo.wav"
accompaniment = "data/audio/air_on_the_g_string/synthesized/accompaniment.wav"
source = "data/audio/air_on_the_g_string/live/variable_tempo.wav"


# Create a synchronizer object
synchronizer = Synchronizer(reference=reference,
                            accompaniment=accompaniment,
                            source=source,
                            sample_rate=16000,
                            win_length=4096,
                            hop_length=1024,
                            c=20,
                            max_run_count=3,
                            diag_weight=2,
                            channels=1,
                            frames_per_buffer=1024)

# Start the synchronizer
synchronizer.start()

# Wait until the synchronizer is active
while not synchronizer.is_active():
    time.sleep(0.01)

try:
    while synchronizer.update():  # Update the playback rate of the accompaniment based on fuzzy logic
        soloist_time = synchronizer.soloist_time()
        predicted_time = synchronizer.estimated_time()
        accompanist_time = synchronizer.accompanist_time()
        playback_rate = synchronizer.player.playback_rate
        
        # Alignment and accompaniment error information (optional debugging)
        alignment_error = predicted_time - soloist_time
        accompaniment_error = accompanist_time - predicted_time

        # Print the type of error (membership degree) without returning values
        name = synchronizer.fuzzy_controller.print_error_membership(accompaniment_error)

        # Print the timing information
        print(f'Soloist time: {soloist_time:.2f}, Predicted time: {predicted_time:.2f}, Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}, error: {name}')
        
except KeyboardInterrupt:
    synchronizer.stop()

# Save the performance to a file
synchronizer.save_performance(path='performance.wav')