// A custom audio processor that captures live microphone audio 
// and sends 4096-sample chunks to App.tsx for further processing
class MicProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._buffer = new Float32Array(4096); // Create a buffer to collect 4096 audio samples (same size as ChromaMaker's FFT window)
    this._bufIndex = 0; // Tracks how many samples have been added to the buffer
  }

  // This method is called repeatedly
  process(inputs, outputs) {
    const input = inputs[0]; // Get audio from the first input

    // Check if we have valid input data
    if (input && input[0]) {
      const samples = input[0]; // An array of audio samples (128 samples per call)

      // Loop through each sample and fill our custom buffer
      for (let i = 0; i < samples.length; i++) {
        this._buffer[this._bufIndex++] = samples[i];

        // Once we've collected 4096 samples, send them to App.tsx
        if (this._bufIndex >= this._buffer.length) {
          this.port.postMessage(this._buffer.slice(0)); // Send a copy of the full buffer
          this._bufIndex = 0; // Reset buffer index to start collecting the next chunk
        }
      }
    }

    return true; // Return true to keep the processor running
  }
}
// Register this processor under the name 'mic-processor' for it to be used by App.tsx using addModule()
registerProcessor('mic-processor', MicProcessor);
