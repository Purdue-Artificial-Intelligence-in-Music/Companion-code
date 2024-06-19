from AudioThread import *
import pyaudio
import time
import numpy as np
import pandas as pd


'''
    This class uses the AudioThread class to listen to audio and create an audio buffer
'''
class Listener:
    
    def __init__(self):
        self.buffer = np.empty(0)
    
    '''
    Takes in a duration in seconds and listens. Fills a buffer with audio values
    NOTE there is currently no measure against too much input. Will fill buffer forever
    Duration is checked every one second and a half. (Avoids unable to stop condition)
    NOTE don't call listen() twice since buffer is a static variable
    
    :params duration: Duration in seconds to listen for
    :return: Audio buffer
    '''
    def listen(self, duration=10):
        self.buffer = np.empty(0) #will fill this buffer
        #Creates a thread for class
        self.my_thread = AudioThreadWithBufferPorted('my thread', rate=44100, starting_chunk_size=1024, process_func=self._callback)
        start = time.time()
        try: 
            self.my_thread.start()
            print("Start thread")
            while True:
                print("listening")
                time.sleep(1.5) #Check every second
                
                #only let thread run for duration
                if time.time() - start > duration:
                    self.my_thread.stop()
                    break
                    
        except KeyboardInterrupt:
            self.my_thread.stop()
        print('stopped')
        #manually stopping it is also causing the same problems??
        
        return self.buffer
    
    '''
    Helper function that takes in audio input to fill a given numpy buffer
    
    :param arg: data passed from AudioThread
    :param buffer: buffer to fill with data
    '''
    def _callback(self, arg):
        self.buffer = np.append(self.buffer, arg)
