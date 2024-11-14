import { fetchData } from "./Api";
import { View, Text, Button } from "react-native";
import { useState, useEffect } from "react";
import { Audio } from "expo-av";

export function AudioPlayerRefactored( {state, dispatch}:
  {state: {playRate: number, timestamp: number, sound: Audio.Sound | null, playing: boolean },
    dispatch: Function
  }
) {
  const [sample_rate, setSampleRate] = useState("");
  const [buffer, setBuffer] = useState();
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const [playbackRate, setPlaybackRate] = useState(1.0); // Default rate of 1x
  const [currentPosition, setCurrentPosition] = useState(0); // Playback position in seconds
  const [duration, setDuration] = useState(0); // Total audio duration in seconds

  const fetchAndPlay = async () => {
    try {
      const data = await fetchData("http://localhost:5000/audioBuffer"); // Adjust URL as needed
      setSampleRate(data["sr"]); // Update state with the fetched data
      if (!data["buffer"]) {
        console.warn("No buffer!!");
        return;
      }

      const soundObject = new Audio.Sound();
      await soundObject.loadAsync({
        uri: `data:audio/wav;base64,${data["buffer"]}`,
      });

      // soundObject.setRateAsync(0.5, true);
      dispatch( {type:'new_audio', sound:soundObject});

      const status = await soundObject.getStatusAsync();
      console.log(status);
      if (soundObject) {
        await soundObject.playAsync(); // Now it's safe to play
      } else {
        console.warn("Audio not loaded properly");
      }
      // await soundObject.playAsync();
    } catch (error) {
      // Handle error case
      console.log("error loading sound", error);
    }
  };

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

  return (
    <View>
      <Button title="Get and play Audio" onPress={fetchAndPlay} />

      <View
        style={{
          flexDirection: "row",
          justifyContent: "space-between",
          marginTop: 20,
        }}
      >
        <Text>0.1x</Text>
        <Text>Current rate: {state.playRate.toFixed(2)}x</Text>
        <Text>5.0x</Text>
      </View>
      <Text style={{ marginTop: 10 }}>
        Position: {state.timestamp.toFixed(1)}s / {duration.toFixed(1)}s
      </Text>
      <Text style={{ marginTop: 10 }}>
        Audio Status: {state.sound ? "Audio Loaded" : "Audio Unavailable"}
      </Text>
    </View>
  );
}
