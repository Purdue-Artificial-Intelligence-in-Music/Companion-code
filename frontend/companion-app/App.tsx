// Import necessary modules and components from the Expo and React Native libraries
import { StatusBar } from 'expo-status-bar'; // Manages the status bar on mobile devices
import { StyleSheet, Text, View, SafeAreaView} from 'react-native'; // Imports styling and layout components
import React, { useEffect, useReducer, useRef, useState } from 'react'; // Imports React and hooks
import {GET_Request, POST_Request, Play_Audio} from "./components/Api_Caller";
import { Score_Select } from './components/ScoreSelect';
import { Start_Stop_Button } from './components/StartButton';
import { MeasureSetBox } from './components/MeasureSetter';
import { TempoBox } from './components/TempoBox';
import { Fraction } from 'opensheetmusicdisplay';
import AudioRecorder from './components/AudioRecorder';
import { AudioPlayerRefactored } from './components/AudioPlayerRefactored';
import reducer_function from './Dispatch';
import ScoreDisplay from './components/ScoreDisplay';
  
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
  const [state, dispatch] = useReducer( reducer_function, // The reducer function is found in Dispatch.ts
    {
      playing:false,
      resetMeasure:1,
      playRate:1.0,
      timestamp:0.0,
      cursorTimestamp:0.0,
      time_signature: new Fraction(4, 4, 0, false),
      score:"air_on_the_g_string.musicxml",
      sessionToken:"",
      accompanimentSound:null,
      synth_tempo:100, // the tempo of the synthesized audio
      tempo:100, // the tempo in the tempo box (even if changed more recently)
      score_tempo:100, // the tempo in the musical score
      scores: [
        {
          filename: "air_on_the_g_string.musicxml",
          piece: "Bach - Air on the G String",
        },
        {
          filename: "twelve_duets.musicxml",
          piece: "Mozart - Twelve Duets"
        }
      ]
    }
  )

  /////////////////////////////////////////////////////////
  // The code below updates the timestamp but is not yet tied to the API
  // This could be moved to any sub-component (e.g., ScoreDisplay, AudioPlayer)
  // or made its own invisible component - OR,
  // we will re-synchronize whenever the audiorecorder posts, in which case this should
  // be handled there
  const UPDATE_INTERVAL = 500; // milliseconds between updates to timestamp and rate

  const getAPIData = async () => {
    const newPlayRate = 0.5 + Math.random(); // Update this to actual get data from API!!!
    const newTimeStamp = state.timestamp + UPDATE_INTERVAL * state.playRate / 1000;
    dispatch( {type:'increment', time:newTimeStamp, rate:newPlayRate} )
    
  }

  useEffect(() => {
    if (state.playing) setTimeout(getAPIData, UPDATE_INTERVAL);
  }, [state.playing, state.timestamp])
  // The "could be moved into any subcomponent" comment refers to the above
  ///////////////////////////////////////////////////////////////////////////////

  ////////////////////////////////////////////////////////////////////////////////
  // Render the component's UI
  ////////////////////////////////////////////////////////////////////////////////
  return (
    <SafeAreaView style={styles.container}>
      {/* Provides safe area insets for mobile devices */}
      <AudioRecorder state={state} dispatch={dispatch}/>
      <Text style={styles.title}>Companion, the digital accompanist</Text>
      
      <View style={styles.button_wrapper}>
        <Score_Select state={state} dispatch={dispatch}/>
        <TempoBox state={state} dispatch={dispatch} wrapper_style={styles.measure_box} text_input_style={styles.text_input} label_text_style={styles.label}/>
        <Start_Stop_Button state={state} dispatch={dispatch}
        button_style={styles.play_button} text_style={styles.button_text}
        />
        <MeasureSetBox
          state={state} dispatch={dispatch} wrapper_style={styles.measure_box}
          text_input_style={styles.text_input} button_style={styles.reset_button} button_text_style={styles.button_text} label_text_style={styles.label}
        />
      </View>
      <ScoreDisplay state={state} dispatch={dispatch}/>
      <StatusBar style="auto" />
      {/* Automatically adjusts the status bar style */}
      <AudioPlayerRefactored state={state} dispatch={dispatch}/>
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
  play_button: {
    flex: 0.2,
    borderColor: "black",
    borderRadius: 15,
    backgroundColor: 'lightblue',
    justifyContent: 'center',
  },
  reset_button: {
    flex: 0.8,
    borderColor: 'black',
    borderRadius: 15,
    backgroundColor: 'lightblue',
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
    backgroundColor: 'lightgray',
    width: '100%',
    minHeight: 72
  },
  measure_box: {
    flexDirection: 'row',
    padding: 10,
    justifyContent: 'space-between',
    width: '40%',
    flex: 0.4,
    height: '80%',
  },
  text_input: {
    backgroundColor: 'white',
    flex: 0.3,
    height: '100%'
  }
});
