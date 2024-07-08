import threading
import time
from buffer import AudioBuffer
from AudioPlayer import AudioPlayer
import speech_recognition as sr         #Defunct?
import pyttsx3                          #Defunct?
import numpy as np
from nltk.stem import PorterStemmer     #Defunct?
from transformers import pipeline

import argparse
import queue
import sys
import sounddevice as sd
import json

from vosk import Model, KaldiRecognizer


class VoiceAnalyzerThread(threading.Thread):
    def __init__(self, name: str, buffer: AudioBuffer, player: AudioPlayer, voice_length=3):
        super(VoiceAnalyzerThread, self).__init__()
        self.name = name
        self.buffer = buffer
        self.player = player
        self.stop_request = False
        self.r = sr.Recognizer()        #Defunct?
        self.ps = PorterStemmer()       #Defunct?
        self.output = ""
        self.voice_length = voice_length #Defunct?
        # Initialize whatever stuff you need here

        #The following are all related to the use of Vosk and voice commanding
        self.q = queue.Queue()

        # Define the list of possible commands along with hypothesis templates
        self.commands = {
            "speed up": "The action involves increasing speed.",
            "slow down": "The action involves decreasing speed.",
            "volume up": "The action involves increasing volume.",
            "volume down": "The action involves decreasing volume.",
            "stop": "The action involves bringing something to a halt.",
            "start": "The action involves beginning something.",
            "exit": "The action involves the termination of something.",
            #"edit": "The action involves changing something."
        }

        # Initialize the zero-shot classification pipeline with the Roberta model
        self.classifier = pipeline('zero-shot-classification', model='roberta-large-mnli')

    def convert_to_AudioData(self, arr: np.ndarray): #Defunct?
        # sample_width=2 relies on the fact that AudioThreadWithBuffer's format is PyAudio.paFloat32, which has 4 bytes per sample
        return sr.AudioData(frame_data=arr.tobytes(), 
                            sample_rate=self.buffer.sample_rate, 
                            sample_width=4)
    
    def int_or_str(text):
    #Helper function for argument parsing, it allows for numbers to be converted into ints
        try:
            return int(text)
        except ValueError:
            return text
    
    def callback(self, indata, frames, time, status):
        """
        This function is called whenever PyAudio recieves new audio. It adds the audio to the queue
        and stores the result in the field "data".
        This function should never be called directly.
        Parameters: none user-exposed
        Returns: Nothing, but it adds onto the queue
        """
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def classify_command(self, user_input):
        """
        This function is called whenever the partial reult gains a new element, where in it will
        determine using Roberta the most likely command to be called upon
        Parameters: user_input: a string that is the partial result
        Returns: highest_scoring_command: a string that is put into run_command to run the command
        """
        # Check for negations and adjust the command accordingly
        negations = ["don't", "do not", "please don't", "never", "no", "not"]
        # Adjustments for negations
        adjustments = {
            "don't stop": "start",
            "do not stop": "start",
            "never stop": "start",
            "don't go": "stop",
            "do not go": "stop",
            "never go": "stop",
        }
        # Action phrases that directly map to commands
        action_phrases = {
            "too fast": "slow down",
            "too slow": "speed up",
            "too loud": "volume down",
            "too quiet": "volume up",
            "go": "start",
            "halt": "stop",
            "be quiet": "volume down",
            "stop playing": "stop",  
            "pause": "stop", 
            "I can't hear": "volume up",
            "it's noisy": "volume down",
        }

        # First check for any negation adjustments
        for phrase, command in adjustments.items():
            if phrase in user_input.lower():
                return command

        # Next, check for direct action phrase mappings
        for phrase, command in action_phrases.items():
            if phrase in user_input.lower():
                return command

        # If no special cases, proceed with model classification
        hypotheses = [f"The action is: {desc}" for desc in self.commands.values()]
        result = self.classifier(user_input, hypotheses, multi_label=True) # Changed multi_class to multi_label
        highest_score = max(result['scores'])
        highest_scoring_command = [cmd for cmd, desc in self.commands.items() if f"The action is: {desc}" == result['labels'][result['scores'].index(highest_score)]][0]
        return highest_scoring_command
    
    def run_command(self, command):
        """
        This function is called after classify_command is called upon and uses the highest scoring command
        to enact whatever command was requested
        Parameters: command: a string that is the highest scoring command found by roberta
        Returns: Nothing, but acts upon the AudioBuffer to do various actions
        """
        if command == "start":

            #If audio is not playing from the AudioBuffer, then start playing audio
            print("start")
            self.buffer.unpause()
            self.player.unpause()

        elif command == "stop":

            print("stop")
            #Still run Buffer in the background, but don't play audio
            self.buffer.pause()
            self.player.pause()

        elif command == "exit":

            print("Detected interrupt")
            #Stop both voice and buffer
            self.stop_request = True
            self.buffer.stop()
            self.player.stop()

        else:
            #TODO: Look into ways to use LLM to create commands and have the code be able to run them
                #Maybe have the user provide smaller step by step requests to gain a better chance of the command working
                #^ like the idea provided by ()

                #Also possibly add an "Undo" command that can just reverse the last command sent?
                #But only for custom commands?
            print("Run the user's defined command")


    """
    #TODO: Verify this code isn't needed anymore and remove it
    """
    # Function to convert text to
    # speech
    def SpeakText(command: str):
        # Initialize the engine
        engine = pyttsx3.init()
        engine.say(command)
        engine.runAndWait()

    """
    #TODO: Verify this code isn't needed anymore and remove it as run now should just do this
    """
    def getSpeech(self, audio: sr.AudioData):
        # Exception handling to handle
        # exceptions at the runtime
        try:
            # Using google to recognize audio
            MyText = self.r.recognize_google(audio)
            MyText = MyText.lower()
            spokenWords = np.array(MyText.split())
            

            # TODO: Process the command and act upon the AudioBuffer
            # MVP: Get start and stop to work

            if self.output == "start":

                print("start")
                #If audio is not playing from the AudioBuffer, then start playing audio
                self.buffer.unpause()
                self.player.unpause()

            elif self.output == "stop":

                print("stop")
                #Still run Buffer in the background, but don't play audio
                self.buffer.pause()
                self.player.pause()

            elif self.output == "exit":

                print("Detected interrupt")
                #Stop both voice and buffer
                self.stop_request = True
                self.buffer.stop()
                self.player.stop()

            else:
                #TODO: Look into ways to use LLM to create commands and have the code be able to run them
                #Maybe have the user provide smaller step by step requests to gain a better chance of the command working
                #^ like the idea provided by ()

                #Also possibly add an "Undo" command that can just reverse the last command sent?
                #But only for custom commands?
                print("Run the user's defined command")

            self.output = ""

        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            self.stop_request = True
        except sr.UnknownValueError:
            print("unknown error occurred")
            self.stop_request = True

        self.output = ""

    def run(self):
        """
        This function is the driving force behind voice commanding, it will call upon classify command
        in order to find the best command for what was said and then run said command
        Parameters: nothing
        Returns: nothing
        """
        time.sleep(0.5)

        #TODO: Trim down the arg parser portion to what's needed to minimize faults

        #Activates the arguement parser so that Vosk can collect the spoken words using the SoundDevice library
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "-l", "--list-devices", action="store_true",
            help="show list of audio devices and exit")
        args, remaining = parser.parse_known_args()
        if args.list_devices:
            print(sd.query_devices())
            parser.exit(0)
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[parser])
        parser.add_argument(
            "-f", "--filename", type=str, metavar="FILENAME",
            help="audio file to store recording to")
        parser.add_argument(
            "-d", "--device", type=self.int_or_str,
            help="input device (numeric ID or substring)")
        parser.add_argument(
            "-r", "--samplerate", type=int, help="sampling rate")
        parser.add_argument(
            "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
        args = parser.parse_args(remaining)

        try:
            if args.samplerate is None:
                device_info = sd.query_devices(args.device, "input")
                # soundfile expects an int, sounddevice provides a float:
                args.samplerate = int(device_info["default_samplerate"])
                
            if args.model is None:
                #Using a specific model to improve correctness
                model = Model(model_name="vosk-model-en-us-0.22-lgraph")
            else:
                model = Model(lang=args.model)

            if args.filename:
                dump_fn = open(args.filename, "wb")
            else:
                dump_fn = None

            with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
                    dtype="int16", channels=1, callback=self.callback):
                print("#" * 80)
                print("Press Ctrl+C or say exit to stop the recording")
                print("#" * 80)

                rec = KaldiRecognizer(model, args.samplerate)
                while not self.stop_request:
                    data = self.q.get()

                    #Possible optimization would be jut to ignore Result entirely,
                    #but I don't think that would end up clearing the json buffer
                    # if rec.AcceptWaveform(data) is False:
                    #     print(rec.PartialResult())
                    #     #print()

                    #     #Possible optimization by using partials rather than whole
                    #     #Parse the json text and find the command
                    #     res = json.loads(rec.PartialResult())
                    #     print(res["partial"])
                    #     if res["partial"] != "":
                    #         #print(toParse)
                    #         toParse = self.classify_command(res["partial"])
                    #         self.run_command(toParse)

                    if rec.AcceptWaveform(data):
                        #Print the result
                        print(rec.Result())

                        #Parse the json text and find the command
                        res = json.loads(rec.Result())
                        print(res["text"])
                        if res["text"] != "":
                            #print(toParse)                
                            toParse = self.classify_command(res['text'])
                            self.run_command(toParse)

                    else:
                        print(rec.PartialResult())
                        #print()

                        #Possible optimization by using partials rather than whole
                        #Parse the json text and find the command
                        res = json.loads(rec.PartialResult())
                        print(res["partial"])
                        if res["partial"] != "":
                            #print(toParse)
                            toParse = self.classify_command(res["partial"])
                            self.run_command(toParse)

                    if dump_fn is not None:
                        dump_fn.write(data)

        except KeyboardInterrupt:
            print("\nDone")
            self.stop_request = True
            self.buffer.stop()
            self.player.stop()
            parser.exit(0)
            
        except Exception as e:
            parser.exit(type(e).__name__ + ": " + str(e))

# def main():
#     #Todo: Change to your file path
#     AThread = AudioBuffer(name="AThread", frames_per_buffer=1024, 
#                                     wav_file = "new_src\hunt.wav",
#                                     process_func=(lambda x, y, z: z))
#     VThread = VoiceAnalyzerThread(BUFFER=AThread, name = "Vthread")
#     try:
#         AThread.start()
#         VThread.start()
#     except KeyboardInterrupt:
#         AThread.stop_request = True
#         VThread.stop_request = True


# if __name__ == "__main__":
#     main()
