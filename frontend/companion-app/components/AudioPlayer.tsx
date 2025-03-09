import { View, Text, StyleSheet, Animated } from "react-native";
import { useEffect } from "react";
import { Audio } from "expo-av";

export function AudioPlayer({
  state,
  menuStyle
}: {
  state: {
    playRate: number;
    timestamp: number;
    accompanimentSound: Audio.Sound | null;
    playing: boolean;
  };
  menuStyle: object;
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
    <Animated.View style={[styles.container, menuStyle]}>
      <Text style={styles.text}>
        Current rate: {state.playRate.toFixed(2)}x
      </Text>
      <Text style={styles.text}>Position: {state.timestamp.toFixed(1)}s</Text>
      <Text style={styles.text}>
        Audio Status:{" "}
        {state.accompanimentSound ? "Audio Loaded" : "Audio Unavailable"}
      </Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({

  // footer container styles
  container: {
    flexDirection: "row",
    justifyContent: "space-evenly",
    marginTop: 10,
    padding: 10,
    width: "100%",
    backgroundColor: "#2C3E50", 
    position: "absolute", // make footer stick on bottom even after scroll
    bottom: 0,
  },
  // text styles for text in footer content
  text: {
    textAlign: "center",
    color: "#ffffff",
    fontWeight: "bold",
    fontSize: 10
  },
});
