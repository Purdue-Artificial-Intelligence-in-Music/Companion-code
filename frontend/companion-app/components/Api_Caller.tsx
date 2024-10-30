import {fetchData} from './Api';
import { View, Text, TextInput, Button, Pressable } from 'react-native';
import { useState } from 'react';
import { Audio } from 'expo-av'

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

    
    export function Play_Audio() {
        const [sample_rate, setSampleRate] = useState('')
        const [buffer, setBuffer] = useState()
        const [sound, setSound] = useState<Audio.Sound | null>(null);
        const fetchAndPlay = async () => {
        try {
            const data = await fetchData('http://localhost:5000/audioBuffer'); // Adjust URL as needed
            setSampleRate(data["sr"]); // Update state with the fetched data
            if (!data["buffer"]) {
                console.warn("No buffer!!");
                return;
            }

            const soundObject = new Audio.Sound();
            await soundObject.loadAsync({ uri: `data:audio/wav;base64,${data["buffer"]}` });

            // soundObject.setRateAsync(0.5, true);
            setSound(soundObject);
            
            const status = await soundObject.getStatusAsync();
            console.log(status)
            if (soundObject) {
                await soundObject.playAsync(); // Now it's safe to play
            } else {
                console.warn('Audio not loaded properly');
            }
            // await soundObject.playAsync();

        } catch (error) {
            // Handle error case
            console.log("error loading sound", error)
        }
    };
    

    const stopAudio = async () => {
        if (sound) {
            await sound.stopAsync();
        }
    };
    

    const setPlaybackRate = async (rate : number) => {
        if (sound) {
            await sound.setRateAsync(rate, true); // Update playback speed
        }
    };
    return (
        <View>

            <Button title="Get and play Audio" onPress={fetchAndPlay} />
            <Button title="Stop Audio" onPress={stopAudio} />
            <Button title="Normal Speed" onPress={() => setPlaybackRate(1.0)} />
            <Button title="Double Speed" onPress={() => setPlaybackRate(2.0)} />
            <Button title="Half Speed" onPress={() => setPlaybackRate(0.5)} />
            <Text> Audio found: {sound ? 'Audio loaded' : 'Audio unavailable'}</Text>
        </View>
        // <Pressable onPress={retrieveAndPlay}>
        // <Text> Output: {buffer ? JSON.stringify(buffer) : 'No output yet'}</Text>
        // </Pressable>

    );
}