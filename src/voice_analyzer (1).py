# Written by Shrish Senthilkumar
import speech_recognition as sr
import pyttsx3
import numpy as np
from nltk.stem import PorterStemmer

# Initialize the recognizer
r = sr.Recognizer()


# Function to convert text to
# speech
def SpeakText(command):
    # Initialize the engine
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()


def getSpeech():
    ps = PorterStemmer()
    # Exception handling to handle
    # exceptions at the runtime
    try:
        # use the microphone as source for input.
        with sr.Microphone() as source2:
            # wait for a second to let the recognizer
            # adjust the energy threshold based on
            # the surrounding noise level
            r.adjust_for_ambient_noise(source2, duration=0.2)
            # listens for the user's input
            audio2 = r.listen(source2)
            # check the type of the output
            print(type(audio2))
            # Using google to recognize audio
            MyText = r.recognize_google(audio2)
            MyText = MyText.lower()
            spokenWords = np.array(MyText.split())
            commands = ["speed", "go to", "exit", "start", ""]
            relevantWord = []
            for i in commands:
                for j in range(len(spokenWords) - 1):
                    if (ps.stem(spokenWords[j]) == i):
                        relevantWord.append(i)
                    if ((ps.stem(spokenWords[j]) + " " + ps.stem(spokenWords[j + 1]) == i)):
                        relevantWord.append(i)
            print(relevantWord)
            return relevantWord
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
    except sr.UnknownValueError:
        print("unknown error occurred")
    return []


if __name__ == "__main__":
    getSpeech()
