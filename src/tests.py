import unittest

class Tests(unittest.TestCase):
    def example_test(self):
        pass

    def metronome_beat_detection_test(self):
        # TODO
        # Generate an audio signal/use a precomputed one of two metronomes
        # Manually calculate the error using math
        # Sample the error of the beat detection thread at a bunch of different times and compare the output to your expected array of error
        # If it's significantly wrong, write an exception
        pass

    def error_counting_function_test(self):
        # TODO
        # Generate two audio signals, one which is offset from the other by 1 beat
        # Assert that the error remains +1 even after the offset beat is out of the get_last_sample calls to ATWB

if __name__ == '__main__':
    unittest.main()