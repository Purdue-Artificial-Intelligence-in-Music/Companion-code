/* eslint-disable prettier/prettier */
import { Text, TextStyle, ViewStyle, Pressable } from "react-native";
import { synthesizeAudio } from "./Utils";
import { Audio } from "expo-av";

export function SynthesizeButton({
  state,
  dispatch,
  button_style,
  text_style,
}: {
  state: { sessionToken: string; score: string; tempo: number };
  dispatch: Function;
  button_style: ViewStyle;
  text_style: TextStyle;
}) {
  const handlePress = async () => {
    console.log("Synthesizing audio...");
    synthesizeAudio(state.sessionToken, state.score, state.tempo).then(
      async (data) => {
        console.log("Synthesized audio data:", data);
        const { sound: newSound } = await Audio.Sound.createAsync(
          { uri: data.uri },
          { shouldPlay: false }
        );
        const status = await newSound.getStatusAsync();
        console.log("New sound status:", status);
        dispatch({
          type: "new_audio",
          sound: newSound,
          synth_tempo: state.tempo,
        });
      }
    );
  };

  return (
    <Pressable
      style={button_style}
      onPress={() => {
        handlePress();
      }}
    >
      <Text style={text_style}>{"Synthesize"}</Text>
    </Pressable>
  );
}

async function createSoundFromFloatArray(
  floatArray: number[],
  sampleRate: number = 44100
): Promise<Audio.Sound> {
  const write16LE = (value: number): string =>
    String.fromCharCode(value & 0xff, (value >> 8) & 0xff);

  // Normalize floats to 16-bit PCM
  const pcmData = floatArray
    .map((float) => {
      const int16 = Math.max(-1, Math.min(1, float)) * 32767;
      return write16LE(Math.round(int16));
    })
    .join("");

  // WAV header
  const wavHeader = [
    "RIFF",
    write16LE(36 + pcmData.length), // File size minus 8 bytes
    "WAVE",
    "fmt ", // Format chunk
    write16LE(16), // Subchunk1Size (PCM format)
    write16LE(1), // Audio format (1 = PCM)
    write16LE(1), // Number of channels (1 = mono)
    write16LE(sampleRate), // Sample rate
    write16LE(sampleRate * 2), // Byte rate (SampleRate * NumChannels * BitsPerSample/8)
    write16LE(2), // Block align (NumChannels * BitsPerSample/8)
    write16LE(16), // Bits per sample
    "data", // Data chunk
    write16LE(pcmData.length), // Subchunk2Size
  ].join("");

  // Combine header and PCM data
  const wavFile = wavHeader + pcmData;

  // For web platforms
  const blob = new Blob(
    [new Uint8Array([...wavFile].map((c) => c.charCodeAt(0)))],
    {
      type: "audio/wav",
    }
  );
  const uri: string = URL.createObjectURL(blob);

  // Load the sound into an Audio.Sound object
  const { sound } = await Audio.Sound.createAsync({ uri });

  return sound;
}
