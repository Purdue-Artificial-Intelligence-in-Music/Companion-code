import numpy as np
import wave

def audio_compressor(input_file, output_file, threshold, ratio, attack_time, release_time):
    # Open the input audio file
    with wave.open(input_file, 'rb') as wave_file:
        params = wave_file.getparams()
        num_frames = params.nframes
        sample_width = params.sampwidth
        sample_rate = params.framerate

        # Read audio data
        audio_data = np.frombuffer(wave_file.readframes(num_frames), dtype=np.int16)

        # Apply compression
        compressed_audio = compress_audio(audio_data, threshold, ratio, attack_time, release_time, sample_rate)

        # Write compressed audio to a new file
        with wave.open(output_file, 'wb') as output_wave:
            output_wave.setparams(params)
            output_wave.writeframes(compressed_audio.tobytes())

def compress_audio(audio_data, threshold, ratio, attack_time, release_time, sample_rate):
    # Convert audio data to float for processing
    audio_data_float = audio_data.astype(float)

    # Envelope follower parameters
    envelope = np.zeros_like(audio_data_float)
    attack_coeff = np.exp(-1 / (attack_time * 0.001 * sample_rate))
    release_coeff = np.exp(-1 / (release_time * 0.001 * sample_rate))

    # Apply compression
    for i in range(1, len(audio_data_float)):
        envelope[i] = max(envelope[i - 1] * release_coeff, abs(audio_data_float[i]))

    # Apply gain reduction
    for i in range(len(audio_data_float)):
        if envelope[i] > threshold:
            gain_reduction = (envelope[i] - threshold) / ratio
            audio_data_float[i] /= (1 + gain_reduction)

    # Clip to 16-bit PCM range
    audio_data_float = np.clip(audio_data_float, -32768, 32767)

    return audio_data_float.astype(np.int16)

    
if __name__ == '__main__':
    input_file = r"c:\Users\nicke\Downloads\RT_Tabla_Violin_Violin_14_Strings_Athena_Koumis_one_shot.wav"
    output_file = r"c:\Users\nicke\Downloads\output.wav"
    audio_compressor(input_file, output_file, threshold=0, ratio=0.1, attack_time=10, release_time=100)