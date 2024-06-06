from BeatNet_local.BeatNet_thread import BeatNet_thread
from WavBeatTracker import *
from AudioBuffer import *
from VoiceCommandThread import *
import pytsmod as tsm
from process_funcs import *
from xml2midi_conversion import process_score
from ddsp_funcs import generate_audio_from_midi
import traceback
import sys
import midi_ddsp
import pretty_midi
import os

FRAMES_PER_BUFFER = 1024

def main():
    buffer = None
    beat_detector = None
    wav_beat_tracker = None
    voice_recognizer = None

    try:
        while True:
            '''
            Main menu
            '''

            print("What would you like to do?")
            print("1) Play along with Companion")
            print("2) Generate an accompaniment audio file")
            print("3) Change debug options")
            user_choice = input("")
            if input == "1":
                while True:
                    accomp_audio_path = input("What is the path to your accompaniment audio? (.wav supported)")
                    if accomp_audio_path[-4:] == ".wav":
                        break
                    print("Invalid file name")
                
                while True:
                    score_path = input("What is the path to your score? (Uncompressed .musicxml supported)")
                    if score_path[-9:] == ".musicxml":
                        break
                    print("Invalid score")

                buffer = AudioBuffer(name="buffer", 
                            frames_per_buffer=FRAMES_PER_BUFFER,
                            wav_file=accomp_audio_path,
                            process_func=process_func,
                            process_func_args=(),
                            calc_beats=True,
                            debug_prints=True,
                            time_stretch=True,
                            kill_after_finished=True,
                            output_path="./src/wav_output.wav")
                beat_detector = BeatNet_thread(model=1, BUFFER=buffer, plot=[], device='cpu')
                wav_beat_tracker = WavBeatTracker(BUFFER=buffer)
                voice_recognizer = VoiceAnalyzerThread(name="voice_recognizer",
                                                    BUFFER=buffer,
                                                    voice_length=3)
                buffer.daemon = True
                beat_detector.daemon = True
                wav_beat_tracker.daemon = True
                voice_recognizer.daemon = True
                print("All thread objects initialized")
                buffer.start()
                print("Buffer started")
                beat_detector.start()
                print("Beat detector started")
                wav_beat_tracker.start()
                print("Wav beat tracker started")
                voice_recognizer.start()
                print("Voice recognizer started")
                while not buffer.stop_request:
                    print("Mic beats: %d" % (beat_detector.get_total_beats()))
                    print("Wav beats: %d" % (wav_beat_tracker.get_total_beats()))
                    time.sleep(0.5)

            elif input == "2":
                #import sys
                #sys.path.append('./midi-ddsp/')

                # Define the path or paths of the model weights or relevant files you expect after downloading
                expected_file_path = './midi_ddsp_model_weights_urmp_9_10'  # Adjust this to your file's expected location

                # Save the current working directory
                original_dir = os.getcwd()

                # Get the path to the midi_ddsp package
                package_path = os.path.dirname(midi_ddsp.__file__)
                print(f"Package directory: {package_path}")

                # Change to the package directory
                os.chdir(package_path)

                # Check if the model weights or relevant files already exist
                if not os.path.exists(expected_file_path):
                    print("Downloading model weights...")
                    # Execute the script to download model weights
                    %run download_model_weights.py
                else:
                    print("Model weights already exist. No need to download.")

                # Return to the original directory
                os.chdir(original_dir)
                print(f"Returned to original directory: {os.getcwd()}")

                #@title #Install Dependencies, Import Code and Setup Models

                #@markdown Run this cell to install dependencies, import codes, 
                #@markdown setup utility functions and load MIDI-DDSP model weights.
                #@markdown Running this cell could take a while.
                # %pip install -q git+https://github.com/lukewys/qgrid.git

                # # !pip install -q git+https://github.com/magenta/midi-ddsp
                import os

                # !!! Run these once
                if not os.path.exists('./midi-ddsp') or not os.path.exists('./FluidR3_GM.zip'):
                    # Your commands
                    !git clone -q https://github.com/magenta/midi-ddsp.git
                    !wget -q https://keymusician01.s3.amazonaws.com/FluidR3_GM.zip
                    !unzip -q FluidR3_GM.zip
                else:
                    print('The required resources are already present.')

                # Ignore a bunch of deprecation warnings
                sys.path.append('./midi-ddsp')
                import warnings
                warnings.filterwarnings("ignore")

                import librosa
                import matplotlib.pyplot as plt
                import numpy as np
                import tensorflow.compat.v2 as tf
                import pandas as pd
                import qgrid
                import music21
                from IPython.display import Javascript
                import IPython.display as ipd

                from midi_ddsp import load_pretrained_model
                from midi_ddsp.utils.training_utils import set_seed, get_hp

                set_seed(1234)
                sample_rate = 16000

                synthesis_generator, expression_generator = load_pretrained_model()

                print('Done!')

                while True:
                    score_path = input("What is the path to your score? (Uncompressed .musicxml supported)")
                    if score_path[-9:] == ".musicxml":
                        break
                    print("Invalid score")
                accomp_audio_path = input("Which folder do you want your accompaniment audio to be saved in?")
                midi_output = None
                audio = None

                try:
                    midi_output = process_score(score_path)
                except KeyboardInterrupt:
                    raise KeyboardInterrupt("Keyboard interrupt")
                except Exception:
                    raise Exception("Error processing score in Music21. Is your musicxml compressed?")
                if midi_output is not None:
                    try:
                        audio, conditioning_df, midi_synth_params = generate_audio_from_midi(synthesis_generator, 
                                                                                             expression_generator, 
                                                                                             midi_output, 
                                                                                             inst="violin", 
                                                                                             inst_num=0)
                    except KeyboardInterrupt:
                        raise KeyboardInterrupt("Keyboard interrupt")
                    except Exception:
                        raise Exception("Error generating audio from MIDI-DDSP")
                if audio is not None:
                    soundfile.write(os.path.join(os.getcwd, "generated_audio.wav"), audio, samplerate=sample_rate)
                print("Audio generation done! Audio saved to ", os.path.join(os.getcwd, "generated_audio.wav"))

            elif input == "3":
                print("There are no debug options currently")
            else:
                print("Invalid menu choice")
        
    except KeyboardInterrupt:
        print("Detected keyboard interrupt")
    except Exception as e:
        print("Exception occurred")
        print(traceback.format_exception(None, # <- type(e) by docs, but ignored 
                                     e, e.__traceback__),
          file=sys.stderr, flush=True)
    if buffer is not None:
        buffer.stop()
        buffer.join()

    print("Program done")


if __name__ == "__main__":
    main()
