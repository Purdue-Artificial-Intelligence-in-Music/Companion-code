import {fetchData} from './Api';
import { View, Text, Button } from 'react-native';
import Slider from '@react-native-community/slider';
import { useState, useEffect } from 'react';
import { Audio } from 'expo-av'

export function AudioPlayer() {
    const [sample_rate, setSampleRate] = useState('')
    const [buffer, setBuffer] = useState()
    const [sound, setSound] = useState<Audio.Sound | null>(null);
    const [playbackRate, setPlaybackRate] = useState(1.0); // Default rate of 1x
    const [currentPosition, setCurrentPosition] = useState(0); // Playback position in seconds
    const [duration, setDuration] = useState(0); // Total audio duration in seconds
    useEffect(() => {
        let interval: NodeJS.Timeout;

        if (sound) {
            // Set up interval to track playback position
            interval = setInterval(async () => {
                const status = await sound.getStatusAsync();
                if (status.isLoaded) {
                    setCurrentPosition(status.positionMillis / 1000); // Convert to seconds
                    setDuration((status.durationMillis ?? 0)/ 1000); // Convert to seconds
                }
            }, 1000); // Update every second
        }

        return () => clearInterval(interval); // Clean up on component unmount
    }, [sound]);

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
  
  const startAudio = async() => {
      if (sound) {
          await sound.playAsync();
      }
  }
  const stopAudio = async () => {
      if (sound) {
          await sound.pauseAsync();
      }
  };
  

  const updatePlaybackRate = async (rate : number) => {
    setPlaybackRate(rate);
    if (sound) {
        await sound.setRateAsync(rate, true); // Update playback speed
    }
  };
  return (
        <View>

            <Button title="Get and play Audio" onPress={fetchAndPlay} />
            <Button title="Resume Audio" onPress={startAudio} />
            <Button title="Pause Audio" onPress={stopAudio} />

            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 20 }}>
                <Text>0.1x</Text>
                <Text>Current rate: {playbackRate.toFixed(2)}x</Text>
                <Text>5.0x</Text>
            </View>
            <Slider
                minimumValue={0.1}
                maximumValue={5.0}
                step={0.1}
                value={playbackRate}
                onValueChange={updatePlaybackRate}
                minimumTrackTintColor="#1EB1FC"
                maximumTrackTintColor="#1EB1FC"
                thumbTintColor="#1EB1FC"
            />
            <Text style={{ marginTop: 10 }}>
                Position: {currentPosition.toFixed(1)}s / {duration.toFixed(1)}s
            </Text>
            <Text style={{ marginTop: 10 }}>Audio Status: {sound ? 'Audio Loaded' : 'Audio Unavailable'}</Text>
        </View>
      

  );
}