// Import necessary modules and components from the Expo and React Native libraries
import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View, Image, SafeAreaView, TouchableOpacity, useWindowDimensions, ScrollView, TextStyle, Animated } from "react-native";
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
import Icon from 'react-native-vector-icons/Feather';

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
  // State to conditionally render the style type of the components (can only be "light" or "dark")
  const [theme, setTheme] = useState<"light" | "dark">("light");

  // Creating animated values using useRef for UI animation
  const backgroundColorAnim = useRef(new Animated.Value(0)).current; 
  const textColorAnim = useRef(new Animated.Value(0)).current; 
  const borderBottomAnim = useRef(new Animated.Value(0)).current;
  const borderColorAnim = useRef(new Animated.Value(0)).current;

  // Interpolate background color based on light or dark mode
  const containerBackgroundColor = backgroundColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["#F5F5F5", "#1A1A1A"], // Light to dark
  });
  // Interpolate text color based on light or dark mode
  const textColor = textColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["#2C3E50", "#FFFFFF"], // Light to dark
  });
  // Interpolate text color based on light or dark mode
  const invertTextColor = textColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["#FFFFFF", "#2C3E50"], // Light to dark
  });
  // Interpolate sidebar bg color based on light or dark mode
  const sidebarBackgroundColor = backgroundColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["#ECF0F1", "#4A627A"], // Light to dark
  });
  // Interpolate mainContent container bg color based on light or dark mode
  const mainContentBackgroundColor = backgroundColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["#FFFFFF", "#A3B9D3"], // Light to dark
  });
  // Interpolate button bg color based on light or dark mode
  const buttonBackgroundColor = backgroundColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["#2C3E50", "#FFFFFF"], // Light to dark
  });
  // Interpolate header and footer container color based on light or dark mode
  const menubarBackgroundColor =  backgroundColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["#2C3E50", "#1A252F"], // Light to dark
  });
  // Interpolate border bottom color based on light or dark mode
  const borderBottomColor = borderBottomAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["#2C3E50", "#FFFFFF"], // Light to dark transition
  });
  // Interpolate border bottom color based on light or dark mode
  const borderColor = borderColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["#FFFFFF", "#2C3E50"], // Light to dark transition
  })


  // Toggles between light and dark mode by animating background, text, and border properties smoothly
  const toggleTheme = () => {
    const toValue = theme === "light" ? 1 : 0;
    Animated.parallel([
      Animated.timing(backgroundColorAnim, {
        toValue,
        duration: 500, 
        useNativeDriver: false, // `backgroundColor` is not supported by native driver
      }),
      Animated.timing(textColorAnim, {
        toValue,
        duration: 500,
        useNativeDriver: false, // `color` is not supported by native driver
      }),
      Animated.timing(borderBottomAnim, {
        toValue,
        duration: 500,
        useNativeDriver: false, // Can't use native driver for border properties
      }), 
      Animated.timing(borderColorAnim, {
        toValue,
        duration: 500,
        useNativeDriver: false, // Can't use native driver for border properties
      }),
    ]).start(() => {
      setTheme(theme === "light" ? "dark" : "light");
    });
  };
  // Get device's width 
  const { width } = useWindowDimensions()
  // Boolean used for dynmaic display (row or column)
  const isSmallScreen = width < 768;

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
    <SafeAreaView style={[styles.container, themeStyles[theme].container]}>
        {/* Provides safe area insets for mobile devices */}
        <Animated.View style={[styles.container, { backgroundColor: containerBackgroundColor }]}>

          {/* Scroll View used for device scroll for content going over the frame */}
          <ScrollView contentContainerStyle={isSmallScreen ? { flexGrow: 1 } : {height: "100%"}}>
          {/* Header with image */}
          <Animated.View style={[styles.menu_bar, themeStyles[theme].menu_bar, {backgroundColor: menubarBackgroundColor}]}>
            <Image source={{ uri: './assets/companion.png' }} style={styles.logo}/>
            
            <TouchableOpacity onPress={toggleTheme}>
              <Icon name={theme === 'light' ? 'sun' : 'moon'} size={30} color="white" />
            </TouchableOpacity>
          </Animated.View>

          {/* Container used for 1:3 ratio display */}
          <View style={[styles.contentWrapper, isSmallScreen ? styles.contentWrapperColumn : styles.contentWrapperRow]}>

            {/* Sidebar for inputs and buttons (takes up little width) */}
            <Animated.View style={[styles.sidebar,  themeStyles[theme].sidebar, { backgroundColor: sidebarBackgroundColor }, isSmallScreen ? styles.sidebarColumn : {}]}>
              { // List of scores, show when not in play mode
              state.inPlayMode || <Score_Select state={state} dispatch={dispatch} textStyle={textColor} borderStyle={borderBottomColor}/> }
              <Return_Button
                state={state}
                dispatch={dispatch}
                button_format={[styles.button, {backgroundColor:buttonBackgroundColor, borderColor: borderColor}]}
                text_style={invertTextColor}
              />
              
              {
                state.inPlayMode ?
                <MeasureSetBox
                  state={state}
                  dispatch={dispatch}
                  button_style={[styles.button, {backgroundColor: buttonBackgroundColor, borderColor: borderColor}]}
                  button_text_style={invertTextColor}
                />
                :
                <TempoBox
                  state={state}
                  dispatch={dispatch}
                  label_text_style={styles.button_text}
                  textStyle={textColor}
                />
              }
              <Start_Stop_Button
                state={state}
                dispatch={dispatch}
                button_format={[styles.button, {backgroundColor: buttonBackgroundColor, borderColor: borderColor}]}
                text_style={invertTextColor}
              />
            </Animated.View>

            {/* Actual content display (takes up remaining width after sidebar) */}
            <Animated.View style={[styles.mainContent, themeStyles[theme].mainContent, {backgroundColor: mainContentBackgroundColor}, isSmallScreen ? styles.mainContentColumn : {}]}>
              <ScoreDisplay state={state} dispatch={dispatch} />
            </Animated.View>

          </View>
            
          {/* Footer display for status */}
          <StatusBar style="auto" />
          {/* Automatically adjusts the status bar style */}
          <AudioPlayer state={state}  menuStyle={{ backgroundColor: menubarBackgroundColor }}/>
        </ScrollView>
      </Animated.View>
    </SafeAreaView>
  );
}

