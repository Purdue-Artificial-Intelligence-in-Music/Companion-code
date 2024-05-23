import threading
import time
from AudioThreadWithBuffer import AudioThreadWithBuffer
import speech_recognition as sr
import pyttsx3
import numpy as np
from nltk.stem import PorterStemmer
from transformers import pipeline


class VoiceAnalyzerThread(threading.Thread):
    def __init__(self, name, AThread, voice_length=3):
        super(VoiceAnalyzerThread, self).__init__()
        self.name = name
        self.AThread = AThread
        self.stop_request = False
        self.r = sr.Recognizer()
        self.ps = PorterStemmer()
        self.output = ""
        self.voice_length = voice_length
        # Initialize whatever stuff you need here

    def convert_to_AudioData(self, nparr):
        # sample_width=2 relies on the fact that AudioThreadWithBuffer's format is PyAudio.paInt16, which has 16 bits
        return sr.AudioData(frame_data=nparr.tobytes(), 
                            sample_rate=self.AThread.RATE, 
                            sample_width=2)

    # Function to convert text to
    # speech
    def SpeakText(command):
        # Initialize the engine
        engine = pyttsx3.init()
        engine.say(command)
        engine.runAndWait()

    def getSpeech(self, audio):
        # Exception handling to handle
        # exceptions at the runtime
        try:
            # Using google to recognize audio

            # Initialize the zero-shot classification pipeline with the Roberta model
            classifier = pipeline('zero-shot-classification', model='roberta-large-mnli')
            
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
                "edit": "The action involves changing something."
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

            #Preset to "edit" since that's the key to adding/changing a command
            myCommand = "edit"
            
            # First check for any negation adjustments
            for phrase, command in adjustments.items():
                if phrase in spokenWords.lower():
                    myCommand = command

            # Next, check for direct action phrase mappings
            for phrase, command in action_phrases.items():
                if phrase in spokenWords.lower():
                    myCommand = command

            #If no new command was grabbed then act upon the edit
            if (myCommand == "edit"):
                print("No command found for what you said, please define your command")
                
                name = spokenWords

                MyText = self.r.recognize_google(audio)
                MyText = MyText.lower()
                yourDesc = np.array(MyText.split())
            
                commands[name] = yourDesc


            # If no special cases, proceed with model classification
            hypotheses = [f"The action is: {desc}" for desc in commands.values()]
            result = classifier(spokenWords, hypotheses, multi_label=True) # Changed multi_class to multi_label
            highest_score = max(result['scores'])
            highest_scoring_command = [cmd for cmd, desc in commands.items() if f"The action is: {desc}" == result['labels'][result['scores'].index(highest_score)]][0]

            # relevantWord = []
            # for i in commands:
            #     for j in range(len(spokenWords) - 1):
            #         if (self.ps.stem(spokenWords[j]) == i):
            #             relevantWord.append(i)
            #         if ((self.ps.stem(spokenWords[j]) + " " + self.ps.stem(spokenWords[j + 1]) == i)):
            #             relevantWord.append(i)
            # print(relevantWord)
            self.output = highest_scoring_command
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
            smp = self.AThread.get_last_samples(self.AThread.RATE * self.voice_length)
            if len(smp) >= self.AThread.RATE * self.voice_length / 2.0:
                self.getSpeech(self.convert_to_AudioData(smp))
            time.sleep(self.voice_length)

def main():
    #Todo: Change to your file path
    AThread = AudioThreadWithBuffer(name="AThread", starting_chunk_size=1024, 
                                    wav_file = "C:\\Users\\Eddie\\Downloads\\IMG_8791.wav",
                                    process_func=(lambda x, y, z: z))
    VThread = VoiceAnalyzerThread(AThread=AThread, name = "Vthread")
    try:
        AThread.start()
        VThread.start()
    except KeyboardInterrupt:
        AThread.stop_request = True
        VThread.stop_request = True


if __name__ == "__main__":
    main()
