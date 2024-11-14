import { StyleSheet } from "react-native";
import { useRef, useEffect } from "react";
import { Cursor, OpenSheetMusicDisplay, Fraction } from "opensheetmusicdisplay";

export default function ScoreDisplay( { state, dispatch }:
    { state: any, dispatch: any }
) {
    // Create a reference to the SVG container where sheet music will be rendered
    const osmContainerRef = useRef<HTMLDivElement | null>(null); // Reference for the SVG container
    // Create refs to the cursor and to the OSDiv
    const cursorRef = useRef<Cursor | null>(null);
    const osdRef = useRef<OpenSheetMusicDisplay | null>(null);

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

    if (state.score) {
      const selectedScore = state.scores.find((s: {filename: string}) => s.filename === state.score);
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
          .load("assets/" + state.score)
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
            // TODO!  Find the piece's tempo and send that instead of constant 100
            dispatch({type:'update_piece_info', time_signature:cursorRef.current.Iterator.CurrentMeasure.ActiveTimeSignature, tempo: 100});
          })
          .catch((error) => {
            // Handle errors in loading the music XML file
            console.error("Error loading music XML:", error); // Log the error message
          });
      }
    }

    // Cleanup function to dispose of the OpenSheetMusicDisplay instance if needed
    return () => {};
  }, [state.score]); // Dependency array means this effect runs once when the component mounts and again when a new score is selected

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
        ct += 60 * dt.RealValue * state.time_signature.Denominator / state.score_tempo;
        console.log("ct:",ct);
        // // either way, the calculation is:
        // 60 secs/min * dt wholes * time signature denominator (beats/whole) / BPM (beats/minute) yields seconds
        ts_meas = Fraction.plus(ts_meas, dt);
      }
      cursorRef.current?.Iterator.moveToPreviousVisibleVoiceEntry(false);
      console.log("Cursor should be updating");
      cursorRef.current?.update();
      dispatch( {type:'cursor_update', time:(60 * cursorRef.current?.Iterator.CurrentSourceTimestamp.RealValue * state.time_signature.Denominator / state.score_tempo)})
    }  
                
    // if (osdRef.current !== undefined && osdRef.current?.Sheet !== undefined) {
    //   console.log("Should be re-rendering.");
    //   osdRef.current.render();
    // } // COMMENTING THIS OUT FIXED IT AND I DON"T KNOW WHY!!!!! ❤️ Robert
  }, [state.timestamp])

    return (
        <div style={styles.scrollContainer}> {/* Container for scrolling the sheet music */}
            <div ref={osmContainerRef} style={styles.osmContainer}>
            </div> Reference to the SVG container for sheet music
        </div>
    )
}

// Define styles for the components using StyleSheet
const styles = StyleSheet.create({
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
    }
  });