// Theme-based styles
const themeStyles = {
  light: {
    container: { backgroundColor: '#F5F5F5' },
    menu_bar: { backgroundColor: '#2C3E50' },
    sidebar: { backgroundColor: '#ECF0F1' },
    mainContent: { backgroundColor: '#FFFFFF' },
    text: { color: "#2C3E50", fontWeight: "bold"} as TextStyle, // use for typscirpt syntax 
    button: {  backgroundColor: "#2C3E50"}
  },
  dark: {
    container: { backgroundColor: '#0F0F0F' },
    menu_bar: { backgroundColor: '#1A252F' },
    sidebar: { backgroundColor: '#4A627A' },
    mainContent: { backgroundColor: '#6B87A3' },
    text: { color: '#ffffff', fontWeight: "bold"} as TextStyle, // use for typscirpt syntax 
    button: {  backgroundColor: "#ffffff"}

  },
};

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
    justifyContent: "space-between",
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
    gap: 10,
    flex: 1,
    padding: 20,
  },
  // Container displaying sidebar and main content (row form)
  contentWrapperRow: {
    flexDirection: "row",
  },
  contentWrapperColumn: {
    flexDirection: "column",
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
  sidebarColumn: {
    width: "100%", // Full width on smaller screens
  },
  // Container displaying score sheet 
  mainContent: {
    flex: 1,
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
  mainContentColumn: {
    width: "100%", // Full width on smaller screens
  },
  // Primary button styles
  button: {
    padding: 10,
    borderRadius: 8,
    alignItems: "center",
    marginVertical: 5,
    borderWidth: 3, 
  },
  // Primary button text
  button_text: {
    textAlign: "center",
    fontSize: 14,
    color: "#FFFFFF",
    fontWeight: "bold",
  },
});
