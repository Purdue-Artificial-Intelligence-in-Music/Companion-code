import threading
import time
from AudioBuffer import AudioBuffer
import speech_recognition as sr
import pyttsx3
import numpy as np
from nltk.stem import PorterStemmer
from transformers import pipeline


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

        # Initialize the zero-shot classification pipeline with the Roberta model
        self.classifier = pipeline('zero-shot-classification', model='roberta-large-mnli')

    def convert_to_AudioData(self, arr: np.ndarray):
        # sample_width=2 relies on the fact that AudioThreadWithBuffer's format is PyAudio.paFloat32, which has 4 bytes per sample
        return sr.AudioData(frame_data=arr.tobytes(), 
                            sample_rate=self.BUFFER.RATE, 
                            sample_width=4)

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
            # Define the list of possible commands along with hypothesis templates
            commands = {
                "speed up": "The action involves increasing speed.",
                "slow down": "The action involves decreasing speed.",
                "volume up": "The action involves increasing volume.",
                "volume down": "The action involves decreasing volume.",
                "stop": "The action involves bringing something to a halt.",
                "start": "The action involves beginning something.",
                "exit": "The action involves the termination of something.",
                # "edit": "The action involves changing something."
            }

            # Enhance the classify_command function to handle a wider range of negations
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
                # "don't do this": "edit",
                # "do not do this": "edit",
                # "never do this": "edit",
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
                # "fix": "edit",
                # "change": "edit",
                # "alter": "edit",
                # "modify": "edit",
            }

            # #Preset to "edit" since that's the key to adding/changing a command
            # myCommand = "edit"
            # toInsert = True
            
            # First check for any negation adjustments
            for phrase, command in adjustments.items():
                if phrase in spokenWords.lower():
                    command = command

            # Next, check for direct action phrase mappings
            for phrase, command in action_phrases.items():
                if phrase in spokenWords.lower():
                    command = command

            # #If no new command was grabbed then act upon the edit
            # if (myCommand == "edit"):
            #     print("No command found for what you said, please define your command")
                
            #     name = spokenWords

            #     MyText = self.r.recognize_google(audio)
            #     MyText = MyText.lower()
            #     yourDesc = np.array(MyText.split())

            #     # First check if this is just a new negation
            #     for phrase, command in adjustments.items():
            #         if yourDesc in spokenWords.lower():
            #             adjustments[name] = yourDesc
            #             toInsert = False

            #     # Next, check if its a new alterantive mapping
            #     for phrase, command in action_phrases.items():
            #         if yourDesc in spokenWords.lower():
            #             action_phrases[name] = yourDesc
            #             toInsert = False

            #     # Lastly, if it wasn't either then insert it properly into the commands list
            #     if (toInsert):
            #         commands[name] = yourDesc


            # If no special cases, proceed with model classification
            hypotheses = [f"The action is: {desc}" for desc in commands.values()]
            result = self.classifier(spokenWords, hypotheses, multi_label=True) # Changed multi_class to multi_label
            highest_score = max(result['scores'])
            highest_scoring_command = [cmd for cmd, desc in commands.items() if f"The action is: {desc}" == result['labels'][result['scores'].index(highest_score)]][0]

            # Now that the most optimal command has been determined... 
            self.output = highest_scoring_command

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
                self.stop()
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
        while not self.stop_request:
            smp = self.BUFFER.get_last_frames(self.BUFFER.RATE * self.voice_length)
            if len(smp) >= self.BUFFER.RATE * self.voice_length / 2.0:
                self.getSpeech(self.convert_to_AudioData(smp))
            time.sleep(self.voice_length)

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
