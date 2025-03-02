import { StyleSheet, Text, TextStyle, ViewStyle, Pressable, View } from "react-native";
import { synthesizeAudio } from "./Utils";
import { Audio } from "expo-av";

export function Start_Stop_Button({
  state,
  dispatch,
  button_format,
  text_style,
  buttonStyle
}: {
  state: { playing: boolean, inPlayMode: boolean, sessionToken: string, score: string, tempo: number };
  dispatch: Function;
  button_format: ViewStyle;
  text_style: TextStyle;
  buttonStyle: object
}) {

  // Copied from SynthesizeButton.tsx
  const synthesize_audio_handler = async () => {
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
    <View style={styles.flexing_box}>
      <Pressable
        style={[buttonStyle, button_format]}
        onPress={() => {
          if (state.inPlayMode) dispatch({ type: "start/stop" });
          else {
            synthesize_audio_handler();
            dispatch({ type: "swap_mode"});
          }
        }}
      >
        <Text style={text_style}>{state.inPlayMode? state.playing ? "STOP" : "PLAY" : "SELECT" }</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
    button_shape: {
      // paddingHorizontal: 24,
      // paddingVertical: 12
    },
    flexing_box: {

    }
})
