from AudioThread1 import AudioThread
import time
import numpy as np

STARTING_CHUNK = 1024

def process_func(self, mic_data, wav_data):
    data = np.copy(mic_data).astype(np.float64, casting='safe')
    wav_data = wav_data.astype(np.float64)
    
    # input to buffer
    if self.buffer_index + len(data) <= self.buffer_size:
        self.audio_buffer[self.buffer_index:self.buffer_index + len(data)] = data
        self.buffer_index += len(data)
    else:
        # Overflow: Reset or handle as per your requirement
        self.buffer_index = 0

    if self.buffer_index >= 2 * self.starting_chunk_size:
        self.audio_buffer[:self.buffer_index - self.starting_chunk_size] = self.audio_buffer[self.starting_chunk_size:]
        self.buffer_index -= self.starting_chunk_size

    # use RMS to match the input amplitude and output amplitude
    if data is not None:
        input_amplitude = np.sqrt(np.mean(data ** 2))
        output_amplitude = np.sqrt(np.mean(wav_data ** 2))

        scaling_factor = input_amplitude / (output_amplitude + 1e-6)
        wav_data *= scaling_factor
    else:
        data_bytes = b''
    return wav_data.astype(np.int16)


def main():
    
    AThread = AudioThread(name="SPA_Thread", starting_chunk_size=STARTING_CHUNK, process_func=process_func, wav_file="2.wav")
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
