import { Pressable } from "react-native";
import RNPickerSelect from "react-native-picker-select";
import { View, Text, TextInput, Button } from 'react-native';
import { OpenSheetMusicDisplay, Cursor } from 'opensheetmusicdisplay';
import { MutableRefObject, useState } from 'react';
import {fetchData} from './Api';


export function GET_Request() {
    const [output, setOutput] = useState('')

    const handlePress = async () => {
        try {
          const data = await fetchData('http://localhost:5000/getData'); // Adjust URL as needed
          setOutput(data); // Update state with the fetched data
        } catch (error) {
          setOutput('Error fetching data'); // Handle error case
        }
    };
    return <Pressable onPress={handlePress}>
        <Text> Output: {output ? JSON.stringify(output) : 'No output yet'}</Text>
        </Pressable>
}

export function POST_Request() {
    const [inputText, setInputText] = useState(''); 
    const [response, setResponse] = useState(''); 
  
    const handlePostRequest = async () => {
      try {
        const response = await fetch('http://localhost:5000/squareInt', { 
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ number: inputText }), // Send the user input in the body
        });
  
        const data = await response.json();
        setResponse(`Response from server: ${JSON.stringify(data)}`);
      } catch (error) {
        console.error('Error making POST request:', error);
        setResponse('Error making POST request');
      }
    };
  
    return (
      <View>
        <Text>Enter some text:</Text>
        <TextInput
          value={inputText}
          onChangeText={text => setInputText(text)} // Update state with input value
          placeholder="Enter your text here"
          style={{ borderColor: 'gray', borderWidth: 1, marginBottom: 10, padding: 5 }} // For styling
        />
        <Button
          title="Submit"
          onPress={handlePostRequest}
        />
        <Text>{response}</Text> {/* Display the response */}
      </View>
    );
  }

export function Score_Select( {score, scoreOptions, setScore}:
    { score: string, scoreOptions: Array<{ filename: string, piece: string}>, setScore: Function }
) {
    const my_options = scoreOptions.map( (score) => { return { label: score["piece"], value: score["filename"]}})
    return <div>
        <Text>Choose a piece:</Text>
        <RNPickerSelect value={score} items={my_options} onValueChange={(value) => setScore(value)}/>
    </div>
}

export function Play_Button( { my_cursor, playing, setPlaying } : 
    { my_cursor: MutableRefObject<Cursor | null>, playing: boolean, setPlaying: Function } ) {
    
        // If the function below is uncommented - even if it isn't called - the cursor doesn't appear
    // const move_function = () => {
    //     if (my_cursor.current) {
    //         my_cursor.current?.next()
    //         const bpm = my_cursor.current?.Iterator.CurrentBpm ? my_cursor.current?.Iterator.CurrentBpm : 100
    //         const note_dur = my_cursor.current?.NotesUnderCursor().map( note => note.Length ).reduce( (prev, cur) => (prev < cur ? prev : cur));
    //         const time = 60000 / bpm * note_dur.RealValue
    //         console.log("Moving time: ", time)
    //         setTimeout(move_function, time)
    //     }
    // }

    return <Pressable onPress={ () => {
        console.log("The play button's on_press runs.");
        if (my_cursor.current) {
            console.log("And it has a valid ref");
            my_cursor.current.reset();
            my_cursor.current.show();
            setPlaying(true);
            // const bpm = my_cursor.current?.Iterator.CurrentBpm ? my_cursor.current?.Iterator.CurrentBpm : 100
            // const note_dur = my_cursor.current?.NotesUnderCursor().map( note => note.Length ).reduce( (prev, cur) => (prev < cur ? prev : cur));
            // const time = 60000 / bpm * note_dur.RealValue
            // setTimeout(move_function, time)
        }
    }}><Text>PLAY</Text></Pressable>
}

export function Next_Button( { my_cursor } : 
    { my_cursor: MutableRefObject<Cursor | null> } ) {
    return <Pressable onPress={ () => {
        console.log("The NEXT button's on_press runs.");
        if (my_cursor.current) {
            console.log("And it has a valid ref");
            my_cursor.current.Iterator.CurrentVoiceEntries[0].Notes[0].NoteheadColor = "#22ee55";
            my_cursor.current.next();
        }
    }}><Text>NEXT</Text></Pressable>
}

export function RenderSomethingButton( { osdRef } : { osdRef: MutableRefObject<OpenSheetMusicDisplay | null>}) {
    return(<Pressable onPress={ () => {
        osdRef.current?.setOptions( { autoResize: true });
        console.log("The RENDER SOMETHING button was pressed");
    }}>
        <Text>RENDER SOMETHING!!!</Text>
    </Pressable>)
}