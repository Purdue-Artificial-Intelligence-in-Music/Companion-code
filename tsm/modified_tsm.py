import librosa
import soundfile as sf


def time_stretch(input_beat, original_beat, original_audio_path, error):
    """
    Time-stretches the original audio to match the input beat based on the error value.

    :param input_beat: The BPM of the input audio from the microphone.
    :param original_beat: The BPM of the original audio track.
    :param original_audio_path: The path to the original audio file.
    :param error: The difference in beats.
    :return: The time-stretched audio as a numpy array, and the corresponding sample rate.
    """
    
    y, sr = librosa.load(original_audio_path)
    
    original_duration_per_beat = 60.0 / original_beat
    
    target_duration_per_beat = 60.0 / (input_beat + error)
    
    rate = target_duration_per_beat / original_duration_per_beat
    
    y_stretched = librosa.effects.time_stretch(y, rate=rate)
    
    return y_stretched, sr



def main():
    original_audio_path = 'C:\\Users\\Tima\\Desktop\\Companion-code\\beat_tempo_detection\\songs\\around_the_output.wav'
    
    input_beat =  123.04687499999999
    original_beat =  42.49974300986841
    
    error = 5
    
    stretched_audio, sample_rate = time_stretch(input_beat, original_beat, original_audio_path, error)
    
    stretched_audio_path = 'C:\\Users\\Tima\\Desktop\\Companion-code\\tsm\\modified.wav'
    sf.write(stretched_audio_path, stretched_audio, sample_rate)
    
    print(f"Stretched audio has been saved to {stretched_audio_path}")

if __name__ == "__main__":
    main()