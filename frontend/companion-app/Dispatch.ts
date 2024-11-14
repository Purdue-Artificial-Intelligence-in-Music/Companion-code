const reducer_function = (state: any, action: any) => {
    console.log("Dispatch received.");
    switch (action.type) {
        case 'reset':
        // When resetting, move the cursor, then adjust the timestamp accordingly and reset the playback rate
            console.log("It should be resetting now.")
            var reset_time = 60 * state.time_signature.Numerator * (state.resetMeasure - 1) / state.tempo;
            return {...state, ...{playing: false, playRate:1.0, timestamp:reset_time } }
        case 'start/stop':
            return {...state, ...{playing: !(state.playing)}}
        case 'increment':
            return {...state, ...{playRate: action.rate as number, timestamp: action.time as number} }
        case 'cursor_update':
            return {...state, ...{cursorTimestamp: action.time as number}}
        case 'change_reset':
            return {...state, ...{resetMeasure: action.measure as number}}
        case 'change_tempo':
            return {...state, ...{tempo: action.tempo as number}}
        case 'change_time_signature':
            return {...state, ...{time_signature: action.time_signature}}
        case 'new_session':
            return {...state, ...{sessionToken: action.token}}
        case 'new_audio':
            return {...state, ...{accompanimentSound: action.sound}}
        case 'change_score':
            console.log("Score is being changed")
            return {...state, ...{score: action.score, playing: false, timestamp: 0.0, playRate: 1.0 }}
        case 'new_scores_from_backend':
            var known_files = state.scores.map( (s: { filename: string }) => s.filename );
            var new_files = action.scores.filter( (filename: string) => !known_files.includes(filename) )
            return {...state, ...{scores: [...state.scores, new_files.map( (filename: string) => { return {
                filename: filename, piece: filename.replace(".musicxml", "")
            }})]}}
        case 'new_score_from_upload':
            return {...state, ...{scores: [...state.scores, action.score], score: action.score.filename}}
        default:
            return state;
    }
}

export default reducer_function;