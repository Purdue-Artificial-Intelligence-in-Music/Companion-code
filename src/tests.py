import unittest
import time
from AudioThreadWithBuffer import AudioThreadWithBuffer
from BeatDetectionThread import BeatDetectionThread

class Tests(unittest.TestCase):
    def example_test(self):
        pass

    def metronome_beat_detection_test(self):
        # TODO
        # Generate an audio signal/use a precomputed one of two metronomes
        # Manually calculate the error using math
        # Sample the error of the beat detection thread at a bunch of different times and compare the output to your expected array of error
        # If it's significantly wrong, write an exception
        AThread = AudioThreadWithBuffer(name="SPA_Thread", starting_chunk_size=44100, wav_file='replace with actual file')
        BeatThread = BeatDetectionThread(name="Beat_Thread", AThread=AThread)

        start_time = time.time()
        expected_error_array = []
        actual_error_array = []

        if (time.time() - start_time) > 5:
            actual_error_array.append(BeatThread.loss)

        
        for expected_loss in expected_error_array:
            for actual_loss in actual_error_array:
                if abs(expected_loss - actual_loss) > 3: # Placeholder value
                    raise Exception("Loss difference is too great!")
        pass

    def error_counting_function_test(self):
        # TODO
        # Generate two audio signals, one which is offset from the other by 1 beat
        # Assert that the error remains +1 even after the offset beat is out of the get_last_sample calls to ATWB
        pass

if __name__ == '__main__':
    unittest.main()