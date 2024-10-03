// Import necessary modules and components from the Expo and React Native libraries
import { StatusBar } from 'expo-status-bar'; // Manages the status bar on mobile devices
import { StyleSheet, Text, View, SafeAreaView } from 'react-native'; // Imports styling and layout components
import React, { useEffect, useRef } from 'react'; // Imports React and hooks
import { OpenSheetMusicDisplay } from 'opensheetmusicdisplay'; // Imports the OpenSheetMusicDisplay library for rendering sheet music

// Define the main application component
export default function App() {
  // Create a reference to the SVG container where sheet music will be rendered
  const osmContainerRef = useRef<HTMLDivElement | null>(null); // Reference for the SVG container

  // useEffect hook to handle side effects (like loading music) after the component mounts
  useEffect(() => {
    // Create an instance of OpenSheetMusicDisplay, passing the reference to the container
    const osm = new OpenSheetMusicDisplay(osmContainerRef.current as HTMLElement, {
      autoResize: true, // Enable automatic resizing of the sheet music display
    });

    // Load the music XML file from the assets folder
    osm.load('assets/air_on_the_g_string.musicxml')
      .then(() => {
        // Render the sheet music once it's loaded
        osm.render();
        console.log('Music XML loaded successfully'); // Log success message to console
      })
      .catch((error) => {
        // Handle errors in loading the music XML file
        console.error('Error loading music XML:', error); // Log the error message
      });

    // Cleanup function to dispose of the OpenSheetMusicDisplay instance if needed
    return () => {
    };
  }, []); // Empty dependency array means this effect runs once when the component mounts

  // Render the component's UI
  return (
    <SafeAreaView style={styles.container}> {/* Provides safe area insets for mobile devices */}
      <Text style={styles.title}>OpenSheetMusicDisplay Example</Text> {/* Title text */}
      <div style={styles.scrollContainer}> {/* Container for scrolling the sheet music */}
        <div ref={osmContainerRef} style={styles.osmContainer}></div> {/* Reference to the SVG container for sheet music */}
      </div>
      <StatusBar style="auto" /> {/* Automatically adjusts the status bar style */}
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