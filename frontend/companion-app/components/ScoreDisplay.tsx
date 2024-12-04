// Import necessary modules and components from the Expo and React Native libraries
import { StatusBar } from "expo-status-bar"; // Manages the status bar on mobile devices
import { StyleSheet, Text, View, SafeAreaView } from "react-native"; // Imports styling and layout components
import React, { useEffect, useRef, useState } from "react"; // Imports React and hooks
import { OpenSheetMusicDisplay, Cursor } from "opensheetmusicdisplay"; // Imports the OpenSheetMusicDisplay library for rendering sheet music
// import {GET_Request, POST_Request, Play_Audio} from "./components/Api_Caller";
import { AudioPlayer } from "./AudioPlayer";
import { Play_Button } from "./Play_Button";
import { Score_Select } from "./Score_Select";
import { Stop_Button } from "./Stop_Button";
import { TimeStampBox } from "./TimeStampBox";

import { MeasureSetBox } from "./MeasureSetter";
import { Fraction } from "opensheetmusicdisplay";
import AudioRecorder from "./AudioRecorder";

// Define the main application component
export function ScoreDisplay() {
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

  // Create a state holding the cursor (a ref didn't work)
  const cursorRef = useRef<Cursor | null>(null);
  const osdRef = useRef<OpenSheetMusicDisplay | null>(null);

  // And one determining whether the piece is currently playing
  const [playing, setPlaying] = useState(false);

  const [cursorPos, setCursorPos] = useState<number>(-1); // this and all features using it are to be deprecated
  const [timestamp, setTimestamp] = useState<number>(0); // timestamp in seconds which the cursor attempts to approximate
  const [cursorExactTimestamp, setCursorExactTimestamp] = useState<number>(0); // timestamp of the note the cursor is at

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

  const BPM = 100; // EDIT THESE AS APPROPRIATE
  const TSD = 4;

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

  // useEffect to update the time-stamp
  useEffect(() => {
    // move the cursor based on the timestamp!
    let ct = cursorExactTimestamp; // current timestamp of cursor's note(s) in seconds
    var dt;
    if (cursorRef.current?.Iterator.CurrentSourceTimestamp !== undefined) {
      var ts_meas = Fraction.createFromFraction(
        cursorRef.current?.Iterator.CurrentSourceTimestamp,
      ); // current timestamp of iterator as a fraction
      var ts_start = Fraction.createFromFraction(ts_meas); // where iterator starts from, as a fraction

      // while timestamp is less than desired, update it
      while (ct < timestamp) {
        cursorRef.current?.Iterator.moveToNextVisibleVoiceEntry(false);
        dt = Fraction.minus(
          cursorRef.current?.Iterator.CurrentSourceTimestamp,
          ts_meas,
        );
        // dt is a fraction indicating how much - in whole notes - the iterator moved

        // // If we are using the active BPM and time signature in the given score, uncomment:
        // ct += 60 * dt.RealValue * cursorRef.current?.Iterator.CurrentMeasure.ActiveTimeSignature.Denominator / cursorRef.current?.Iterator.CurrentBpm
        // // and remove the BPM and TSD arguments used in the below, and comment the below:
        ct += (60 * dt.RealValue * TSD) / BPM;
        // // either way, the calculation is:
        // 60 secs/min * dt wholes * time signature denominator (beats/whole) / BPM (beats/minute) yields seconds
        ts_meas = Fraction.plus(ts_meas, dt);
      }
      cursorRef.current?.Iterator.moveToPreviousVisibleVoiceEntry(false);
      setCursorExactTimestamp(
        cursorExactTimestamp +
          (60 *
            Fraction.minus(
              cursorRef.current?.Iterator.CurrentSourceTimestamp,
              ts_start,
            ).RealValue *
            TSD) /
            BPM,
      );
      cursorRef.current?.update();
    }

    if (osdRef.current !== undefined && osdRef.current?.Sheet !== undefined) {
      osdRef.current.render();
    }
  }, [timestamp]);

  // Render the component's UI
  return (
    <SafeAreaView style={{display: "flex", justifyContent: "center", alignItems: "center", width: "100%", overflow: "scroll"}}>
      {/* Provides safe area insets for mobile devices */}
      <AudioRecorder />
      <Text style={styles.title}>Companion, the digital accompanist</Text>
      <Score_Select
        scores={scores}
        setScore={setScore}
        onFileUpload={handleFileUpload}
      />

      <View style={styles.button_wrapper}>
        <Play_Button
          my_cursor={cursorRef}
          playing={playing}
          setPlaying={setPlaying}
          button_style={styles.button}
          text_style={styles.button_text}
          cursorPos={cursorPos}
          setCursorPos={setCursorPos}
          osdRef={osdRef}
        />
        <Stop_Button
          setPlaying={setPlaying}
          button_style={styles.button}
          text_style={styles.button_text}
        />
        <MeasureSetBox
          setTimestamp={setCursorExactTimestamp}
          cursorRef={cursorRef}
          text_input_style={styles.text_input}
          button_style={styles.button}
          button_text_style={styles.button_text}
          label_text_style={styles.label}
          BPM={BPM}
          TSD={TSD}
        />
        <TimeStampBox
          timestamp={timestamp}
          setTimestamp={setTimestamp}
          style={styles.text_input}
        />
      </View>

      <div style={{overflow: "auto", width: "100%", height: "300px"}}>
        {" "}
        {/* Container for scrolling the sheet music */}
        <Text>
          Cursor position (used by deprecated play button): {cursorPos}
        </Text>
        <div ref={osmContainerRef}></div> Reference
        to the SVG container for sheet music
      </div>

      <StatusBar style="auto" />
      {/* Automatically adjusts the status bar style */}

      {/* <GET_Request/>
      <POST_Request/> */}
      <AudioPlayer />
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
    overflow: "scroll"
  },
  title: {
    fontSize: 20, // Set the font size for the title
    marginBottom: 20, // Add space below the title
  },
  label: {
    fontSize: 12,
  },
  scrollContainer: {
    width: "100%", // Make the scroll container fill the width of the parent
    height: '100%', // Set a specific height for scrolling (adjust as needed)
    overflow: "scroll", // Enable vertical scrolling
    borderWidth: 1, // Add border to the container
    borderColor: "black", // Set border color to black
  },
  osmContainer: {
    width: "100%", // Make the sheet music container fill the width of the parent
    minHeight: "100%", // Set a minimum height to ensure scrolling is possible
    borderWidth: 1, // Add border to the sheet music container
    borderColor: "black", // Set border color to black
    // overflow: "hidden", // Ensure content doesn't overflow outside this container
  },
  button: {
    flex: 0.2,
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
    minHeight: 64,
  },
  text_input: {
    backgroundColor: "white",
    flex: 0.3,
  },
});

export function MusicXMLStringDisplay(musicXMLString: string) {
    const containerRef = useRef<HTMLDivElement | null>(null);
    const scoreRef = useRef<OpenSheetMusicDisplay | null>(null);

    useEffect(() => {
        if (!scoreRef.current) {
            scoreRef.current = new OpenSheetMusicDisplay(containerRef.current as HTMLElement, {
                autoResize: true,
                drawTitle: true,
            })
        }

        if (musicXMLString) {
            scoreRef.current.load(musicXMLString).then(() => {
                scoreRef.current?.render()
            })
            .catch((error) => {
                console.error(error);
            })
        }

        return () => {
            if (scoreRef.current) {
                scoreRef.current.clear();
                scoreRef.current = null;
            }
        };
    }, [musicXMLString]);

    return (
        <div ref={containerRef}></div>
    );
}