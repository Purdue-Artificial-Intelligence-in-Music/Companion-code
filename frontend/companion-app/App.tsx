// Import necessary modules and components from the Expo and React Native libraries
import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View, SafeAreaView } from "react-native";
import React, { useEffect, useReducer } from "react";
import { startSession, synchronize } from "./components/Utils";
import { Score_Select } from "./components/ScoreSelect";
import { Start_Stop_Button } from "./components/StartButton";
import { MeasureSetBox } from "./components/MeasureSetter";
import { TempoBox } from "./components/TempoBox";
import { Fraction } from "opensheetmusicdisplay";
import AudioRecorder from "./components/AudioRecorder";
import { AudioPlayer } from "./components/AudioPlayer";
import reducer_function from "./Dispatch";
import ScoreDisplay from "./components/ScoreDisplay";
import { SynthesizeButton } from "./components/SynthesizeButton";

// Define the main application component
export default function App() {
  ////////////////////////////////////////////////////////////////////////////////////
  // Main state - holds position in the piece, playback rate, etc.
  ////////////////////////////////////////////////////////////////////////////////////
  // useReducer returns a state - which is an object initialized to be useReducer's second argument
  // - and a function (here called "dispatch") which is the only way to update the state.
  // The reducer_function takes in two arguments ("state" and "action") and returns an object -
  // when the dispatch function is called, it takes one argument, calls the reducer_function
  // with the current state as the state and the dispatch function's argument as the action,
  // and updates the state to be the output of the reducer_function.
  const [state, dispatch] = useReducer(
    reducer_function, // The reducer function is found in Dispatch.ts
    {
      playing: false, // whether the audio is playing
      resetMeasure: 1, // the measure to reset to
      playRate: 1.0, // the rate at which the audio is playing
      timestamp: 0.0, // the current position in the piece in seconds
      cursorTimestamp: 0.0, // the position of the cursor in the piece in seconds
      time_signature: new Fraction(4, 4, 0, false),
      score: "", // the score to display
      sessionToken: null, // the session token for the API
      accompanimentSound: null, // the accompaniment sound
      synth_tempo: 100, // the tempo of the synthesized audio
      tempo: 100, // the tempo in the tempo box (even if changed more recently)
      score_tempo: 100, // the tempo in the musical score
      scores: [], // the list of scores to choose from
    },
  );

  // Sync sessionToken with useReducer state
  // Fetch the session token and dispatch it to the reducer
  useEffect(() => {
    const fetchSessionToken = async () => {
      try {
        const data = await startSession();
        const token = data.session_token;
        console.log("Fetched session token:", token);
        dispatch({ type: "new_session", token: token });
      } catch (error) {
        console.error("Error fetching session token:", error);
      }
    };

    fetchSessionToken();
  }, []);

  console.log(state);

  /////////////////////////////////////////////////////////
  // The code below updates the timestamp but is not yet tied to the API
  // This could be moved to any sub-component (e.g., ScoreDisplay, AudioPlayer)
  // or made its own invisible component - OR,
  // we will re-synchronize whenever the audiorecorder posts, in which case this should
  // be handled there
  const UPDATE_INTERVAL = 500; // milliseconds between updates to timestamp and rate

  useEffect(() => {
    const getAPIData = async () => {
      const {
        playback_rate: newPlayRate,
        estimated_position: estimated_position,
      } = await synchronize(state.sessionToken, [0], state.timestamp);
      console.log("New play rate:", newPlayRate);
      console.log("New timestamp:", estimated_position);

      dispatch({
        type: "increment",
        time: estimated_position,
        rate: 1,
      });
    };

    // Start polling
    setInterval(() => {
      if (state.playing) {
        getAPIData();
      }
    }, UPDATE_INTERVAL);
  }, [state.playing, state.timestamp, state.sessionToken]);
  // The "could be moved into any subcomponent" comment refers to the above
  ///////////////////////////////////////////////////////////////////////////////

  ////////////////////////////////////////////////////////////////////////////////
  // Render the component's UI
  ////////////////////////////////////////////////////////////////////////////////
  return (
    <SafeAreaView style={styles.container}>
      {/* Provides safe area insets for mobile devices */}
      <AudioRecorder state={state} dispatch={dispatch} />
      <Text style={styles.title}>Companion, the digital accompanist</Text>

      <View style={styles.button_wrapper}>
        <Score_Select state={state} dispatch={dispatch} />
        <TempoBox
          state={state}
          dispatch={dispatch}
          wrapper_style={styles.tempo_box}
          text_input_style={styles.text_input}
          label_text_style={styles.label}
        />
        <SynthesizeButton
          state={state}
          dispatch={dispatch}
          button_style={styles.synthesize_button}
          text_style={styles.button_text}
        />
        <Start_Stop_Button
          state={state}
          dispatch={dispatch}
          button_style={styles.play_button}
          text_style={styles.button_text}
        />
        <MeasureSetBox
          state={state}
          dispatch={dispatch}
          wrapper_style={styles.measure_box}
          text_input_style={styles.text_input}
          button_style={styles.reset_button}
          button_text_style={styles.button_text}
          label_text_style={styles.label}
        />
      </View>
      <ScoreDisplay state={state} dispatch={dispatch} />
      <StatusBar style="auto" />
      {/* Automatically adjusts the status bar style */}
      <AudioPlayer state={state} />
    </SafeAreaView>
  );
}

// Define styles for the components using StyleSheet
const styles = StyleSheet.create({
  container: {
    flex: 1, // Make the container fill the available space
    backgroundColor: "#fff", // Set background color to white
    alignItems: "center", // Center children horizontally
    justifyContent: "center", // Center children vertically
    padding: 16, // Add padding around the container
  },
  title: {
    fontSize: 20, // Set the font size for the title
    marginBottom: 20, // Add space below the title
  },
  label: {
    fontSize: 16,
  },
  synthesize_button: {
    flex: 0.2,
    borderColor: "black",
    borderRadius: 15,
    backgroundColor: "lightblue",
    justifyContent: "center",
  },
  play_button: {
    flex: 0.2,
    borderColor: "black",
    borderRadius: 15,
    backgroundColor: "lightblue",
    justifyContent: "center",
  },
  reset_button: {
    flex: 0.8,
    borderColor: "black",
    borderRadius: 15,
    backgroundColor: "lightblue",
  },
  button_text: {
    fontSize: 20,
    textAlign: "center",
  },
  button_wrapper: {
    flex: 1,
    flexDirection: "row",
    justifyContent: "space-between",
    padding: 10,
    backgroundColor: "lightgray",
    width: "100%",
    minHeight: 72,
  },
  measure_box: {
    flexDirection: "row",
    padding: 10,
    justifyContent: "space-between",
    width: "40%",
    flex: 0.4,
    height: "80%",
  },
  tempo_box: {
    flexDirection: "row",
    padding: 10,
    justifyContent: "space-between",
    width: "20%",
    flex: 0.2,
    height: "80%",
  },
  text_input: {
    backgroundColor: "white",
    flex: 0.3,
    height: "100%",
  },
});
