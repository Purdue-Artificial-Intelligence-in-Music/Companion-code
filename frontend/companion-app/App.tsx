// Import necessary modules and components from the Expo and React Native libraries
import { StatusBar } from 'expo-status-bar'; // Manages the status bar on mobile devices
import { StyleSheet, Text, View, SafeAreaView} from 'react-native'; // Imports styling and layout components
import React, { useEffect, useReducer, useRef, useState } from 'react'; // Imports React and hooks
import { OpenSheetMusicDisplay, Cursor } from 'opensheetmusicdisplay'; // Imports the OpenSheetMusicDisplay library for rendering sheet music
import {GET_Request, POST_Request, Play_Audio} from "./components/Api_Caller";
import { Score_Select } from './Components';
import { Start_Stop_Button } from './components/StartButton';
import { MeasureSetBox } from './components/MeasureSetter';
import { Fraction } from 'opensheetmusicdisplay';
import AudioRecorder from './components/AudioRecorder';
import { Audio } from 'expo-av';
import reducer_function from './Dispatch';
  
// Define the main application component
export default function App() {
  // Create a reference to the SVG container where sheet music will be rendered
  const osmContainerRef = useRef<HTMLDivElement | null>(null); // Reference for the SVG container

  // Directory of scores with filenames and piece names (names for the selection display)
  const [scores, setScores] = useState([
    {
      filename: "air_on_the_g_string.musicxml",
      piece: "Bach - Air on the G String",
    },
    { filename: "twelve_duets.musicxml", piece: "Mozart - Twelve Duets" },
  ]);

  // Create a state representing the file name of the current piece
  const [score, setScore] = useState("air_on_the_g_string.musicxml");

  // This state *is* the audio player - access it at top-level
  const [sound, setSound] = useState<Audio.Sound | null>(null);

  // Create refs to the cursor and to the OSDiv
  const cursorRef = useRef<Cursor | null>(null);
  const osdRef = useRef<OpenSheetMusicDisplay | null>(null);

  const BPM = 100; // EDIT THESE AS APPROPRIATE - get from user??
  const TSD = 4;

  const UPDATE_INTERVAL = 500; // milliseconds between updates to timestamp and rate

  ////////////////////////////////////////////////////////////////////////////////////
  // Main state - holds position in the piece, playback rate, etc.
  ////////////////////////////////////////////////////////////////////////////////////
  const [state, dispatch] = useReducer( reducer_function,
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
      tempo:100,
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
  
  //////////////////////////////////////////////////////////////
  // Action function for file uploader
  const handleFileUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const xmlContent = e.target?.result as string;
      const newScore = {
        filename: file.name,
        piece: file.name.replace(".musicxml", ""),
        content: xmlContent,
      };
      setScores([...scores, newScore]); //append the new score to scores list
      setScore(file.name);
    };
    reader.readAsText(file);
  };

  // !!! TODO !!!
  const getAPIData = async () => {
    // try {
    //   const syncdata = await fetch("http://localhost:5000/synchronization",
    //     {
    //     method:"POST",
    //     headers: {
    //       'session-token':state.sessionToken // fix this
    //     }
    //     },
    //   );
    //   const data_json = await syncdata.json();
    //   dispatch( {type:'increment', time:data_json['estimated_position'], rate:data_json['playback_rate']} )
    // }
    // catch {
    //   console.log("Synchronization must not have occurred.")
    // }
    const newPlayRate = 0.5 + Math.random(); // Update this to actual get data from API!!!
    const newTimeStamp = state.timestamp + UPDATE_INTERVAL * state.playRate / 1000;
    dispatch( {type:'increment', time:newTimeStamp, rate:newPlayRate} )
    
  }

  useEffect(() => {
    if (state.playing) setTimeout(getAPIData, UPDATE_INTERVAL);
  }, [state.playing, state.timestamp])

  // useEffect hook to handle side effects (like loading music) after the component mounts
  // and when a piece is selected
  useEffect(() => {
    // Remove any previously-loaded music
    if (osmContainerRef.current) {
      while (osmContainerRef.current.children[0]) {
        osmContainerRef.current.removeChild(
          osmContainerRef.current.children[0],
        );
      }
    }

    if (score) {
      const selectedScore = scores.find((s) => s.filename === score);
      if (selectedScore) {
        // Create an instance of OpenSheetMusicDisplay, passing the reference to the container
        const osm = new OpenSheetMusicDisplay(
          osmContainerRef.current as HTMLElement,
          {
            autoResize: true, // Enable automatic resizing of the sheet music display
            followCursor: true, // And follow the cursor
          },
        );

        osdRef.current = osm;

        // Load the music XML file from the assets folder
        osm
          .load("assets/" + score)
          .then(() => {
            // Render the sheet music once it's loaded
            osm.render();
            console.log("Music XML loaded successfully"); // Log success message to console
            cursorRef.current = osm.cursor; // Pass reference to cursor
            cursorRef.current.show(); // and never hide it.  it should always be visible
            cursorRef.current.CursorOptions = {
              ...cursorRef.current.CursorOptions,
              ...{ follow: true },
            };
          })
          .catch((error) => {
            // Handle errors in loading the music XML file
            console.error("Error loading music XML:", error); // Log the error message
          });
      }
    }

    // Cleanup function to dispose of the OpenSheetMusicDisplay instance if needed
    return () => {};
  }, [score]); // Dependency array means this effect runs once when the component mounts and again when a new score is selected

  /////////////////////////////////////////////////////////////////////////////////
  // useEffect to tie the cursor position to the state
  /////////////////////////////////////////////////////////////////////////////////
  useEffect( () => {
    let ct = state.cursorTimestamp; // current timestamp of cursor's note(s) in seconds
    var dt = new Fraction();
    console.log("ct:",ct);
    if (cursorRef.current?.Iterator.CurrentSourceTimestamp !== undefined) {
      var ts_meas = Fraction.createFromFraction(cursorRef.current?.Iterator.CurrentSourceTimestamp); // current timestamp of iterator as a fraction
      // var ts_start = Fraction.createFromFraction(ts_meas); // where iterator starts from, as a fraction

      console.log("ts_meas:",ts_meas.RealValue);
      if (ct > state.timestamp) { // If timestamp is older, go back to beginning, b/c probably reset
        console.log("Moving ct back to beginning.");
        ct = 0;
        cursorRef.current?.reset();
        ts_meas = new Fraction();
      }

      // while timestamp is less than desired, update it
      while (ct <= state.timestamp ) {
        cursorRef.current?.Iterator.moveToNextVisibleVoiceEntry(false);
        dt = Fraction.minus(
          cursorRef.current?.Iterator.CurrentSourceTimestamp,
          ts_meas,
        );
        // dt is a fraction indicating how much - in whole notes - the iterator moved

        // // If we are using the active BPM and time signature in the given score, uncomment:
        // ct += 60 * dt.RealValue * cursorRef.current?.Iterator.CurrentMeasure.ActiveTimeSignature.Denominator / cursorRef.current?.Iterator.CurrentBpm
        // // and remove the BPM and TSD arguments used in the below, and comment the below:
        ct += 60 * dt.RealValue * TSD / BPM;
        console.log("ct:",ct);
        // // either way, the calculation is:
        // 60 secs/min * dt wholes * time signature denominator (beats/whole) / BPM (beats/minute) yields seconds
        ts_meas = Fraction.plus(ts_meas, dt);
      }
      cursorRef.current?.Iterator.moveToPreviousVisibleVoiceEntry(false);
      console.log("Cursor should be updating");
      cursorRef.current?.update();
      dispatch( {type:'cursor_update', time:(60 * cursorRef.current?.Iterator.CurrentSourceTimestamp.RealValue * TSD / BPM)})
    }  
                
    // if (osdRef.current !== undefined && osdRef.current?.Sheet !== undefined) {
    //   console.log("Should be re-rendering.");
    //   osdRef.current.render();
    // } // COMMENTING THIS OUT FIXED IT AND I DON"T KNOW WHY!!!!! ❤️ Robert
  }, [state.timestamp])

  ///////////////////////////////////////////////////////////////////////////////////////
  // Two useEffects that tie the sound playback to the state
  ///////////////////////////////////////////////////////////////////////////////////////
  useEffect( () => {
    const updateThePlayRate = async () => {
      if (sound) {
        await sound.setRateAsync(state.playRate, true);
      }
    }
    updateThePlayRate();
  }, [state.playRate])

  useEffect( () => {
    const updateWhetherPlaying = async () => {
      if (sound) {
        if (state.playing) await sound.playAsync()
        else await sound.pauseAsync()
      }
    }
    updateWhetherPlaying();
  }, [state.playing])

  // TODO:  Skip the point in sound when resetting?

  ////////////////////////////////////////////////////////////////////////////////
  // Render the component's UI
  ////////////////////////////////////////////////////////////////////////////////
  return (
    <SafeAreaView style={styles.container}>
      {/* Provides safe area insets for mobile devices */}
      <AudioRecorder />
      <Text style={styles.title}>Companion, the digital accompanist</Text>
      
      <View style={styles.button_wrapper}>
        <Score_Select scores={scores} setScore={setScore} onFileUpload={handleFileUpload}/>
        <Start_Stop_Button state={state} dispatch={dispatch}
        button_style={styles.play_button} text_style={styles.button_text}
        />
        <MeasureSetBox
          state={state} dispatch={dispatch} wrapper_style={styles.measure_box}
          text_input_style={styles.text_input} button_style={styles.reset_button} button_text_style={styles.button_text} label_text_style={styles.label}
          BPM={BPM} TSD={TSD}
        />
        {/* <TimeStampBox timestamp={timestamp} setTimestamp={setTimestamp} style={styles.text_input}/> */}
      </View>

      <div style={styles.scrollContainer}> {/* Container for scrolling the sheet music */}
        <div ref={osmContainerRef} style={styles.osmContainer}>
          </div> Reference to the SVG container for sheet music
      </div>

      <StatusBar style="auto" />
      {/* Automatically adjusts the status bar style */}

      { /* <GET_Request/>
      <POST_Request/> */ }
      {/* <AudioPlayer/> */}
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
  scrollContainer: {
    width: "100%", // Make the scroll container fill the width of the parent
    height: "80%", // Set a specific height for scrolling (adjust as needed)
    overflow: "scroll", // Enable vertical scrolling
    borderWidth: 1, // Add border to the container
    borderColor: "black", // Set border color to black
  },
  osmContainer: {
    width: "100%", // Make the sheet music container fill the width of the parent
    minHeight: "150%", // Set a minimum height to ensure scrolling is possible
    borderWidth: 1, // Add border to the sheet music container
    borderColor: "black", // Set border color to black
    overflow: "hidden", // Ensure content doesn't overflow outside this container
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
