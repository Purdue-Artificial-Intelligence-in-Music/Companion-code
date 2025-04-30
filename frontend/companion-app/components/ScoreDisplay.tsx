import { NativeScrollEvent, NativeSyntheticEvent, ScrollView, StyleSheet, Text, TouchableOpacity, View, TextInput} from "react-native";
import { useRef, useEffect, useState } from "react";
import { Cursor, OpenSheetMusicDisplay, Fraction } from "opensheetmusicdisplay";
import Icon from 'react-native-vector-icons/FontAwesome';
import scoresData from "../musicxml/scores"; // Local mapping of score filenames to XML content

export default function ScoreDisplay({
  state,
  dispatch,
}: {
  state: any;
  dispatch: any;
}) {
  // Create a reference to the SVG container where sheet music will be rendered
  const osmContainerRef = useRef<HTMLDivElement | null>(null); // Reference for the SVG container
  // Create refs to the cursor and to the OSDiv
  const cursorRef = useRef<Cursor | null>(null);
  const osdRef = useRef<OpenSheetMusicDisplay | null>(null);

  const scrollViewRef = useRef<ScrollView>(null); // reference to scroll view component
  const scrollPositionRef = useRef<number>(0); // ref to keep track of current y position of scroll view (used ref instead of state to prevent rerender when scroll)
  const [steps, setSteps] = useState<string | null>(""); // state for declaring number of intended cursor iterations
  const [speed, setSpeed] = useState<string | null>(""); // state for speed of cursor update

  useEffect(()=> {
    if (!cursorRef.current) {
      console.error("Cursor not initialized.");
      return;
    }
    scrollPositionRef.current = 0;

      const moveCursorStep = (currentTime: number) => {
        console.log("Current Time:", currentTime);
        const newTime = currentTime + 0.1; // Convert speed from ms to seconds
        dispatch({ type: "update_timestamp", timestamp: newTime });
        setTimeout(() => {
          moveCursorStep(newTime);
        }, 0.1 * 1000);
      };
    
    // moveCursorStep(0, state.timestamp);
    moveCursorStep(state.timestamp);
  }, [dispatch, state.playing]);

  // Function that is used to move cursor x amount of steps, updating the cursor y milleconds
  const moveCursorAhead = () => {
    // Check if cursor is referenced
    if (!cursorRef.current) {
      console.error("Cursor not initialized.");
      return;
    }
    // Make sure Y position is always 0 when starting the cursor 
    scrollPositionRef.current = 0;  

    // Function to move the cursor given the number of steps
    const moveCursorStep = (step: number) => {
        
      // Stop cursor after exceeding a certain number of steps
      if (step >= parseInt(steps)) {
        return;
      }
      console.log("Current Cursor", cursorRef)
      // Move the cursor to the next note
      if (cursorRef.current) {
        cursorRef.current.next()
      }

      // Update sheet visually to see updated cursor placement
      if (osdRef.current) {
        osdRef.current.render();
      }
      
      // Scroll to saved position after rerendering the OSM container
      scrollUp(scrollPositionRef.current);

      // Schedule the next step after a delay (speed state decides how fast cursor should update)
      // setTimeout(() => {
      //   moveCursorStep(step + 1);
      // }, parseInt(speed)); 
      setTimeout(() => {
        moveCursorStep(step + 1);
      }, 1000); 
    };

    // run move cursor function given an intial starting step number
    moveCursorStep(0);
  };

  useEffect(()=> {
    // Remove any previously-loaded music
    if (osmContainerRef.current) {
      while (osmContainerRef.current.children[0]) {
        osmContainerRef.current.removeChild(
          osmContainerRef.current.children[0],
        );
      }
    }

    if (state.score) {
      const selectedScore: string = state.score;
      console.log("Selected score:", selectedScore);
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
        // If score name is a key within ScoreContents use the xml content value within that key, otherwise access xml content through the static key value mapping defined within scores.ts
        const xmlContent = (state.scoreContents && state.scoreContents[selectedScore]) || scoresData[selectedScore];
        // Error handling if no xml content for selected score is found
        if (!xmlContent) {
          console.error("Score content not found for:", selectedScore);
          return;
        }

        // Load and render the XML content.
        osm
          .load(xmlContent)
          .then(() => {
            // Render the sheet music
            osm.render();
            console.log("Music XML loaded successfully");
            cursorRef.current = osm.cursor;
            cursorRef.current.show();  // Ensure the cursor is visible
            cursorRef.current.CursorOptions = {
              ...cursorRef.current.CursorOptions,
              follow: true,
            };
              
            // TODO!  Find the piece's tempo and send that instead of constant 100
            dispatch({
              type: "update_piece_info",
              time_signature:
                cursorRef.current.Iterator.CurrentMeasure.ActiveTimeSignature,
              tempo: 100,
            });
          })
          .catch((error) => {
            // Handle errors in loading the music XML file
            console.error("Error loading music XML:", error);
          });

        // // Fetch the MusicXML file from the backend
        // fetch(`http://127.0.0.1:5000/score/${state.score}`) // Replace with your actual API endpoint
        //   .then((response) => {
        //     if (!response.ok) {
        //       throw new Error(`HTTP error! status: ${response.status}`);
        //     }
        //     return response.text(); // Return the XML content as a string
        //   })
        //   .then((xmlContent) => {
        //     // Load the fetched XML content into OpenSheetMusicDisplay
        //     return osm.load(xmlContent);
        //   })
        //   .then(() => {
        //     // Render the sheet music
        //     osm.render();
        //     console.log("Music XML loaded successfully");

        //     cursorRef.current = osm.cursor;
        //     cursorRef.current.show(); // Ensure the cursor is visible
        //     cursorRef.current.CursorOptions = {
        //       ...cursorRef.current.CursorOptions,
        //       follow: true,
        //     };
        //     // TODO!  Find the piece's tempo and send that instead of constant 100
        //     dispatch({
        //       type: "update_piece_info",
        //       time_signature:
        //         cursorRef.current.Iterator.CurrentMeasure.ActiveTimeSignature,
        //       tempo: 100,
        //     });
        //   })
        //   .catch((error) => {
        //     // Handle errors in loading the music XML file
        //     console.error("Error loading music XML:", error); // Log the error message
        //   });
      }
    

    // Cleanup function to dispose of the OpenSheetMusicDisplay instance if needed
    //return () => {};
  }; // Dependency array means this effect runs once when the component mounts and again when a new score is selected
  }, [dispatch, state.score, state.scores])

  // Function used for scrolling vertically through the OSM Container based on passed in value
  const scrollUp = (amount: number) => {
    if (scrollViewRef.current) {
      scrollViewRef.current.scrollTo({ y: amount, animated: false });
    }
  };

  // Function used to listen to scroll on OSM container and saves current Y position
  const handleScroll = (event: NativeSyntheticEvent<NativeScrollEvent>) => {
    const yOffset = event.nativeEvent.contentOffset.y;
    // console.log('Current Scroll Position (Y):', yOffset);
    scrollPositionRef.current = yOffset; // update ref immediately
  };
  
  /////////////////////////////////////////////////////////////////////////////////
  // useEffect to tie the cursor position to the state
  /////////////////////////////////////////////////////////////////////////////////
  useEffect(() => {
    let ct = state.cursorTimestamp; // current timestamp of cursor's note(s) in seconds
    var dt = new Fraction();
    console.log("ct:", ct);
    if (cursorRef.current?.Iterator.CurrentSourceTimestamp !== undefined) {
      var ts_meas = Fraction.createFromFraction(
        cursorRef.current?.Iterator.CurrentSourceTimestamp,
      ); // current timestamp of iterator as a fraction
      console.log("ts_meas:", ts_meas.RealValue);
      // if (ct > state.timestamp) {
      //   // If timestamp is older, go back to beginning, b/c probably reset
      //   console.log("Moving ct back to beginning.");
      //   ct = 0;
      //   cursorRef.current?.reset();
      //   ts_meas = new Fraction();
      // }

      // while timestamp is less than desired, update it
      while (ct <= state.timestamp) {
        cursorRef.current?.Iterator.moveToNextVisibleVoiceEntry(false);
        dt = Fraction.minus(
          cursorRef.current?.Iterator.CurrentSourceTimestamp,
          ts_meas,
        );
        // dt is a fraction indicating how much - in whole notes - the iterator moved

        ct +=
          (60 * dt.RealValue * state.time_signature.Denominator) /
          state.synth_tempo;
        console.log("ct:", ct);
        ts_meas = Fraction.plus(ts_meas, dt);
      }
      cursorRef.current?.Iterator.moveToPreviousVisibleVoiceEntry(false);
      console.log("Cursor should be updating");
      cursorRef.current?.update();
      dispatch({
        type: "cursor_update",
        time:
          (60 *
            cursorRef.current?.Iterator.CurrentSourceTimestamp.RealValue *
            state.time_signature.Denominator) /
          state.synth_tempo,
      });
    }
  }, [state.timestamp]);

  return (
    <>
      {/* Temporary inputs for testing cursor movement */}
      <TextInput
        value={steps !== null ? steps.toString() : ""}
        onChangeText={(text) => {
          setSteps(text);
        }}
        keyboardType="numeric"
        placeholder="Type Number Of Steps"

      />
      <TextInput
        value={speed !== null ? speed.toString() : ""}
        onChangeText={(text) => {
          setSpeed(text);
        }}
        keyboardType="numeric"
        placeholder="Type Cursor Update Speed (ms)"
      />

      <TouchableOpacity
        onPress={moveCursorAhead}
      >
        <Text>Start</Text>
      </TouchableOpacity>
        
        {/* Reference ScrollView Component for controlling scroll */}
        <ScrollView indicatorStyle="white" contentContainerStyle={{flexGrow: 1}} showsVerticalScrollIndicator={true} ref={scrollViewRef} onScroll={handleScroll} scrollEventThrottle={16}>
        <div ref={osmContainerRef} style={styles.osmContainer}></div> 
        <Text style={styles.text}>
          <Icon name="music" size={20} color="#2C3E50" /> Reference to the SVG container for sheet music <Icon name="music" size={20} color="#2C3E50" />
        </Text>
    </ScrollView>
    </>

  );
}

// Define styles for the components using StyleSheet
const styles = StyleSheet.create({
  scrollContainer: {
    width: "100%", // Make the scroll container fill the width of the parent
    height: "100%", // Set a specific height for scrolling (adjust as needed)
    overflow: "scroll", // Enable vertical scrolling
    borderWidth: 1, // Add border to the container
    borderColor: "black", // Set border color to black
  },
  osmContainer: {
    width: "100%", // Make the sheet music container fill the width of the parent
    borderWidth: 1, // Add border to the sheet music container
    borderColor: "black", // Set border color to black
    overflow: "hidden", // Ensure content doesn't overflow outside this container
  },
  text: {
    fontSize: 20,
    textAlign: "center",
    color: "#2C3E50"
  }
});
