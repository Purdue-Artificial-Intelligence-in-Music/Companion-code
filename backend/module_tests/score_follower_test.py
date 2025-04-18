import unittest
import numpy as np
import os
import librosa
import pretty_midi
from src.score_follower import ScoreFollower
from src.audio_generator import AudioGenerator

CHROMA_LABEL = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

TEMPO = 80
PROGRAM = 0
PITCH = 97
NOTE = 'C#'


class TestScoreFollower(unittest.TestCase):
    def test_get_chroma(self):

        # Initialize prettyMIDI objects and add note with pitch PITCH
        # Write to note_test.mid
        pm = pretty_midi.PrettyMIDI(initial_tempo=TEMPO)
        instrument = pretty_midi.Instrument(program=PROGRAM, is_drum=False, name='inst')
        note = pretty_midi.Note(velocity=100, pitch=PITCH, start=0, end=5)
        instrument.notes.append(note)
        pm.instruments.append(instrument)
        pm.write(os.path.join(os.path.dirname(__file__), 'note_test.mid'))

        # Synthesize audio from note_test.mid
        midi_path = os.path.join(os.path.dirname(__file__), 'note_test.mid')
        generator = AudioGenerator(score_path=midi_path)
        generator.generate_audio(output_dir=os.path.join(os.path.dirname(__file__)))
        ref_path = os.path.join(os.path.dirname(__file__), 'instrument_0.wav')
        

        score_follower = ScoreFollower(reference=ref_path,
                                   c=10,
                                   max_run_count=3,
                                   diag_weight=0.5,
                                   sample_rate=44100,
                                   win_length=8192)
        
        source_audio = librosa.load(ref_path, sr=44100)
        source_audio = source_audio[0].reshape((1, -1))
        frames = source_audio[:,:8192]

        empty_frames = np.zeros((1,2))

        # Get chroma vector of the given frames
        chroma = score_follower._get_chroma(frames)

        empty_chroma = score_follower._get_chroma(empty_frames)

        for i in chroma:
            print(i)

        # Check chroma vector length
        self.assertTrue(len(chroma) == 12)
        self.assertTrue(len(empty_chroma) == 12)

        # Check chroma detects the given note
        note_index = np.argmax(chroma)
        self.assertEqual(CHROMA_LABEL[note_index], NOTE)

        os.remove(os.path.join(os.path.dirname(__file__), 'instrument_0.wav'))
        os.remove(os.path.join(os.path.dirname(__file__), 'note_test.mid'))


    def test_step(self):
        midi_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'midi', 'ode_to_joy.mid')
        generator = AudioGenerator(score_path=midi_path)
        generator.generate_audio(output_dir=os.path.join(os.path.dirname(__file__)))


        ref_path = os.path.join(os.path.dirname(__file__), 'instrument_0.wav')
        source = os.path.join(os.path.dirname(__file__), 'instrument_0.wav')

        sample_rate = 44100
        win_length = 8192

        score_follower = ScoreFollower(reference=ref_path,
                                   c=10,
                                   max_run_count=3,
                                   diag_weight=0.5,
                                   sample_rate=sample_rate,
                                   win_length=win_length)
        
        source_audio = librosa.load(source, sr=44100)
        source_audio = source_audio[0].reshape((1, -1))
        
        prev_time = 0
        change = win_length / sample_rate

        for i in range(0, source_audio.shape[-1], 8192):
            frames = source_audio[:, i:i+8192]
            estimated_time = score_follower.step(frames)
            print(f'Estimated: {estimated_time} Increase: {estimated_time - prev_time} Expected: {change}')
            self.assertAlmostEqual(estimated_time - prev_time, change, delta=0.2)

            prev_time = estimated_time

        os.remove(os.path.join(os.path.dirname(__file__), 'instrument_0.wav'))
        os.remove(os.path.join(os.path.dirname(__file__), 'instrument_1.wav'))
