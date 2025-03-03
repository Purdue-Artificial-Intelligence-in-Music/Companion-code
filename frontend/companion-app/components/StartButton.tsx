import { StyleSheet, Text, TextStyle, ViewStyle, Pressable, View, Animated } from "react-native";
import { synthesizeAudio } from "./Utils";
import { Audio } from "expo-av";

export function Start_Stop_Button({
  state,
  dispatch,
  button_format,
  text_style,
}: {
  state: { playing: boolean, inPlayMode: boolean, sessionToken: string, score: string, tempo: number };
  dispatch: Function;
  button_format: object[];
  text_style: Animated.AnimatedInterpolation<string | number>;

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
    <Animated.View style={[...button_format ]}>
      <Pressable 
        onPress={() => {
          if (state.inPlayMode) dispatch({ type: "start/stop" });
          else {
            synthesize_audio_handler();
            dispatch({ type: "swap_mode"});
          }
        }}
      >
        <Animated.Text style={[styles.buttonText, { color: text_style }]}>{state.inPlayMode? state.playing ? "STOP" : "PLAY" : "SELECT" }</Animated.Text>
      </Pressable>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
    button_shape: {
      // paddingHorizontal: 24,
      // paddingVertical: 12
    },
    flexing_box: {

    },
    buttonText: {
      fontWeight: "bold",
      fontSize: 14,
    }
})
