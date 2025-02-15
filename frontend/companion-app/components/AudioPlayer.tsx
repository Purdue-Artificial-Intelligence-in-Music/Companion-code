import { View, Text, StyleSheet } from "react-native";
import { useEffect } from "react";
import { Audio } from "expo-av";

export function AudioPlayer({
  state,
}: {
  state: {
    playRate: number;
    timestamp: number;
    accompanimentSound: Audio.Sound | null;
    playing: boolean;
  };
}) {
  ///////////////////////////////////////////////////////////////////////////////////////
  // Two useEffects that tie the sound playback to the state
  ///////////////////////////////////////////////////////////////////////////////////////
  useEffect(() => {
    const updateThePlayRate = async () => {
      if (state.accompanimentSound) {
        await state.accompanimentSound.setRateAsync(state.playRate, true);
      }
    };
    updateThePlayRate();
  }, [state.playRate, state.accompanimentSound]);

  useEffect(() => {
    const updateWhetherPlaying = async () => {
      if (state.accompanimentSound) {
        if (state.playing) {
          await state.accompanimentSound.playAsync();
        } else {
          await state.accompanimentSound.pauseAsync();
        }
      }
    };
    updateWhetherPlaying();
  }, [state.playing, state.accompanimentSound]);

  // The code to update the position in the case of reset is in Dispatch.ts,
  // in the reducer function's reset case, because it runs then and not on
  // any particular state change

  return (
    <View style={styles.container}>
      <Text style={styles.text}>
        Current rate: {state.playRate.toFixed(2)}x
      </Text>
      <Text style={styles.text}>Position: {state.timestamp.toFixed(1)}s</Text>
      <Text style={styles.text}>
        Audio Status:{" "}
        {state.accompanimentSound ? "Audio Loaded" : "Audio Unavailable"}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    justifyContent: "space-evenly",
    marginTop: 10,
    width: "60%",
  },
  text: {
    textAlign: "center",
  },
});
