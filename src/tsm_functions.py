import numpy as np
import pytsmod as tsm
import soundfile as sf
import threading
import librosa
import time


def process_func(wav_tempo, mic_tempo, wav_data):
    '''
    Perform time-stretching on the WAV audio based on microphone and WAV tempos.

    Args:
    - wav_tempo: Tempo of the WAV audio (float)
    - mic_tempo: Tempo of the microphone audio (float)
    - wav_data: WAV audio data (numpy array)

    Returns:
    - timestretch_ratio: Time-stretch ratio (float)
    '''
    tempo_microphone = mic_tempo    # Get the tempo of the microphone audio from the beatThread
    tempo_wav = wav_tempo  # Get the tempo of the wav audio from the beatThread
    timestretch_ratio = tempo_microphone / tempo_wav # Calculate the time-stretch ratio
    timestretched_wav = time_stretch(wav_data, timestretch_ratio) # Perform time-stretching on the wav audio using the ratio

    # self.previous_microphone_tempo = tempo_microphone
    # self.previous_wav_tempo = tempo_wav
    return timestretch_ratio

"""
The function lower is for processing the output of the beat detection thread.
"""

def pid_control(bpm_track, initial_bpm, expected_start_time, actual_start_time):
    # Constants for PID control
    KP = 0.5  # Proportional gain
    KI = 0.1  # Integral gain
    KD = 0.2  # Derivative gain

    predicted_bpm = initial_bpm

    error = 0
    cumulative_error = 0

    start_time = actual_start_time
    previous_time = start_time

    while True:
        beat_interrupt = True  # Assuming a beat interrupt occurred

        current_time = time.time()
        elapsed_time = current_time - start_time

        expected_beat_time = predicted_bpm * elapsed_time / 60.0

        error = expected_beat_time - elapsed_time

        cumulative_error += error

        output = KP * error + KI * cumulative_error + KD * (error - (previous_time - current_time))

        predicted_bpm -= output

        # print("Elapsed Time: {:.2f}s, Predicted BPM: {:.2f}, Error: {:.2f}, Output: {:.2f}".format(
        #     elapsed_time, predicted_bpm, error, output))

        # Update the previous time
        previous_time = current_time

        time.sleep(0.1)  

# # Example usage
# bpm_track = 120  # BPM of the track
# initial_bpm = 200  # Initial predicted BPM
# expected_start_time = 5.0  # Expected start time in seconds
# actual_start_time = time.time()  # Actual start time

# pid_control(bpm_track, initial_bpm, expected_start_time, actual_start_time)


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

def split_file(x,sr,time,tempo):
    '''
    Split the input audio file into multiple chunks based on time and tempo.

    Args:
    - x: Soundfile data (numpy array)
    - sr: Sample rate (integer)
    - time: List of time boundaries (seconds)
    - tempo: List of tempos (beats per minute)

    Returns:
    - x_split: List of audio chunks
    - scale: List of scaling factors
    '''
    x_split = []
    scale = []
    temp = []
    time.append((x.shape[-1])/sr)
    for i in range(len(time)-1):
        i1 = int(time[i]*sr)
        i2 = int((time[i+1]*sr)+1)
        # Split the audio into chunks
        print(i1,i2)
        temp = x[:,i1:i2].copy()
        print(temp)
        x_split.append(temp)
        # Calculate the scaling factor based on tempo
        scale.append(120/tempo[i])
    return(x_split, scale)

def time_stretch(input_file, pairs):
    '''
    Time-stretch an audio file based on specified time and tempo pairs.

    Args:
    - input_file: Path to the input WAV file
    - pairs: List of time and tempo pairs [(time, tempo), ...]

    Returns:
    - x_output: Time-stretched audio data
    - sr: Sample rate
    '''
    x,sr = sf.read(input_file) #gets data and sample rate
    x = x.T
    print("length:",len(x[0]),"sr:",sr,"time:",(len(x[0])/sr))
    print(x)
    #gets data from pair
    time = pairs[0]
    bpm = pairs[1]
    #insert starting data
    time.insert(0,0) 
    bpm.insert(0,120)

    x_split,scale = split_file(x,sr,time,bpm) #splits data into multiple chunks
    x_output = np.array([[],[]])
    for i in range(len(x_split)):
        print("period:",i)
        print(x_split[i],scale[i])
        x_output = np.concatenate((x_output,(tsm.hptsm(x_split[i],scale[i]))),axis = 1) #added each chunks scaled
        print("current length: ",(len(x_output[0])/sr))
    return (x_output,sr)

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