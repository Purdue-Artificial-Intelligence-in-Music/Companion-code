import unittest
import tempfile
import os

import numpy as np
import soundfile as sf

from src.phase_vocoder import PhaseVocoder  # import your modified PhaseVocoder here


class TestPhaseVocoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Create a short test WAV file to use in all tests.
        We'll generate a 1-second sine wave at 440 Hz, 44.1 kHz sample rate, mono.
        """
        sr = 44100
        duration = 1.0  # second
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
        Test reading the entire file at default playback rate (1.0).
        Because _audio_index tracks the original domain, we expect
        `get_time()` to end up ~1.0 seconds, and the output length
        ~ num_samples.
        """
        pv = PhaseVocoder(
            path=self.test_wav.name,
            sample_rate=self.sample_rate,
            channels=1,
            n_fft=1024,
            win_length=1024,
            hop_length=256,
            playback_rate=1.0,
        )

        all_frames = []
        frames_per_call = 512
        while True:
            frames = pv.get_next_frames(frames_per_call)
            if frames is None:
                break
            all_frames.append(frames)

        output_audio = np.concatenate(all_frames, axis=1)  # shape: (1, total_samples)
        total_out = output_audio.shape[1]

        # Check the output length is ~ the original sample count
        self.assertTrue(
            abs(total_out - self.num_samples) < 2048,
            msg=f"Default speed output length off by more than 2048. Got {total_out}, expected ~ {self.num_samples}",
        )

        # Now check get_time() ~ 1.0 second
        final_time = pv.get_time()
        self.assertAlmostEqual(
            final_time,
            1.0,
            delta=0.1,
            msg=f"get_time() should be near 1.0s for default speed, got {final_time}",
        )

    def test_vocoder_slow_speed(self):
        """
        Test reading the entire file at 0.5 playback rate (half-speed).
        We expect ~2x the output samples (time-stretched), but _audio_index
        should still end up ~44100 in the original domain => ~1.0 second of input.
        """
        pv = PhaseVocoder(
            path=self.test_wav.name,
            sample_rate=self.sample_rate,
            channels=1,
            n_fft=1024,
            win_length=1024,
            hop_length=256,
            playback_rate=0.5,
        )

        all_frames = []
        frames_per_call = 512
        while True:
            frames = pv.get_next_frames(frames_per_call)
            if frames is None:
                break
            all_frames.append(frames)

        output_audio = np.concatenate(all_frames, axis=1)
        total_out = output_audio.shape[1]

        # Expect about double the original length
        expected_out = 2 * self.num_samples
        self.assertTrue(
            abs(total_out - expected_out) < 2048,
            msg=f"Half-speed output length off. Got {total_out}, expected ~ {expected_out}",
        )

        # get_time() in *original* domain => should be ~1.0s
        final_time = pv.get_time()
        self.assertAlmostEqual(
            final_time,
            1.0,
            delta=0.1,
            msg=f"get_time() should be near 1.0s for half speed, got {final_time}",
        )

    def test_vocoder_fast_speed(self):
        """
        Test reading the entire file at 2.0 playback rate (double-speed).
        We expect ~0.5x the output samples, but still get_time() ~1.0 second.
        """
        pv = PhaseVocoder(
            path=self.test_wav.name,
            sample_rate=self.sample_rate,
            channels=1,
            n_fft=1024,
            win_length=1024,
            hop_length=256,
            playback_rate=2.0,
        )

        all_frames = []
        frames_per_call = 512
        while True:
            frames = pv.get_next_frames(frames_per_call)
            if frames is None:
                break
            all_frames.append(frames)

        output_audio = np.concatenate(all_frames, axis=1)
        total_out = output_audio.shape[1]

        # Expect about half the original length
        expected_out = self.num_samples // 2
        self.assertTrue(
            abs(total_out - expected_out) < 1024,
            msg=f"Double-speed output length off. Got {total_out}, expected ~ {expected_out}",
        )

        # get_time() in *original* domain => ~1.0s
        final_time = pv.get_time()
        self.assertAlmostEqual(
            final_time,
            1.0,
            delta=0.1,
            msg=f"get_time() should be near 1.0s for double speed, got {final_time}",
        )

    def test_vocoder_end_of_file(self):
        """
        Make sure that once we've exhausted the STFT frames, get_next_frames returns None
        and that we indeed got some data out before that happened.
        """
        pv = PhaseVocoder(
            path=self.test_wav.name,
            sample_rate=self.sample_rate,
            channels=1,
            n_fft=1024,
            win_length=1024,
            hop_length=256,
            playback_rate=1.0,
        )

        frames_per_call = 1024

        got_data = False
        while True:
            frames = pv.get_next_frames(frames_per_call)
            if frames is None:
                break
            if frames.shape[1] > 0:
                got_data = True

        # We expect to have gotten *some* frames
        self.assertTrue(got_data, "Never received any frames from the PhaseVocoder.")
        # By now, we expect repeated calls to also give None
        frames_after_eof = pv.get_next_frames(frames_per_call)
        self.assertIsNone(
            frames_after_eof, "Should still return None after end of file."
        )


if __name__ == "__main__":
    unittest.main()
