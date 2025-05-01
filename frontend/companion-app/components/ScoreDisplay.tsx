import { NativeScrollEvent, NativeSyntheticEvent, ScrollView, StyleSheet, Text, TouchableOpacity, View, TextInput, Platform, useWindowDimensions} from "react-native";
import { useRef, useEffect, useState} from "react";
import { Cursor, OpenSheetMusicDisplay, Fraction, SourceMeasure } from "opensheetmusicdisplay";
import Icon from "react-native-vector-icons/FontAwesome";
import scoresData from "../musicxml/scores"; // Local mapping of score filenames to XML content
import { WebView } from "react-native-webview";

export default function ScoreDisplay({
  state,
  dispatch,
}: {
  state: any;
  dispatch: any;
}) {
  
  // Web-only refs
  const osmContainerRef = useRef<HTMLDivElement | null>(null); // Reference for the SVG container
  // Create refs to the cursor and to the OSDiv
  const cursorRef = useRef<Cursor | null>(null);
  const osdRef = useRef<OpenSheetMusicDisplay | null>(null);

  // Native-only ref (Used to inject html code into since OSMD is only supported through browser)
  const webviewRef = useRef<WebView>(null);

  const scrollViewRef = useRef<ScrollView>(null); // reference to scroll view component
  const scrollPositionRef = useRef<number>(0); // ref to keep track of current y position of scroll view (used ref instead of state to prevent rerender when scroll)
  const [steps, setSteps] = useState<string>(""); // state for declaring number of intended cursor iterations
  const [speed, setSpeed] = useState<string>(""); // state for speed of cursor update

  const moveCursorByBeats = () => {

     // Mobile approach
    if (Platform.OS !== "web") {

      // Check to make sure WebView component exists to continue 
      if (!webviewRef.current) {
        console.error("WebView not initialized.");
        return;
      }

      // Build one injected script that:
      // 1. Grabs time‐sig denominator (Assumption: Only dealing with pieces with a fixed time signature)
      // 2. Accumulates beats under the cursor (first instrument only)
      // 3. Recursively steps until totalBeats reached or passed 
      // This script is essentially the same movement logic on the web version 

      const script = `
        (function() {
          const osd = window.osm;
          const cursor = window.cursor;
          if (!osd.IsReadyToRender()) {
            console.warn("Please call osmd.load() and osmd.render() before stepping the cursor.");
            return;
          }
          // get denom of first measure
          const measures = osd.GraphicSheet.MeasureList;
          if (!measures.length || !measures[0].length) {
            console.warn("No measures found after render().");
            return;
          }
          const denom = measures[0][0].parentSourceMeasure.ActiveTimeSignature.denominator;
          // initial beats under cursor
          let accumulated = -1;
          const topPart = osd.Sheet.Instruments[0];
          const initVoices = cursor.VoicesUnderCursor(topPart);
          if (initVoices.length && initVoices[0].Notes.length) {
            const len = initVoices[0].Notes[0].Length;
            accumulated += (len.Numerator / len.Denominator) * denom;
          }
          // recursive step
          function stepFn() {
            if (accumulated >= ${parseInt(steps)}) {
              osd.render();
              return;
            }
            cursor.next();
            const voices = cursor.VoicesUnderCursor(topPart);
            if (!voices.length || !voices[0].Notes.length) {
              console.warn("Ran out of entries before hitting target beats.");
              //osd.render();
              //return;
            } else {
              const nextLen = voices[0].Notes[0].Length;
              accumulated += (nextLen.Numerator / nextLen.Denominator) * denom;
             }
            osd.render();
            setTimeout(stepFn, ${parseInt(speed)});
          }
          stepFn();
        })();
        true;
      `;
      webviewRef.current.injectJavaScript(script);
      return;
    }


    // Web Approach to moving cursor by beats

    // Ensure OSMD is loaded and rendered
    if (!osdRef.current!.IsReadyToRender()) {
      console.warn("Please call osmd.load() and osmd.render() before stepping the cursor.");
      return;
    }

    // Grab all measure’s time signature 
    const measures = osdRef.current!.GraphicSheet.MeasureList;
    if (!measures.length || !measures[0].length) {
      console.warn("No measures found after render()."); // error handling when no measures are found
      return;
    }
    
    // This first part is accounting for the note that the cursor is hovering on load 

    // Take the first measure's time signature denominator (e.g. 4 in “4/4”)
    const denom = measures[0][0].parentSourceMeasure.ActiveTimeSignature!.denominator;
  
    // Compute the starting accumulated beats under the cursor
    let accumulated = -1; // Represents the total number of beats the cursor has gone through (-1 so it is 0 indexed)

    // Focus on only the voice entries of the first instrument
    const topPart = osdRef.current!.Sheet.Instruments[0];
    const initial = osdRef.current!.cursor.VoicesUnderCursor(topPart);
    
    // Only proceed if there’s at least one voice and that voice has at least one note
    if (initial.length && initial[0].Notes.length) {
      
      // Find the value of current note. e.g. 1/4 = Quarter Note 
      const len = initial[0].Notes[0].Length as Fraction;

      // Multiply fraction value of current note by denominator of time signature to get how much beat this current note is worth
      // The add to cumulative number of beats the cursor as went over so far
      accumulated += (len.Numerator / len.Denominator) * denom;
    }

    // Make sure Y position is always 0 when starting the cursor 
    let scrollPosition = 0;
  
    // Recursive step function used to
    function stepFn() {
      
      // Stop when we've reached (or exceeded) target beats
      if (accumulated >= parseInt(steps)) {
        osdRef.current!.render(); // final render to show final cursor position
        return; 
      }
      cursorRef.current!.next(); // Advance cursor one note 
      
      // Get voice entries of new position of cursor (only focused on first instrument) 
      const voice = cursorRef.current!.VoicesUnderCursor(topPart);

      if (!voice.length || !voice[0].Notes.length) { // If no notes for first instrument, continue to next note
        console.log("skip due to empty notes")

      } else { // Case if there is a note, we get it's value in beats and add to our cumulative beats
        const len = voice[0].Notes[0].Length as Fraction; 
        accumulated += (len.Numerator / len.Denominator) * denom; // Find how many beats that note is worth based on denominator of time signature
      }

      osdRef.current!.render(); // Re-render to show the moved cursor
      scrollUp(scrollPosition); // Scroll to saved position after rerendering the OSM container
      setTimeout(stepFn, parseInt(speed)); // Schedule the next step after a delay (speed state decides how fast cursor should update)
    }
    // Start the cursor movement logic
    stepFn();
  }
  

  // Build HTML for native WebView, exposing window.osm & window.cursor for moving cursor logic for mobile when injecting the js script above
  const buildHtml = (xml: string) => {
    const escaped = xml
      // Escape every backtick so that embedding this string in a JS template literal
      // won’t accidentally terminate the literal early.
      .replace(/`/g, "\\`")
      // Escape every closing </script> tag so that, when injected into our <script> block,
      // it can’t break out of that block and end our script prematurely.
      .replace(/<\/script>/g, "<\\/script>"); 
      return `<!DOCTYPE html>
                <html>
                  <head>
                  <meta name="viewport" content="width=device-width, initial-scale=1.0">
                  </head>
                  <body>
                    <div id="osmd-container"></div>
                    <script src="https://unpkg.com/opensheetmusicdisplay@latest/build/opensheetmusicdisplay.min.js"></script>
                    <script>
                      (async () => {
                        const osm = new opensheetmusicdisplay.OpenSheetMusicDisplay(
                          document.getElementById('osmd-container'),
                          { autoResize: true, followCursor: true }
                        );
                        try {
                          await osm.load(\`${escaped}\`);
                          osm.render();
                          // expose for RN->WebView injection
                          window.osm = osm;
                          window.osm.zoom = .45;
                          window.cursor = osm.cursor;
                          window.cursor.show();
                          window.cursor.CursorOptions = {
                            ...window.cursor.CursorOptions,
                            follow: true
                          };
                          window.ReactNativeWebView.postMessage(JSON.stringify({
                            type: 'loaded',
                            time_signature: window.cursor.Iterator.CurrentMeasure.ActiveTimeSignature,
                            tempo: 100
                          }));
                        } catch (err) {
                          console.error(err);
                        }
                      })();
                    </script>
                  </body>
                </html>`;
  };

  // Web-only initialization
  useEffect(() => {
    if (Platform.OS === "web" && osmContainerRef.current && state.score) {
      // Remove any previously-loaded music
      if (osmContainerRef.current) {
        while (osmContainerRef.current.children[0]) {
          osmContainerRef.current.removeChild(
            osmContainerRef.current.children[0],
          );
        }
      }

      // Create an instance of OpenSheetMusicDisplay, passing the reference to the container
      const osm = new OpenSheetMusicDisplay(osmContainerRef.current as HTMLElement, {
        autoResize: true , // Enable automatic resizing of the sheet music display
        followCursor: true, // And follow the cursor

      });
      osdRef.current = osm; 
      // If score name is a key within ScoreContents use the xml content value within that key, otherwise access xml content through the static key value mapping defined within scores.ts
      const xmlContent = (state.scoreContents && state.scoreContents[state.score]) || scoresData[state.score];

      // Error handling if no xml content for selected score is found
      if (!xmlContent) {
        console.error("Score content not found for:", state.score);
        return;
      }

      // Load and render the XML content.
      osm
        .load(xmlContent)
        .then(() => {
          // Render the sheet music
          osm.render();
          cursorRef.current = osm.cursor;
          cursorRef.current.show(); // Ensure the cursor is visible
          cursorRef.current.CursorOptions = {
            ...cursorRef.current.CursorOptions,
            follow: true,
          };
          //osdRef.current!.zoom = .45

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
    } // Dependency array means this effect runs once when the component mounts and again when a new score is selected
  }, [dispatch, state.score, state.scores])

// Define the handler to catch messages sent from the WebView back to React Native
const onMessage = (event: any) => {
  try {
    // Extract the message string sent via window.ReactNativeWebView.postMessage(...)
    const data = JSON.parse(event.nativeEvent.data);

    // We expect a message of type 'loaded' sent after OSMD has finished rendering
    if (data.type === 'loaded') {
      dispatch({
        type: 'update_piece_info',
        time_signature: data.time_signature,
        tempo: data.tempo,
      });
    }
  } catch (e) {
    // Catch and log any errors during message parsing or if expected fields are missing
    console.error('Failed to parse WebView message', e);
  }
};

  const selectedXml = (state.scoreContents && state.scoreContents[state.score]) || scoresData[state.score] || "";

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
//   useEffect(() => {
//     let ct = state.cursorTimestamp; // current timestamp of cursor's note(s) in seconds
//     var dt = new Fraction();
//     console.log("ct:", ct);
//     if (cursorRef.current?.Iterator.CurrentSourceTimestamp !== undefined) {
//       var ts_meas = Fraction.createFromFraction(
//         cursorRef.current?.Iterator.CurrentSourceTimestamp,
//       ); // current timestamp of iterator as a fraction
//       console.log("ts_meas:", ts_meas.RealValue);
//       if (ct > state.timestamp) {
//         // If timestamp is older, go back to beginning, b/c probably reset
//         console.log("Moving ct back to beginning.");
//         ct = 0;
//         cursorRef.current?.reset();
//         ts_meas = new Fraction();
//       }

//       // while timestamp is less than desired, update it
//       while (ct <= state.timestamp) {
//         cursorRef.current?.Iterator.moveToNextVisibleVoiceEntry(false);
//         dt = Fraction.minus(
//           cursorRef.current?.Iterator.CurrentSourceTimestamp,
//           ts_meas,
//         );
//         // dt is a fraction indicating how much - in whole notes - the iterator moved

//         ct +=
//           (60 * dt.RealValue * state.time_signature.Denominator) /
//           state.synth_tempo;
//         console.log("ct:", ct);
//         ts_meas = Fraction.plus(ts_meas, dt);
//       }
//       cursorRef.current?.Iterator.moveToPreviousVisibleVoiceEntry(false);
//       console.log("Cursor should be updating");
//       cursorRef.current?.update();
//       dispatch({
//         type: "cursor_update",
//         time:
//           (60 *
//             cursorRef.current?.Iterator.CurrentSourceTimestamp.RealValue *
//             state.time_signature.Denominator) /
//           state.synth_tempo,
//       });
//     }
//   },
// [state.timestamp]);

  return (
    <>
      {/* Temporary inputs for testing cursor movement */}
      <TextInput
        value={steps}
        onChangeText={setSteps}
        keyboardType="numeric"
        placeholder="Number Of Steps"
      />
      <TextInput
        value={speed}
        onChangeText={setSpeed}
        keyboardType="numeric"
        placeholder="Cursor Update Speed (ms)"
      />

      <TouchableOpacity 
      onPress={moveCursorByBeats}
      >
        <Text>Start</Text>
      </TouchableOpacity>

      {/* Reference ScrollView Component for controlling scroll */}
      <ScrollView
        style={styles.scrollContainer}
        contentContainerStyle={{ flexGrow: 1 }}
        showsVerticalScrollIndicator
        ref={scrollViewRef}
        onScroll={handleScroll}
        scrollEventThrottle={16}
      >
        {/* If on web, render the OSMD container like normal */}
        {Platform.OS === "web" ? (
          <div ref={osmContainerRef} style={styles.osmContainer} />
        ) : (

          // Otherwise use WebView component to render OSMD since it only has web base support so injecting html is the only way
          <WebView
            ref={webviewRef}
            originWhitelist={["*"]}
            source={{ html: buildHtml(selectedXml) }}
            onMessage={onMessage} // Call function when page inside this Webview calls postMessage
            style={{ backgroundColor: "transparent", height: 400 }}
          />
        )}

        <Text style={styles.text}>
          <Icon name="music" size={20} color="#2C3E50" /> Reference to the SVG
          container for sheet music{" "}
          <Icon name="music" size={20} color="#2C3E50" />
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
