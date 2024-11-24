import { View, Text } from "react-native";
import { useEffect } from "react";
import { Audio } from "expo-av";

export function AudioPlayerRefactored( {state}:
  {state: {playRate: number, timestamp: number, sound: Audio.Sound | null, playing: boolean } }
) {

  ///////////////////////////////////////////////////////////////////////////////////////
  // Two useEffects that tie the sound playback to the state
  ///////////////////////////////////////////////////////////////////////////////////////
  useEffect( () => {
    const updateThePlayRate = async () => {
      if (state.sound) {
        await state.sound.setRateAsync(state.playRate, true);
      }
    }
    updateThePlayRate();
  }, [state.playRate])

  useEffect( () => {
    const updateWhetherPlaying = async () => {
      if (state.sound) {
        if (state.playing) await state.sound.playAsync()
        else await state.sound.pauseAsync()
      }
    }
    updateWhetherPlaying();
  }, [state.playing])

  // The code to update the position in the case of reset is in Dispatch.ts,
  // in the reducer function's reset case, because it runs then and not on 
  // any particular state change

  return (
    <View
      style={{
        flexDirection: "row",
        justifyContent: "space-between",
        marginTop: 20,
      }}
    >
      <Text>Current rate: {state.playRate.toFixed(2)}x</Text>
      <Text style={{ marginTop: 10 }}>
        Position: {state.timestamp.toFixed(1)}s
      </Text>
      <Text style={{ marginTop: 10 }}>
        Audio Status: {state.sound ? "Audio Loaded" : "Audio Unavailable"}
      </Text>
    </View>
  );
}
