import numpy as np
import pyaudio
import soundfile as sf
from threading import Thread

class RealTimePhaseVocoder:
    def __init__(self, input_file, initial_rate=1.0):
        self.input_file = input_file
        self.rate = initial_rate
        self.chunk_size = 2048
        self.overlap = self.chunk_size // 4
        self.hop_size = self.chunk_size - self.overlap
        self.signal, self.sr = sf.read(input_file)
        self.position = 0
        self.phase_accumulator = np.zeros(self.chunk_size)
        self.previous_phase = np.zeros(self.chunk_size)
        self.window = np.hanning(self.chunk_size)
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = self.pyaudio_instance.open(format=pyaudio.paFloat32,
                                                 channels=1,
                                                 rate=self.sr,
                                                 output=True,
                                                 stream_callback=self.callback)

    def stft(self, signal):
        """Compute the Short-Time Fourier Transform."""
        windowed_signal = signal * self.window
        return np.fft.fft(windowed_signal)

    def istft(self, spectrum):
        """Compute the inverse Short-Time Fourier Transform."""
        return np.real(np.fft.ifft(spectrum)) * self.window

    def process_chunk(self, chunk, rate):
        """Apply phase vocoder to a chunk."""
        spectrum = self.stft(chunk)
        magnitude = np.abs(spectrum)
        phase = np.angle(spectrum)
        
        # Phase unwrapping and accumulation
        phase_difference = phase - self.previous_phase
        self.previous_phase = phase
        phase_difference = np.mod(phase_difference + np.pi, 2 * np.pi) - np.pi
        
        true_freq = phase_difference / self.hop_size
        self.phase_accumulator += true_freq * rate
        phase_vocoded = np.exp(1j * self.phase_accumulator)
        
        return self.istft(magnitude * phase_vocoded)

    def callback(self, in_data, frame_count, time_info, status):
        """Stream callback to process and play audio in real-time."""
        if self.position + self.chunk_size > len(self.signal):
            self.position = 0  # Loop back to start

        chunk = self.signal[self.position:self.position + self.chunk_size]
        processed_chunk = self.process_chunk(chunk, self.rate)
        self.position += int(self.hop_size * self.rate)

        return (processed_chunk.astype(np.float32).tobytes(), pyaudio.paContinue)

    def change_rate(self, new_rate):
        """Change the playback rate."""
        self.rate = new_rate

    def play(self):
        """Start the audio stream."""
        self.stream.start_stream()
        while self.stream.is_active():
            pass

    def stop(self):
        """Stop the audio stream."""
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio_instance.terminate()

# Usage
def main():
    input_file = 'audio/imperial_march.wav'
    vocoder = RealTimePhaseVocoder(input_file, initial_rate=1.0)

    # Run the playback in a separate thread
    play_thread = Thread(target=vocoder.play)
    play_thread.start()

    try:
        while True:
            new_rate = float(input("Enter new rate: "))
            vocoder.change_rate(new_rate)
    except KeyboardInterrupt:
        vocoder.stop()
        play_thread.join()

if __name__ == "__main__":
    main()
