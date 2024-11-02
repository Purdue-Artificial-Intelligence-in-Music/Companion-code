import { useState, useRef } from "react";

const mimeType = "audio/webm";

const AudioRecorder = () => {
    const [permission, setPermission] = useState(false);
    const mediaRecorder = useRef(null);
    const [recordingStatus, setRecordingStatus] = useState("inactive");
    const [stream, setStream] = useState(null);
    const [audioChunks, setAudioChunks] = useState([]);
    const [audio, setAudio] = useState(null);
    const [analyserData, setAnalyserData] = useState([]);
    const audioContext = new AudioContext();
    const recordingStatusRef = useRef("inactive");

    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const dataArrayRef = useRef(null);
    const startTimeRef = useRef(null);

    const startRecording = async () => {
        setRecordingStatus("recording");
        recordingStatusRef.current = "recording";
        startTimeRef.current = Date.now();
        //create new Media recorder instance using the stream
        const media = new MediaRecorder(stream, { type: mimeType });
        //set the MediaRecorder instance to the mediaRecorder ref
        mediaRecorder.current = media;
        //invokes the start method to start the recording process
        mediaRecorder.current.start();
        let localAudioChunks = [];
        mediaRecorder.current.ondataavailable = (event) => {
           if (typeof event.data === "undefined") return;
           if (event.data.size === 0) return;
           localAudioChunks.push(event.data);
        };
        setAudioChunks(localAudioChunks);

        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContextRef.current.createMediaStreamSource(stream);
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 2048;
        source.connect(analyserRef.current);
        
        const bufferLength = analyserRef.current.frequencyBinCount;
        dataArrayRef.current = new Uint8Array(bufferLength);

        // Analyze frequency data continuously
        const getFrequencyData = () => {  
            if (recordingStatusRef.current === "recording") {
                analyserRef.current.getByteTimeDomainData(dataArrayRef.current);
                const timestamp = Date.now() - startTimeRef.current;
                const waveForm = Array.from(dataArrayRef.current);
                sendWaveformData({timestamp, waveForm});
                setAnalyserData([...dataArrayRef.current]);
                requestAnimationFrame(getFrequencyData); 
            }
        };
    
        getFrequencyData();

      };
    
    const sendWaveformData = async (data) => {
        try {
            const options = {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            };
            console.log(JSON.stringify(data));
            const res = await fetch("http://127.0.0.1:5000/sendWaveform", options);

        }
        catch (error) {
            console.error("Error occurred: ", error);
        }
    }

    const stopRecording = () => {
        setRecordingStatus("inactive");
        recordingStatusRef.current = "inactive";
        //stops the recording instance
        mediaRecorder.current.stop();
        mediaRecorder.current.onstop = () => {
          //creates a blob file from the audiochunks data
           const audioBlob = new Blob(audioChunks, { type: mimeType });
          //creates a playable URL from the blob file.
           const audioUrl = URL.createObjectURL(audioBlob);
           setAudio(audioUrl);
           setAudioChunks([]);
           audioContextRef.current.close();
           
        };
    };
    const getMicrophonePermission = async () => {
        if ("MediaRecorder" in window) {
            try {
                const streamData = await navigator.mediaDevices.getUserMedia({
                    audio: true,
                    video: false,
                });
                setPermission(true);
                setStream(streamData);
            } catch (err) {
                alert(err.message);
            }
        } else {
            alert("The MediaRecorder API is not supported in your browser.");
        }
    };
    
    return (
        <div className="audio-controls">
            <h1>Audio Recorder</h1>
            {!permission ? (
            <button onClick={getMicrophonePermission} type="button">
                Get Microphone
            </button>
            ) : null}
            {permission && recordingStatus === "inactive" ? (
            <button onClick={startRecording} type="button">
                Start Recording
            </button>
            ) : null}
            {recordingStatus === "recording" ? (
            <button onClick={stopRecording} type="button">
                Stop Recording
            </button>
            ) : null}
            {audio ? (
            <div className="audio-container">
                <audio src={audio} controls></audio>
                <a download href={audio}>
                    Download Recording
                </a>
            </div>
            ) : null}
        </div>
    );
};
export default AudioRecorder;