// Import necessary modules and components from the Expo and React Native libraries
import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View, Image, SafeAreaView } from "react-native";
import React, { useEffect, useReducer, useRef, useState } from "react";
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

  ////////////////////////////////////////////////////////////////////////////////
  // CandP
  ////////////////////////////////////////////////////////////////////////////////
  // State for whether we have microphone permissions - is set to true on first trip to playmode
    const [permission, setPermission] = useState(false);
    // Assorted audio-related objects in need of reference
    // Tend to be re-created upon starting a recording
    const mediaRecorder = useRef<MediaRecorder>(
      new MediaRecorder(new MediaStream()),
    );
    const [stream, setStream] = useState<MediaStream>(new MediaStream());
    const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  
    const audioContextRef = useRef<any>(null);
    const analyserRef = useRef<any>(null);
    const dataArrayRef = useRef<any>(null);
    const startTimeRef = useRef<any>(null);
  
      /////////////////////////////////////////////////////////
      // This function sends a synchronization request and updates the state with the result
      const UPDATE_INTERVAL = 100;
  
      const getAPIData = async () => {
        analyserRef.current?.getByteTimeDomainData(dataArrayRef.current);
        const {
          playback_rate: newPlayRate,
          estimated_position: estimated_position,
        } = await synchronize(state.sessionToken, Array.from(dataArrayRef.current), state.timestamp);
    
        dispatch({
          type: "increment",
          time: estimated_position,
          rate: newPlayRate,
        });
      }
  
    // Starts recorder instances
    const startRecording = async () => {
      startTimeRef.current = Date.now();
      //create new Media recorder instance using the stream
      const media = new MediaRecorder(stream, { mimeType: "audio/webm" });
      //set the MediaRecorder instance to the mediaRecorder ref
      mediaRecorder.current = media;
      //invokes the start method to start the recording process
      mediaRecorder.current.start();
      let localAudioChunks: Blob[] = [];
      mediaRecorder.current.ondataavailable = (event) => {
        if (typeof event.data === "undefined") return;
        if (event.data.size === 0) return;
        localAudioChunks.push(event.data);
      };
      setAudioChunks(localAudioChunks);
  
      audioContextRef.current = new window.AudioContext();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 2048;
      source.connect(analyserRef.current);
  
      const bufferLength = analyserRef.current.frequencyBinCount;
      dataArrayRef.current = new Uint8Array(bufferLength);
  
      getAPIData(); // run the first call
    };
  
    //stops the recording instance
    const stopRecording = () => {
      mediaRecorder.current.stop();
      audioContextRef.current?.close();
    };
  
    // Function to get permission to use browser microphone
    const getMicrophonePermission = async () => {
      if ("MediaRecorder" in window) {
        try {
          const streamData = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: false,
          });
          setPermission(true);
          setStream(streamData);
        } catch (err) {
          alert((err as Error).message);
        }
      } else {
        alert("The MediaRecorder API is not supported in your browser.");
      }
    };
  
    // Get microphone permission on first time entering play state
    useEffect(() => {
      if (!permission) getMicrophonePermission();
    }, [state.inPlayMode]);
  
    // Start and stop recording when player is or isn't playing
    useEffect(() => {
      if (state.playing) startRecording();
      else stopRecording();
    }, [state.playing]);
  
    useEffect(() => {
      if (state.playing) setTimeout(getAPIData, UPDATE_INTERVAL);
    }, [state.timestamp])

  ////////////////////////////////////////////////////////////////////////////////
  // Render the component's UI
  ////////////////////////////////////////////////////////////////////////////////
  return (
    <SafeAreaView style={styles.container}>
      {/* Provides safe area insets for mobile devices */}
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
