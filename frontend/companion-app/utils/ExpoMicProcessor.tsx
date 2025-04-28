import { Audio, InterruptionModeIOS, InterruptionModeAndroid } from 'expo-av';
import { Platform } from 'react-native';

/**
 * ExpoMicProcessor continuously captures short chunks of microphone audio,
 * converts them into Float32 samples, and emits them via `onmessage`.
 */
export class ExpoMicProcessor {
  private _buffer = new Float32Array(4096); // Internal circular buffer to accumulate samples until we have 4096 frames
  private _bufIndex = 0; // Next write position in the internal buffer
  private _running = false; // Flag indicating whether capture should continue

  /**
   * Callback invoked whenever _buffer fills with 4096 samples.
   * Receives an object with a Float32Array of length 4096.
   * Override this to process audio in real time.
   */
  public onmessage: (event: { data: Float32Array }) => void = () => {};


  // Initialize audio subsystem: request mic permission and configure audio mode. Must be called once before `start`.
  public async init() {
    const { granted } = await Audio.requestPermissionsAsync(); // Prompt user for microphone permission
    if (!granted) throw new Error('Microphone permission denied'); // Error handling when microphone is not granted permission

    // Set global audio mode to allow recording
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: true, // Enable recording on iOS
      playsInSilentModeIOS: true, // Allow playback even when device is silenced
      interruptionModeIOS: InterruptionModeIOS.DoNotMix, // Don't mix with other audio playing on iOS device
      interruptionModeAndroid: InterruptionModeAndroid.DoNotMix, // Don't mix with other audio on andriod device
      shouldDuckAndroid: false,  // If we didn’t get exclusive focus, don’t fall back to ducking - andriod devices.
    });
  }

  // Begins the continuous recording loop and records fixed-size chunks (4096 samples) and dispatches them. 
  public async start() {

    if (this._running) return;  // Error checking if already recording somewhow before start
    this._running = true; // Set recording flag to true

    const SAMPLE_RATE = 44100; // The sample rate used across platforms for predictable buffer math
    const chunkMs = (4096 / SAMPLE_RATE) * 1000; // Convert 4096 samples at SAMPLE_RATE into milliseconds
    
    // Recording options differ per platform (Android uses AAC, iOS uses WAV)
    // Configure platform-specific recording options:
    const recordingOptions: RecordingOptions = {
      android: {
        extension: '.m4a',                             // Container file extension
        outputFormat: Audio.AndroidOutputFormat.MPEG_4, // MP4/M4A file format
        audioEncoder: Audio.AndroidAudioEncoder.AAC,    // AAC codec for good quality at low bitrates
        sampleRate: SAMPLE_RATE,                        // Samples per second (e.g., 44100 Hz)
        numberOfChannels: 1,                            // Mono recording
        bitRate: 128000,                                // Target bits per second (128 kbps)
      },
      ios: {
        extension: '.wav',                               // Container file extension
        outputFormat: Audio.IOSOutputFormat.LINEARPCM,   // Uncompressed PCM
        sampleRate: SAMPLE_RATE,                         // Samples per second (e.g., 44100 Hz)
        numberOfChannels: 1,                             // Mono recording
        linearPCMBitDepth: 32,                           // Bits per sample (32-bit float)
        linearPCMIsBigEndian: false,                     // Use little-endian byte order
        linearPCMIsFloat: true,                          // Store samples as IEEE-754 floats
        audioQuality: Audio.IOSAudioQuality.MAX,         // Use highest-quality float PCM for maximum fidelity
      },
    };

    // Capture loop - keep recording chunks until stopped
    while (this._running) {

      // Prepare recorder with our options
      const rec = new Audio.Recording();
      await rec.prepareToRecordAsync(recordingOptions);

      // Start recording, wait for chunk duration, then stop
      await rec.startAsync();
      await new Promise((r) => setTimeout(r, chunkMs));
      await rec.stopAndUnloadAsync();

      const uri = rec.getURI(); // Retrieve file URI for the recorded chunk
      if (!uri) break;  // if URI missing, exit loop

      // Load raw file into memory
      const arrayBuffer = await fetch(uri).then((r) => r.arrayBuffer());
      let floats: Float32Array | null = null;

      // Convert file data to Float32 samples
      if (Platform.OS === 'ios') {
        floats = parseWavToFloat32(arrayBuffer);
      } else {
        // Android: AAC decoding to PCM not implemented here
        console.warn('Android PCM decode not implemented; skipping chunk.');
      }

      if (floats) {
        // Push samples into our circular buffer
        for (let i = 0; i < floats.length; i++) {
          this._buffer[this._bufIndex++] = floats[i];
          // When buffer fills, fire onmessage and reset index
          if (this._bufIndex === 4096) {
            // Pass a copy of the buffer to avoid mutation
            this.onmessage({ data: this._buffer.slice(0) });
            this._bufIndex = 0;
          }
        }
      }
    }
  }

  //Stop the capture loop gracefully.
  public stop() {
    this._running = false;
  }
}

/**
 * Parses a WAV file buffer and extracts the raw Float32 samples from the data chunk.
 * Walks over RIFF chunks until it finds 'data', then returns a Float32Array view.
 */

function parseWavToFloat32(buf: ArrayBuffer): Float32Array {
  const dv = new DataView(buf); // Create a DataView to easily read binary data (bytes, integers) from the ArrayBuffer
  let offset = 12;  // The first 12 bytes are the "RIFF" identifier, file size, and "WAVE" identifier

  // Loop through the subchunks until we find the "data" chunk
  while (offset < dv.byteLength) {
    // Read the 4-character chunk ID 
    const id = String.fromCharCode(
      dv.getUint8(offset),
      dv.getUint8(offset + 1),
      dv.getUint8(offset + 2),
      dv.getUint8(offset + 3)
    );

    // The next 4 bytes tell us how large this chunk’s payload is
    const size = dv.getUint32(offset + 4, true);

    // If this is the "data" chunk, we can extract the raw PCM samples
    if (id === 'data') {
      // PCM floats start immediately after the 8-byte header (ID + size)
      // size is in bytes, so divide by 4 to get the number of Float32 samples
      return new Float32Array(buf, offset + 8, size / 4);
    }

    // Otherwise skip ahead past this chunk (8 bytes header + payload)
    offset += 8 + size;
  }

  // If we never saw a "data" chunk, throw an error
  throw new Error('WAV data chunk not found');
}