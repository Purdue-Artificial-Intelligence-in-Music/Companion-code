import threading
import time
from AudioThreadWithBuffer import AudioThreadWithBuffer
import speech_recognition as sr
import pyttsx3
import numpy as np
from nltk.stem import PorterStemmer


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
            
            MyText = self.r.recognize_google(audio)
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
        time.sleep(0.5)
        while not self.stop_request:
            smp = self.AThread.get_last_samples(self.AThread.RATE * self.voice_length)
            if len(smp) >= self.AThread.RATE * self.voice_length / 2.0:
                self.getSpeech(self.convert_to_AudioData(smp))
            time.sleep(self.voice_length)

def main():
    AThread = AudioThreadWithBuffer(name="AThread", starting_chunk_size=1024, 
                                    wav_file = "C:\\Users\\shris\\Downloads\\IMG_8791.wav",
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
