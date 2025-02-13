// Import necessary modules and components from the Expo and React Native libraries
import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View, Image, SafeAreaView } from "react-native";
import React, { useEffect, useReducer, useRef } from "react";
import { startSession, synchronize } from "./components/Utils";
import { Score_Select } from "./components/ScoreSelect";
import { Return_Button } from "./components/ReturnButton";
import { Start_Stop_Button } from "./components/StartButton";
import { MeasureSetBox } from "./components/MeasureSetter";
import { TempoBox } from "./components/TempoBox";
import { Fraction } from "opensheetmusicdisplay";
import AudioRecorder from "./components/AudioRecorderStateVersion";
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
      inPlayMode: false, // whether we are in play mode (and not score selection mode)
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
      scores: [] // the list of scores to choose from
    },
  );
  const waveFormRef = useRef<Array<number>>([]); // audio data to send to backend
  const updateWaveForm = (data: Array<number>) => { // function to update it from the recorder
    waveFormRef.current = data;
  }

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

  /////////////////////////////////////////////////////////
  // The code below updates the timestamp but is not yet tied to the API
  // This could be moved to any sub-component (e.g., ScoreDisplay, AudioPlayer)
  // or made its own invisible component - OR,
  // we will re-synchronize whenever the audiorecorder posts, in which case this should
  // be handled there
  const UPDATE_INTERVAL = 500; // milliseconds between updates to timestamp and rate

  const getAPIData = async () => {
    // console.log("Sending data: ", waveFormRef.current);
    const {
      playback_rate: newPlayRate,
      estimated_position: estimated_position,
    } = await synchronize(state.sessionToken, [122, 123, 124], state.timestamp);
    console.log("New play rate:", newPlayRate);
    console.log("New timestamp:", estimated_position);

    dispatch({
      type: "increment",
      time: estimated_position,
      rate: newPlayRate,
    });
  }

  useEffect(() => {
    if (state.playing) {
      console.log("To send another request, bc state is: ", state);
      setTimeout(getAPIData, UPDATE_INTERVAL);
    }
  }, [state.playing, state.timestamp, state.sessionToken]);
  // The "could be moved into any subcomponent" comment refers to the above
  ///////////////////////////////////////////////////////////////////////////////

  ////////////////////////////////////////////////////////////////////////////////
  // Render the component's UI
  ////////////////////////////////////////////////////////////////////////////////
  return (
    <SafeAreaView style={styles.container}>
      {/* Provides safe area insets for mobile devices */}
      {/* <AudioRecorder state={state} dispatch={dispatch} updateWaveFormData={updateWaveForm}/> */}
      <View style={styles.menu_bar}>
        <Image source={{ uri: './assets/companion.png' }} style={styles.logo}/>
        <Return_Button
          state={state}
          dispatch={dispatch}
          button_format={styles.button_format}
          text_style={styles.button_text}
        />
        <Start_Stop_Button
          state={state}
          dispatch={dispatch}
          button_format={styles.button_format}
          text_style={styles.button_text}
        />
        {
          state.inPlayMode ?
          <MeasureSetBox
            state={state}
            dispatch={dispatch}
            button_style={styles.button_format}
            button_text_style={styles.button_text}
          />
          :
          <TempoBox
            state={state}
            dispatch={dispatch}
            label_text_style={styles.button_text}
          />
        }
      </View>
      <View style={styles.main_area}>
        { // List of scores, show when not in play mode
        state.inPlayMode || <Score_Select state={state} dispatch={dispatch} /> }
        <ScoreDisplay state={state} dispatch={dispatch} />
      </View>
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
  button_format: {
    borderColor: "black",
    borderRadius: 15,
    backgroundColor: "lightblue",
    justifyContent: "center"
  },
  button_text: {
    fontSize: 24,
    textAlign: "center",
  },
  menu_bar: {
    flex: 0,
    flexDirection: "row",
    justifyContent: "space-between",
    backgroundColor: "lightgray",
    width: "100%",
    minHeight: 100,
  },
  main_area: {
    flex: 1,
    flexDirection: "row",
    justifyContent: "space-between",
    backgroundColor: "white",
    width: "100%",
    height: "80%",
  },
  logo: {
    backgroundColor: "white",
    flex: 0.25,
    width: "25%",
    height: "100%",
    resizeMode: 'contain'
  },
});
