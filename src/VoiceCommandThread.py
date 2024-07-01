import threading
import time
from AudioBuffer import AudioBuffer
import speech_recognition as sr
import pyttsx3
import numpy as np
from nltk.stem import PorterStemmer
from transformers import pipeline

import argparse
import queue
import sys
import sounddevice as sd
import json

from vosk import Model, KaldiRecognizer


class VoiceAnalyzerThread(threading.Thread):
    def __init__(self, name: str, BUFFER: AudioBuffer, voice_length=3):
        super(VoiceAnalyzerThread, self).__init__()
        self.name = name
        self.BUFFER = BUFFER
        self.stop_request = False
        self.r = sr.Recognizer()
        self.ps = PorterStemmer()
        self.output = ""
        self.voice_length = voice_length
        # Initialize whatever stuff you need here

        #The following are all related to the use of Vosk and voice commanding
        self.q = queue.Queue()

        # Define the list of possible commands along with hypothesis templates
        self.commands = {
            "stop": "The action involves bringing something to a halt.",
            "start": "The action involves beginning something.",
            "exit": "The action involves the termination of something.",
        }

        # Initialize the zero-shot classification pipeline with the Roberta model
        self.classifier = pipeline('zero-shot-classification', model='roberta-large-mnli')

    def convert_to_AudioData(self, arr: np.ndarray):
        # sample_width=2 relies on the fact that AudioThreadWithBuffer's format is PyAudio.paFloat32, which has 4 bytes per sample
        return sr.AudioData(frame_data=arr.tobytes(), 
                            sample_rate=self.BUFFER.RATE, 
                            sample_width=4)
    
    def int_or_str(text):
    #Helper function for argument parsing.
        try:
            return int(text)
        except ValueError:
            return text
    
    def callback(self, indata, frames, time, status):
    #This is called (from a separate thread) for each audio block.
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    # Enhance the classify_command function to handle a wider range of negations
    def classify_command(self, user_input):
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

        if command == "start":

            #Check if audio is playing
            self.BUFFER.audio_on()
            #If audio is not playing from the AudioBuffer, then start playing audio
                            
            if self.BUFFER.input_on() is False:
                    print("Turning on audio")
                    self.BUFFER.unpause()

        elif command == "stop":

            print("stop")
            #Still run Buffer in the background, but don't play audio
            self.BUFFER.pause()

        elif command == "exit":

            print("Detected interrupt")
            #Stop both voice and buffer
            self.stop_request = True
            self.BUFFER.stop()

        else:
            #TODO
            print("Run the user's defined command")


    # Function to convert text to
    # speech
    def SpeakText(command: str):
        # Initialize the engine
        engine = pyttsx3.init()
        engine.say(command)
        engine.runAndWait()

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
                #Check if audio is playing
                self.BUFFER.audio_on()
                #If audio is not playing from the AudioBuffer, then start playing audio
                if self.BUFFER.input_on() is False:
                    print("Turning on audio")
                    self.BUFFER.unpause()

            elif self.output == "stop":

                print("stop")
                #Still run Buffer in the background, but don't play audio
                self.BUFFER.pause()

            elif self.output == "exit":

                print("Detected interrupt")
                #Stop both voice and buffer
                self.stop_request = True
                self.BUFFER.stop()

            else:
                #TODO
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
        time.sleep(0.5)

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
                    if rec.AcceptWaveform(data):
                        #Print the result
                        print(rec.Result())

                        #Parse the json text and find the command
                        res = json.loads(rec.Result())
                        print(res['text'])
                        if res['text'] != "":
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
            self.BUFFER.stop()
            parser.exit(0)
            
        except Exception as e:
            parser.exit(type(e).__name__ + ": " + str(e))

def main():
    #Todo: Change to your file path
    AThread = AudioBuffer(name="AThread", frames_per_buffer=1024, 
                                    wav_file = "new_src\hunt.wav",
                                    process_func=(lambda x, y, z: z))
    VThread = VoiceAnalyzerThread(BUFFER=AThread, name = "Vthread")
    try:
        AThread.start()
        VThread.start()
    except KeyboardInterrupt:
        AThread.stop_request = True
        VThread.stop_request = True


if __name__ == "__main__":
    main()
