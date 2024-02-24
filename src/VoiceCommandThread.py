"""
This file defines the VoiceAnalyzerThread class, which facilitates speech recognition and intent detection within audio streams 
using Google's Dialogflow and speech_recognition libraries. Key functionalities include converting text to speech, detecting intents 
from texts, and processing speech to extract relevant commands.
"""


import threading
import time
import AudioThreadWithBuffer
import speech_recognition as sr
import pyttsx3
import numpy as np
from nltk.stem import PorterStemmer
import dialogflow


class VoiceAnalyzerThread(threading.Thread):
    """A thread class for analyzing voice commands using Dialogflow and speech recognition."""
    def __init__(self, name, AThread, project_id, session_id, language_code="en-US"):
        """Initializes the voice analyzer thread with required parameters."""
        super(VoiceAnalyzerThread, self).__init__()
        self.name = name
        self.AThread = AThread
        self.project_id = project_id
        self.session_id = session_id
        self.language_code = language_code
        self.session_client = dialogflow.SessionsClient()
        self.session = self.session_client.session_path(project_id, session_id)
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

    def detect_intent_texts(self, text):
        """Returns the result of detect intent with texts as inputs."""
        text_input = dialogflow.TextInput(text=text, language_code=self.language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        response = self.session_client.detect_intent(session=self.session, query_input=query_input)
        return response.query_result

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

    # Main method to be executed by the thread
    def run(self):
        # Do beat detection
        time.sleep(0.5)
        while not self.stop_request:
            samples = self.AThread.get_last_samples(self.AThread.RATE)
            self.getSpeech(samples)
            time.sleep(2)
