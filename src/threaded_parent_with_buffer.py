from AudioThreadWithBuffer import AudioThreadWithBuffer
import time
import numpy as np

STARTING_CHUNK = 1024


def process_func(self, data, wav_data,
                 smoothing = 2):
    wav_data = wav_data.astype(np.float64)

    #if self.buffer_index >= 2 * self.starting_chunk_size:
    #    self.audio_buffer[:self.buffer_index - self.starting_chunk_size] = self.audio_buffer[self.starting_chunk_size:]
    #    self.buffer_index -= self.starting_chunk_size

    # use RMS to match the input amplitude and output amplitude
    if data is not None:
        input_amplitude = max(np.sqrt(np.mean(data ** 2)), 1)
        if input_amplitude < 5:
            input_amplitude = 0
        output_amplitude = max(np.sqrt(np.mean(wav_data ** 2)), 1)

        scaling_factor = min(max(input_amplitude / (output_amplitude + 1e-6), 0.0001), 0.003)

        if self.last_gain == 0.0:
            self.last_gain = scaling_factor
            self.last_time_updated = time.time()
        else:
            time_since_update = time.time() - self.last_time_updated
            time_since_update /= 1000.0
            average_factor = max(0, min(time_since_update, 1/smoothing))*smoothing
            out_gain = average_factor*scaling_factor + (1 - average_factor)*self.last_gain
            self.last_gain = out_gain
        wav_data *= self.last_gain
    else:
        data_bytes = b''
    return wav_data.astype(np.int16)


def main():
    AThread = AudioThreadWithBuffer(name="SPA_Thread", starting_chunk_size=STARTING_CHUNK, process_func=process_func,
                          wav_file="C:\\Users\\TPNml\\Downloads\\saudade4.wav")
    print("All threads init'ed")
    try:
        AThread.start()
        print("============== AThread started")
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        AThread.stop_request = True


if __name__ == "__main__":
    main()
