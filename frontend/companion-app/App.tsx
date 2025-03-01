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
  // The lines below were modified, copied and pasted out of the audio recorder object
  // (which never really needed a UI).
  // *** THE ACT OF MOVING THEM FROM A COMPONENT TO APP.TSX MADE THE INTERFACE WORK ***
  // *** Probably has to do with parent/child component state something idk ***
  ////////////////////////////////////////////////////////////////////////////////

  // Audio-related states and refs
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
  
  // Audio-related functions
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
  
  // This function established new recording instances when re-entering play mode
  const startRecording = async () => {
    // It's possible some of these can be removed; not sure which relate to the 
    // making of the recorded object we don't need and which relate to the
    // buffer we send to the backend.
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
  
  /////////////////////////////////////////////
  // Audio-related effects
  // Get microphone permission on first time entering play state
  useEffect(() => {
    if (!permission) getMicrophonePermission();
  }, [state.inPlayMode]);
  
  // Start and stop recording when player is or isn't playing
  useEffect(() => {
    if (state.playing) startRecording();
    else stopRecording();
  }, [state.playing]);

  // Keep synchronizing while playing
  useEffect(() => {
    if (state.playing) setTimeout(getAPIData, UPDATE_INTERVAL);
  }, [state.timestamp])

  ////////////////////////////////////////////////////////////////////////////////
  // Render the component's UI
  ////////////////////////////////////////////////////////////////////////////////
  return (
    <SafeAreaView style={styles.container}>
        {/* Provides safe area insets for mobile devices */}

        {/* Header with image */}
        <View style={styles.menu_bar}>
          <Image source={{ uri: './assets/companion.png' }} style={styles.logo}/>
        </View>

        {/* Container used for 1:3 ratio display */}
        <View style={styles.contentWrapper}>

          {/* Sidebar for inputs and buttons (takes up little width) */}
          <View style={styles.sidebar}>
            { // List of scores, show when not in play mode
            state.inPlayMode || <Score_Select state={state} dispatch={dispatch} /> }
            <Return_Button
              state={state}
              dispatch={dispatch}
              button_format={styles.button}
              text_style={styles.button_text}
            />
            
            {
              state.inPlayMode ?
              <MeasureSetBox
                state={state}
                dispatch={dispatch}
                button_style={styles.button}
                button_text_style={styles.button_text}
              />
              :
              <TempoBox
                state={state}
                dispatch={dispatch}
                label_text_style={styles.button_text}
              />
            }
            <Start_Stop_Button
              state={state}
              dispatch={dispatch}
              button_format={styles.button}
              text_style={styles.button_text}
            />
          </View>

          {/* Actual content display (takes up remaining width after sidebar) */}
          <View style={styles.mainContent}>
            <ScoreDisplay state={state} dispatch={dispatch} />
          </View>

        </View>
          
        {/* Footer display for status */}
        <StatusBar style="auto" />
        {/* Automatically adjusts the status bar style */}
        <AudioPlayer state={state} />
    </SafeAreaView>
  );
}

// Define styles for the components using StyleSheet
const styles = StyleSheet.create({

  // Main container for entire content
  container: {
    flex: 1,
    backgroundColor: "#F5F5F5",
  },
  // Header container 
  menu_bar: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#2C3E50",
    padding: 10,
    borderBottomWidth: 2,
    borderBottomColor: "#1A252F",
    height: 80, 
  },
  // Image for header
  logo: {
    height: 200,
    width: 200,
    resizeMode: "contain",
  },

  // Container displaying sidebar and main content (row form)
  contentWrapper: {
    flexDirection: "row",
    flex: 1,
    padding: 10,
  },

  // Side bar container for buttons and inputs (column display)
  sidebar: {
    width: "25%",
    backgroundColor: "#ECF0F1",
    padding: 25,
    borderRadius: 10,
    gap: 6,
    // Shadow style found online
    shadowColor: "#000000",
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity:  0.17,
    shadowRadius: 3.05,
    elevation: 4,
  },

  // Container displaying score sheet 
  mainContent: {
    flex: 1,
    marginLeft: 15,
    backgroundColor: "#FFFFFF",
    padding: 15,
    borderRadius: 10,
    // Shadow style found online
    shadowColor: "#000000",
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity:  0.17,
    shadowRadius: 3.05,
    elevation: 4,
  },

  // Primary button styles
  button: {
    backgroundColor: "#2C3E50",
    padding: 10,
    borderRadius: 8,
    alignItems: "center",
    marginVertical: 5,

  },

  // Primary button text
  button_text: {
    textAlign: "center",
    fontSize: 14,
    color: "#FFFFFF",
    fontWeight: "bold",
  },
});
