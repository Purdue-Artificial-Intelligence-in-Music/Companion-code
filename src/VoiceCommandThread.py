import threading
import time
import AudioThreadWithBuffer
import speech_recognition as sr
import pyttsx3
import numpy as np
from nltk.stem import PorterStemmer


class VoiceAnalyzerThread(threading.Thread):
    def __init__(self, name, AThread):
        super(VoiceAnalyzerThread, self).__init__()
        self.name = name
        self.AThread = AThread
        self.stop_request = False
        self.r = sr.Recognizer()
        self.ps = PorterStemmer()
        self.output = ""
        # Initialize whatever stuff you need here

    # Function to convert text to
    # speech
    def SpeakText(command):
        # Initialize the engine
        engine = pyttsx3.init()
        engine.say(command)
        engine.runAndWait()

    def getSpeech(self, audio2):
        # Exception handling to handle
        # exceptions at the runtime
        try:
            # Using google to recognize audio
            MyText = self.r.recognize_google(audio2)
            MyText = MyText.lower()
            spokenWords = np.array(MyText.split())
            commands = ["speed", "go to", "exit", "start", ""]
            relevantWord = []
            for i in commands:
                for j in range(len(spokenWords) - 1):
                    if (self.ps.stem(spokenWords[j]) == i):
                        relevantWord.append(i)
                    if ((self.ps.stem(spokenWords[j]) + " " + self.ps.stem(spokenWords[j + 1]) == i)):
                        relevantWord.append(i)
            print(relevantWord)
            self.output = relevantWord
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            self.stop_request = True
        except sr.UnknownValueError:
            print("unknown error occurred")
            self.stop_request = True
        self.output = ""

    def run(self):
        # Do beat detection
        time.sleep(0.5)
        while not self.stop_request:
            samples = self.AThread.get_last_samples(self.AThread.RATE)
            self.getSpeech(samples)
            time.sleep(2)
