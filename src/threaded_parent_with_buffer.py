from AudioThreadWithBuffer import AudioThreadWithBuffer
import time
import numpy as np

STARTING_CHUNK = 4096  # Set this appropriately for your application


def process_func(self, data, wav_data,
                 smoothing=2):
    """
    Processes incoming microphone and wav file samples when new audio is received

    This function is user-editable, but currently adjusts the amplitude of the wav file audio to match
    the amplitude of the microphone volume.

    Parameters:
        self: self parameter for when this function is called from inside AudioThreadWithBuffer
        data: microphone data (numpy array)
        wav_data: wav file data (numpy array)
        smoothing: parameter for how smooth the adjustment above is
    Returns: Audio for AudioThreadWithBuffer to play through speakers with content listed above (numpy array)
    """
    print(wav_data[0:10])
    print(data[0:10])

    data = data.astype(np.int32, casting='safe')
    wav_data = wav_data.astype(np.int32, casting='safe')

    # use RMS to match the input amplitude and output amplitude
    if data is not None:
        input_amplitude = np.sqrt(np.mean(data ** 2))
        output_amplitude = np.sqrt(np.mean(wav_data ** 2))
        scaling_factor = min(max(np.power(input_amplitude / (output_amplitude + 1e-6), 1.5), 0.001), 1)

        if self.last_gain == 0.0:
            self.last_gain = scaling_factor
            self.last_time_updated = time.time()
        else:
            time_since_update = time.time() - self.last_time_updated
            time_since_update /= 1000.0
            average_factor = max(0, min(time_since_update, 1 / smoothing)) * smoothing
            out_gain = average_factor * scaling_factor + (1 - average_factor) * self.last_gain
            self.last_gain = out_gain
        print(self.last_gain)
        wav_data = np.rint(wav_data * self.last_gain).astype(np.int16)
    return wav_data


def main():
    """
    This function runs when the program is called.

    This function is user-editable, but currently sets up an AudioThreadWithBuffer, starts it, and lets it run.

    If you need to do processing that runs independently of audio buffer management/input/output, do it in
    the while loop here.

    Parameters: none
    Returns: none
    """

    AThread = AudioThreadWithBuffer(name="SPA_Thread", starting_chunk_size=STARTING_CHUNK, process_func=process_func,
                                    wav_file="C:\\Users\\TPNml\\Downloads\\chinese joke idk.wav")  # Initialize a new thread
    print("All threads init'ed")
    try:
        AThread.start()  # Start collecting audio
        print("============== AThread started")
        while True:
            # Do any processing you want here!
            time.sleep(0.5)  # Make sure to sleep when you do not need the program to run to avoid eating too much CPU.
    except KeyboardInterrupt:  # This kills the thread when the user stops the program to avoid an infinite loop
        AThread.stop_request = True


if __name__ == "__main__":
    main()
