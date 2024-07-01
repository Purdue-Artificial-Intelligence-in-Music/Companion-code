from AudioThread import AudioThread
import time
import numpy as np

STARTING_CHUNK = 1024

def process_func(data):
    # Does nothing
    return

def main():
    AThread = AudioThread(name="SPA_Thread", starting_chunk_size=STARTING_CHUNK, process_func=process_func)
    print("All threads init'ed")
    try:
        AThread.start()
        print("============== AThread started")
        while True:
            print(AThread.input_on)
            time.sleep(1.5)
    except KeyboardInterrupt:
        AThread.stop_request = True


if __name__ == "__main__":
    main()
