from AudioThread import AudioThread
import time
import numpy as np

STARTING_CHUNK = 1024

def process_func(audio_thr, data):
    # Does nothing
        # input to buffer
    if audio_thr.buffer_index + len(data) <= audio_thr.buffer_size:
        audio_thr.audio_buffer[audio_thr.buffer_index:audio_thr.buffer_index+len(data)] = data
        audio_thr.buffer_index += len(data)
    else:                                      
        # Overflow: Reset or handle as per your requirement
        audio_thr.buffer_index = 0

    if audio_thr.buffer_index >= 2 * audio_thr.starting_chunk_size:
        audio_thr.audio_buffer[:audio_thr.buffer_index-audio_thr.starting_chunk_size] = audio_thr.audio_buffer[audio_thr.starting_chunk_size:]
        audio_thr.buffer_index -= audio_thr.starting_chunk_size

    # use RMS to match the input amplitude and output amplitude
    if data is not None:
        input_amplitude = np.sqrt(np.mean(data ** 2))
        output_amplitude = np.sqrt(np.mean(data ** 2))

        scaling_factor = input_amplitude / (output_amplitude + 1e-6)
        data *= scaling_factor
        data_bytes = data.tobytes()
    else:
        data_bytes = b''

    
    return data_bytes
    

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
