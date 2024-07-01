import traceback
import sys
import yaml
import os
import time
from print_commands import *

# https://stackoverflow.com/questions/69345114/read-input-from-keyboard-without-waiting-for-enter
# WAV_FILE = "C:\\Users\\TPNml\\OneDrive\\remix 11 x1.wav"
WAV_FILE = "C:\\Users\\TPNml\Downloads\\bcr 22050.wav"

YAML_PATH = "./src/config.yml"


def main():
    buffer = None
    beat_detector = None
    wav_beat_tracker = None
    voice_recognizer = None

    try:
        while True:
            clear_terminal()
            
            '''
            Main menu
            '''

            print("What would you like to do?")
            print("1) Play along with Companion")
            print("2) Generate an accompaniment audio file")
            print("3) Change debug options")
            print("4) Exit")
            user_choice = input("")
            if user_choice == "1":
                clear_terminal()
                print("--- Play along with Companion -------------\n")
                with open(YAML_PATH, 'r') as yaml_file:       
                    CONFIG_DICT = yaml.load(yaml_file, Loader=yaml.CLoader)
                    while True:
                        accomp_audio_path = input("What is the path to your accompaniment audio? (.wav supported) ")
                        if accomp_audio_path[-4:] == ".wav":
                            break
                        print("Invalid file name")
                    
                    while True:
                        score_path = input("What is the path to your score? (Uncompressed .musicxml supported) ")
                        if score_path[-9:] == ".musicxml":
                            break
                        print("Invalid score")
                    print("Loading...")
                    from BeatNet_local.BeatNet_thread import BeatNet_thread, BeatSynchronizer
                    from WavBeatTracker import WavBeatTracker
                    from AudioBuffer import AudioBuffer
                    from VoiceCommandThread import VoiceAnalyzerThread
                    from process_funcs import save_wav_volume
                    import numpy as np
                    buffer = AudioBuffer(name="buffer", 
                         frames_per_buffer=CONFIG_DICT["FRAMES_PER_BUFFER"],
                         wav_file=accomp_audio_path,
                         process_func=save_wav_volume,
                         process_func_args=(),
                         calc_transforms=False, 
                         calc_beats=True,
                         run_counter=True,
                         kill_after_finished=True,
                         time_stretch=True,
                         playback_rate=1.0,
                         sr_no_wav=22050,
                         dtype_no_wav=np.float32,
                         channels_no_wav=1,
                         debug_prints=False,
                         output_path="./src/wav_output.wav")
    
                    beat_detector = BeatNet_thread(model=1, buffer=buffer, plot=[], device='cpu')
                    wav_beat_tracker = WavBeatTracker(player=buffer)
                    beat_sync = BeatSynchronizer(player_beat_thread=beat_detector, accomp_beat_thread=wav_beat_tracker)
                    buffer.time_stretch_source = beat_sync
                    # voice_recognizer = VoiceAnalyzerThread(name="voice_recognizer",
                    #                                       BUFFER=buffer,
                    #                                       voice_length=3)
                    buffer.daemon = True
                    beat_detector.daemon = True
                    wav_beat_tracker.daemon = True
                    # voice_recognizer.daemon = True
                    #print("All thread objects initialized")
                    buffer.start()
                    #print("Buffer started")
                    beat_detector.start()
                    #print("Beat detector started")
                    wav_beat_tracker.start()
                    #print("Wav beat tracker started")
                    beat_sync.start()
                    #print("Beat synchronizer started")
                    # voice_recognizer.start()
                    # print("Voice recognizer started")
                    minutes_long = int(buffer.wav_len / buffer.RATE / 60)
                    seconds_long = int(buffer.wav_len / buffer.RATE) % 60
                    start_time = time.time()
                    #print("", end="")
                    while not buffer.stop_request:
                        '''
                        GUI stuff
                        '''
                        clear_terminal()
                        elapsed_time = time.time() - start_time
                        minutes_elapsed_in_wav = int(buffer.wav_index / buffer.RATE / 60)
                        seconds_elapsed_in_wav = int(buffer.wav_index / buffer.RATE) % 60
                        print("================== Companion: now playing %s ==================\n" % (accomp_audio_path))
                        print("    Time ", end="")
                        print_one_directional_bar(width = 20, portion_filled = buffer.wav_index / buffer.wav_len)
                        print("\n                              ", end="")
                        print("%d:%02d out of %d:%02d\n" % (minutes_elapsed_in_wav, seconds_elapsed_in_wav, minutes_long, seconds_long))
                        print("   Tempo ", end="")
                        print_two_directional_bar(width = 4, portion_filled = 1.0 - beat_sync.playback_rate)
                        print("     Error ", end="")
                        print_two_directional_bar(width = 4, portion_filled = (beat_detector.get_total_beats() - wav_beat_tracker.get_total_beats())/10.0)
                        print("\n                   %.1f%%                               %.2f\n" % (beat_sync.playback_rate * 100, beat_detector.get_total_beats() - wav_beat_tracker.get_total_beats()))
                        #print("  Volume ", end="")
                        #db = 0.0
                        #if buffer.wav_chunk_rms_volume is not None:
                        #    db = librosa.amplitude_to_db(buffer.wav_chunk_rms_volume)
                        #print_one_directional_bar(width = 8, portion_filled = (db + 36.0) / 36.0)
                        #print("\n                   %.1fdB\n" % (db))
                        # print("Last command heard: %s")
                        time.sleep(0.1)

            elif user_choice == "2":
                clear_terminal()

                current_dir = os.getcwd()
                print("--- Generate an accompaniment audio file -------------\n")
                while True:
                    score_path = input("What is the path to your score? (Uncompressed .musicxml supported) ")
                    if score_path[-9:] == ".musicxml":
                        break
                    print("Invalid score")

                from xml2midi_conversion import process_score

                with open(YAML_PATH, 'r') as yaml_file:
                    CONFIG_DICT = yaml.load(yaml_file, Loader=yaml.CLoader)

                    midi_output = None
                    audio = None
                    score_path = os.path.abspath(score_path)

                    os.chdir(current_dir)
                    import numpy as np

                    try:
                        midi_output = process_score(score_path[:-9])
                    except KeyboardInterrupt:
                        raise KeyboardInterrupt("Keyboard interrupt")
                    except Exception:
                        raise Exception("Error processing score in Music21. Is your musicxml compressed?")
                    if midi_output is not None:
                        if os.path.exists(score_path[:-9] + "_generated_audio.npy"):
                            audio = np.load(score_path[:-9] + "_generated_audio.npy")
                            print("Loaded generated .npy from file to save on generation time")
                        else:
                            try:
                                from ddsp_funcs import init_ddsp, synthesize_midi_using_artics
                                synth_gen, express_gen = init_ddsp()
                                audio = synthesize_midi_using_artics(synth_gen, express_gen, midi_output)
                            except KeyboardInterrupt:
                                raise KeyboardInterrupt("Keyboard interrupt")
                            except Exception:
                                raise Exception("Error generating audio from MIDI-DDSP")
                    if audio is not None:
                        np.save(score_path[:-9] + "_generated_audio.npy", audio)
                        from scipy.signal import resample
                        import soundfile
                        from ddsp_funcs import DDSP_SAMPLE_RATE
                        audio = audio.T.squeeze()
                        resampled_audio = resample(audio, int(len(audio) / float(DDSP_SAMPLE_RATE) * CONFIG_DICT["DDSP_SAMPLE_RATE"]), axis=0)
                        soundfile.write(os.path.join(current_dir, "generated_audio.wav"), resampled_audio, samplerate=CONFIG_DICT["DDSP_SAMPLE_RATE"])
                        print("Audio generation done! Audio saved to ", os.path.join(os.getcwd(), "generated_audio.wav"))
                    else:
                        print("No audio generated")
                    
                input("Press Enter to continue...")

            elif user_choice == "3":
                clear_terminal()
                print("--- Change debug options -------------\n")
                with open(YAML_PATH, 'r+') as yaml_file:       
                    CONFIG_DICT = yaml.load(yaml_file, Loader=yaml.CLoader)
                    yaml_file.seek(0)
                    while True:
                        config_option = ""
                        print("Here is the current config option tree:")
                        print(CONFIG_DICT)
                        print()
                        while True:
                            found = False
                            config_option = input("Which config option would you like to change? Use \"/\" to go up a level in the key tree. You can also type \"exit\" to exit\n")
                            if config_option == "exit":
                                break
                            config_option_list = config_option.split("/")
                            try:
                                d = CONFIG_DICT
                                for o in config_option_list:
                                    d = d[o]
                                if not (type(d) == int or type(d) == float or type(d) == str):
                                    print("Your key is part of the tree and does not have an editable value. Use \"/\" to go further up in the tree to reach an editable key.\n")
                                else:
                                    found = True
                            except KeyError:
                                print("Invalid key\n")
                            if found == True:
                                break
                        if config_option == "exit":
                            break
                        value = input("What would you like to set this key's value to?\n")
                        d = CONFIG_DICT
                        for o in config_option_list[:-1]:
                            d = d[o]
                        try:
                            val = int(value)
                            value = val
                        except ValueError as ignored:
                            try:
                                val = float(value)
                                value = val
                            except ValueError as ignored:
                                pass
                        d[config_option_list[-1]] = value
                        print()
                    yaml.dump(CONFIG_DICT, yaml_file, default_flow_style=False)
                    yaml_file.truncate()
            elif user_choice == "4" or user_choice == "exit":
                break
            else:
                print("Invalid menu choice")
    except KeyboardInterrupt:
        print("\n\n--- Detected keyboard interrupt -------------\n")
    except Exception as e:
        print("\n\n--- Exception occured -------------\n")
        traceback.print_exception(None, e, e.__traceback__,
          file=sys.stderr)
        if buffer is not None:
            buffer.stop()
            buffer.join()
        
        # print("Press Enter to continue...")
        # input()
        # main()

    print("\n\n--- End of program -------------\n")


if __name__ == "__main__":
    main()
