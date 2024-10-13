// Import necessary modules and components from the Expo and React Native libraries
import { StatusBar } from 'expo-status-bar'; // Manages the status bar on mobile devices
import { StyleSheet, Text, View, SafeAreaView, Pressable } from 'react-native'; // Imports styling and layout components
import React, { MutableRefObject, useEffect, useRef, useState } from 'react'; // Imports React and hooks
import { OpenSheetMusicDisplay, Cursor } from 'opensheetmusicdisplay'; // Imports the OpenSheetMusicDisplay library for rendering sheet music
import { Play_Button, Next_Button, Score_Select, Stop_Button, RenderSomethingButton } from './assets/Components';

// Define the main application component
export default function App() {
  // Create a reference to the SVG container where sheet music will be rendered
  const osmContainerRef = useRef<HTMLDivElement | null>(null); // Reference for the SVG container

  // Directory of scores with filenames and piece names (names for the selection display)
  const scores = 
    [{"filename":"air_on_the_g_string.musicxml", "piece":"Bach - Air on the G String"},
    {"filename":"twelve_duets.musicxml", "piece":"Mozart - Twelve Duets"}]
  // Create a state representing the file name of the current piece
  const [score, setScore] = useState("air_on_the_g_string.musicxml");
  // Create a state holding the cursor (a ref didn't work)
  const cursor = useRef<Cursor | null>(null);
  const osdRef = useRef<OpenSheetMusicDisplay | null>(null);
  // And one determining whether the piece is currently playing
  const [playing, setPlaying] = useState(false);
  const [cursorPos, setCursorPos] = useState<number>(-1);

  // useEffect hook to handle side effects (like loading music) after the component mounts
  // and when a piece is selected
  // and when a piece is selected
  useEffect(() => {

    // Remove any previously-loaded music
    if (osmContainerRef.current) {
        while (osmContainerRef.current.children[0]) {
          osmContainerRef.current.removeChild(osmContainerRef.current.children[0]);
        }
      }


    // Remove any previously-loaded music
    if (osmContainerRef.current) {
        while (osmContainerRef.current.children[0]) {
          osmContainerRef.current.removeChild(osmContainerRef.current.children[0]);
        }
      }

    // Create an instance of OpenSheetMusicDisplay, passing the reference to the container
    const osm = new OpenSheetMusicDisplay(osmContainerRef.current as HTMLElement, {
      autoResize: true, // Enable automatic resizing of the sheet music display
    });

    osdRef.current = osm;

    osdRef.current = osm;

    // Load the music XML file from the assets folder
    osm.load('assets/' + score)
    osm.load('assets/' + score)
      .then(() => {
        // Render the sheet music once it's loaded
        osm.render();
        console.log('Music XML loaded successfully'); // Log success message to console
        cursor.current = osm.cursor; // Pass reference to cursor
    })
        cursor.current = osm.cursor; // Pass reference to cursor
    })
      .catch((error) => {
        // Handle errors in loading the music XML file
        console.error('Error loading music XML:', error); // Log the error message
      });

    // Cleanup function to dispose of the OpenSheetMusicDisplay instance if needed
    return () => {
    };
  }, [score]); // Dependency array means this effect runs once when the component mounts and again when a new score is selected
  }, [score]); // Dependency array means this effect runs once when the component mounts and again when a new score is selected

  // Render the component's UI
  return (
    <SafeAreaView style={styles.container}>{/* Provides safe area insets for mobile devices */}
      <Text style={styles.title}>Companion, the digital accompanist</Text>
      <Score_Select score={score} scoreOptions={scores} setScore={setScore}/>
      <Play_Button my_cursor={cursor} playing={playing} setPlaying={setPlaying}
       cursorPos={cursorPos} setCursorPos={setCursorPos} osdRef={osdRef}
      />
      <Next_Button my_cursor={cursor}/>
      <Stop_Button setPlaying={setPlaying}/>
      <div style={styles.scrollContainer}> {/* Container for scrolling the sheet music */}
        <Text>Cursor position: {cursorPos}</Text>
        <div ref={osmContainerRef} style={styles.osmContainer}>
          </div> Reference to the SVG container for sheet music
      </div>
      <StatusBar style="auto" />{/* Automatically adjusts the status bar style */}
    </SafeAreaView>
  );
}

// Define styles for the components using StyleSheet
const styles = StyleSheet.create({
  container: {
    flex: 1, // Make the container fill the available space
    backgroundColor: '#fff', // Set background color to white
    alignItems: 'center', // Center children horizontally
    justifyContent: 'center', // Center children vertically
    padding: 16, // Add padding around the container
  },
  title: {
    fontSize: 20, // Set the font size for the title
    marginBottom: 20, // Add space below the title
  },
  scrollContainer: {
    width: '100%', // Make the scroll container fill the width of the parent
    height: '80%', // Set a specific height for scrolling (adjust as needed)
    overflow: 'scroll', // Enable vertical scrolling
    borderWidth: 1, // Add border to the container
    borderColor: 'black', // Set border color to black
  },
  osmContainer: {
    width: '100%', // Make the sheet music container fill the width of the parent
    minHeight: '150%', // Set a minimum height to ensure scrolling is possible
    borderWidth: 1, // Add border to the sheet music container
    borderColor: 'black', // Set border color to black
    overflow: 'hidden', // Ensure content doesn't overflow outside this container
  },
});