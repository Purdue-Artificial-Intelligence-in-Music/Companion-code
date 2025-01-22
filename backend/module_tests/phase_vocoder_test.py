import unittest
import tempfile
import os

import numpy as np
import soundfile as sf

from src.phase_vocoder import PhaseVocoder  # import your PhaseVocoder class here


class TestPhaseVocoder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Create a short test WAV file to use in all tests.
        We'll generate a 1-second sine wave at 440 Hz, 44.1 kHz sample rate, mono.
        """
        sr = 44100
        duration = 1.0  # seconds
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        freq = 440.0  # Hz
        audio = 0.5 * np.sin(2.0 * np.pi * freq * t)  # amplitude 0.5

        # Write to a temporary file
        cls.test_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sf.write(cls.test_wav.name, audio, sr)
        cls.sample_rate = sr
        cls.num_samples = len(audio)  # total samples in the file

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the temporary file after all tests are done.
        """
        cls.test_wav.close()
        os.remove(cls.test_wav.name)

    def test_vocoder_default_speed(self):
        """
        Test reading the entire file at default playback rate (1.0)
        and confirm we get roughly the same number of samples out.
        """
        pv = PhaseVocoder(path=self.test_wav.name,
                          sample_rate=self.sample_rate,
                          channels=1,
                          n_fft=1024,
                          win_length=1024,
                          hop_length=256,
                          playback_rate=1.0)

        all_frames = []
        frames_per_call = 512

        while True:
            frames = pv.get_next_frames(frames_per_call)
            if frames is None:
                break
            all_frames.append(frames)

        # Concatenate all and compare length
        output_audio = np.concatenate(all_frames, axis=1)  # shape: (1, total_samples)
        total_out = output_audio.shape[1]

        # Because of windowing or partial frames, it's normal to have slight differences.
        # We'll allow some tolerance. Ideally, it should be close to ~ num_samples.
        self.assertTrue(abs(total_out - self.num_samples) < 2048,
                        msg=f"Output length off by more than 2048 samples. Got {total_out}, expected ~ {self.num_samples}")

        # Test that time index is close to 1.0s
        self.assertAlmostEqual(pv.get_time(), total_out / self.sample_rate, places=3)

    def test_vocoder_slow_speed(self):
        """
        Test reading the entire file at 0.5 playback rate (half-speed).
        We expect roughly double the samples out.
        """
        pv = PhaseVocoder(path=self.test_wav.name,
                          sample_rate=self.sample_rate,
                          channels=1,
                          n_fft=1024,
                          win_length=1024,
                          hop_length=256,
                          playback_rate=0.5)

        all_frames = []
        frames_per_call = 512

        while True:
            frames = pv.get_next_frames(frames_per_call)
            if frames is None:
                break
            all_frames.append(frames)

        output_audio = np.concatenate(all_frames, axis=1)  # shape: (1, total_samples)
        total_out = output_audio.shape[1]

        # For half-speed, we expect about double the original sample count
        self.assertTrue(abs(total_out - 2*self.num_samples) < 2048,
                        msg=f"Output length off by more than 2048 from expected. Got {total_out}, expected ~ {2*self.num_samples}")

        # Check final get_time
        self.assertAlmostEqual(pv.get_time(), total_out / self.sample_rate, places=2)

    def test_vocoder_fast_speed(self):
        """
        Test reading the entire file at 2.0 playback rate (double-speed).
        We expect roughly half the samples out.
        """
        pv = PhaseVocoder(path=self.test_wav.name,
                          sample_rate=self.sample_rate,
                          channels=1,
                          n_fft=1024,
                          win_length=1024,
                          hop_length=256,
                          playback_rate=2.0)

        all_frames = []
        frames_per_call = 512

        while True:
            frames = pv.get_next_frames(frames_per_call)
            if frames is None:
                break
            all_frames.append(frames)

        output_audio = np.concatenate(all_frames, axis=1)  # shape: (1, total_samples)
        total_out = output_audio.shape[1]

        # For double-speed, we expect about half the original sample count
        self.assertTrue(abs(total_out - 0.5*self.num_samples) < 1024,
                        msg=f"Output length off by more than 1024 from expected. Got {total_out}, expected ~ {0.5*self.num_samples}")

        # Check final get_time
        self.assertAlmostEqual(pv.get_time(), total_out / self.sample_rate, places=2)

    def test_vocoder_end_of_file(self):
        """
        Make sure the vocoder eventually returns None to indicate end of file.
        """
        pv = PhaseVocoder(path=self.test_wav.name,
                          sample_rate=self.sample_rate,
                          channels=1,
                          n_fft=1024,
                          win_length=1024,
                          hop_length=256,
                          playback_rate=1.0)

        frames_per_call = 1024

        got_data = False
        while True:
            frames = pv.get_next_frames(frames_per_call)
            if frames is None:
                # end of file
                break
            if frames.shape[1] > 0:
                got_data = True

        # We expect to have gotten *some* frames
        self.assertTrue(got_data, "Never received any frames from the PhaseVocoder.")
        # By now, we expect repeated calls to also give None
        frames_after_eof = pv.get_next_frames(frames_per_call)
        self.assertIsNone(frames_after_eof, "Should still return None after end of file.")


if __name__ == '__main__':
    unittest.main()
