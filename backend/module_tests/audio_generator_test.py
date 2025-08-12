import unittest
import os
import librosa

from src.audio_generator import AudioGenerator

TEMPO = 123
SCORE = os.path.join('data', 'musicxml', 'air_on_the_g_string.musicxml')
OUTPUT_DIR = os.path.join('data', 'audio', 'air_on_the_g_string', str(TEMPO)+'bpm')
SAMPLE_RATE = 44100

# Manually ascertained from score
SCORE_TOTAL_BEATS = 144

class TestAudioGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = AudioGenerator(score_path=SCORE)
    
    def test_generation(self):
        self.generator.generate_audio(output_dir=OUTPUT_DIR, tempo=TEMPO)

        writtenFilenames = ["instrument_0.wav", "instrument_1.wav"]
        
        for filename in writtenFilenames:
            writtenFilePath = os.path.join(OUTPUT_DIR, filename)
            
            # Test existence
            self.assertTrue(os.path.isfile(writtenFilePath))
            
            audio, _ = librosa.load(writtenFilePath, sr=SAMPLE_RATE)
            
            # Test existence of contents
            self.assertGreater(audio.size, 0)
            
            # Test duration of file; anticipated duration is converted from minutes to seconds
            anticipatedDuration = (SCORE_TOTAL_BEATS / TEMPO) * 60
            self.assertAlmostEqual(anticipatedDuration, librosa.get_duration(filename=writtenFilePath), delta=1)

            os.remove(writtenFilePath)
        
        os.rmdir(OUTPUT_DIR)