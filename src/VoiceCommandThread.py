import threading
import time

import numpy
import speech_recognition as sr
import numpy as np
from nltk.stem import PorterStemmer

class VoiceCommandThread(threading.Thread):
    def __init__(self, name, AThread, commands=None):
        super(VoiceCommandThread, self).__init__()
        self.name = name
        self.AThread = AThread
        self.commands = ["speed", "go to", "exit", "start", ""]
        if commands is not None:
            self.commands = commands
        self.stop_request = False
        self.r = sr.Recognizer()
        self.output = []

    def getSpeech(self, data: numpy.ndarray):
        ps = PorterStemmer()
        try:
            #self.r.adjust_for_ambient_noise(source2, duration=0.2) Commented out
            audio2 = sr.AudioData(data.tobytes(), sample_rate=self.AThread.RATE, sample_width=2)
            MyText = self.r.recognize_google(audio2)
            MyText = MyText.lower()
            spokenWords = np.array(MyText.split())
            relevantWord = []
            for i in self.commands:
                for j in range(len(spokenWords) - 1):
                    if ps.stem(spokenWords[j]) == i:
                        relevantWord.append(i)
                    if ps.stem(spokenWords[j]) + " " + ps.stem(spokenWords[j + 1]) == i:
                        relevantWord.append(i)
            return relevantWord
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print("unknown error occurred")
        return []

    def run(self):
        time.sleep(0.5)
        while not self.stop_request:
            mic_samples = self.AThread.get_last_samples(220500) # 5 seconds
            if not (len(mic_samples) < 100000):
                self.output = self.getSpeech(mic_samples)
            time.sleep(1.0)