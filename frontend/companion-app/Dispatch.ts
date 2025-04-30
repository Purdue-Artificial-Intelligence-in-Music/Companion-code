import MidiPerformance, { changeScorePosition, togglePerformance } from "./components/MidiPerformance"; // Import the function to change score position

const reducer_function = (state: any, action: any) => {
  console.log("Dispatch received.");
  // Conventions vary, but this one is rather common - the action argument
  // should be an object with the type property; this determines what type
  // of action to carry out on the state.  The action can have other properties;
  // for example, some value to which some property of the state is to be changed

  // Note that these functions only affect the state - things like the visible cursor
  // position and playback rate of the audio must be made to depend on the state
  // (likely with useEffect) in order to work.
  switch (action.type) {
    // Example of dispatch call with no special parameters:
    // this object-join notation causes state to only change in one property, playing,
    // which becomes the opposite of what it was before.
    case "start/stop":
      if (state.midiPerformance.current) {
        togglePerformance(state.midiPerformance.current);
      }
      return { ...state, ...{ playing: !state.playing } };

    // Example of dispatch call with special parameter:
    // dispatch( {type:'change_reset', measure:'3'}) will leave
    // state unchanged except for the resetMeasure property, which becomes 3
    case "change_reset":
      return { ...state, ...{ resetMeasure: action.measure as number } };

    // Multiple properties can be updated in tandem, as the playrate and position
    // would be in every syncrhonization request
    case "increment":
      return {
        ...state,
        ...{
          playRate: action.rate as number,
          timestamp: action.time as number,
        },
      };
    
    case "swap_mode":
      return {
        ...state,
        ...{
          inPlayMode: !state.inPlayMode
        }
      }

    // When resetting, move the cursor, then adjust the timestamp accordingly and reset the playback rate
    case "reset":
      console.log("It should be resetting now.");
      var reset_time =
        (60 * state.time_signature.Numerator * (state.resetMeasure - 1)) /
        state.synth_tempo;
      state.accompanimentSound.setPositionAsync(reset_time * 1000);
      return {
        ...state,
        ...{ playing: false, playRate: 1.0, timestamp: reset_time },
      };
    case "cursor_update":
      return { ...state, ...{ cursorTimestamp: action.time as number } };
    case "change_tempo":
      return { ...state, ...{ tempo: action.tempo as number } };
    case "update_piece_info":
      return {
        ...state,
        ...{
          time_signature: action.time_signature,
          score_tempo: action.tempo as number,
          tempo: action.tempo as number,
        },
      };
    case "new_session":
      console.log("New session token received.");
      return { ...state, ...{ sessionToken: action.token } };
    case "new_audio":
      console.log("New audio received.");
      return {
        ...state,
        ...{ accompanimentSound: action.sound, synth_tempo: state.tempo },
      };

    // Here, it's decided that the mechanism to change the score also resets the play
    case "change_score":
      return {
        ...state,
        ...{
          score: action.score,
          playing: false,
          timestamp: 0.0,
          playRate: 1.0,
        },
      };

    // Gets list of scores - without overwriting uploaded score
    case "new_scores_from_backend":
      var known_files = state.scores;
      var new_files = action.scores.filter(
        (filename: string) => !known_files.includes(filename),
      );
      console.log("New files are: ", new_files);
      return {
        ...state,
        ...{
          scores: [...state.scores, ...new_files],
        },
      };

    case "new_score_from_upload":
      return {
        ...state, // Keep the existing state
        scores: [...state.scores, action.score.filename], // Add the new score filename to the scores array
        score: action.score.filename, // Set the current score to the newly uploaded filename
        scoreContents: { 
          ...state.scoreContents, // Keep existing score content
          [action.score.filename]: action.score.content, // Add the new score content to the scoreContents object using the filename as the key
        },
      };
      
    case "update_timestamp":
      const newTimeBeat = (action.timestamp as number) / (60 / state.tempo);
      changeScorePosition(state.midiPerformance.current, newTimeBeat);
      // state.midiPerformance.current.updateScorePosition(action.timestamp as number);
      return { ...state, ...{ timestamp: action.timestamp as number } };
        
    default: // If no valid type, return state, otherwise the function returns null and the state is gone.
      return state;
  }
};

export default reducer_function;
