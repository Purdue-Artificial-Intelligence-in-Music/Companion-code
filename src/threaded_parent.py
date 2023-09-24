from AudioThread import AudioThread
import time

STARTING_CHUNK = 1024


def process_func(audio):
    # Do something cool here!
    return


def main():
    try:
        AThread = AudioThread(name="SPA_Thread", starting_chunk_size=STARTING_CHUNK, process_func=process_func)
        print("All threads init'ed")
        AThread.start()
        print("============== AThread started")
        while True:
            # Do something here!
            time.sleep(0.1)
    except KeyboardInterrupt:
        AThread.stop_request = True


if __name__ == "__main__":
    main()
