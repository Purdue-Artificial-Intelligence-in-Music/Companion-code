from flask import Flask, request, jsonify
from flask_cors import CORS
import librosa
import io
import base64
import soundfile as sf
import music21

app = Flask(__name__)
app.jinja_options = {}
CORS(app)

@app.route("/sendScore", methods=["GET"])
def sendScore():
    s1 = music21.stream.Stream()
    c_scale = ["C4","D4", "E4", "F4", "G4", "A5", "B5"]
    for note in c_scale:
        s1.append(music21.note.Note(note, type="quarter"))
    musicxml = music21.musicxml.m21ToXml.GeneralObjectExporter(s1)
    musicxml_str = musicxml.parse().decode('utf-8')
    return musicxml_str

@app.route("/")
def hello():
    print(request)
    return "<h1>Hello World!</h1>"

@app.route('/sendWaveform', methods=["POST", "GET"])
def sendWaveform():
    print(request.get_json())
    return 'OK'


@app.route('/getData', methods=["POST", "GET"])
def getData():
    data = {
        "info" : "Information1",
        "info2" : "Information2"
    }
    return jsonify(data)

@app.route('/squareInt', methods=["POST"])
def squareInt():
    input = request.get_json()
    value = input['number']
    def check_int(s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()
    if check_int(value):
        data = {'output': int(value) ** 2}
    else:
        data = {'output': 'Not an integer'}
    return data

@app.route('/audioBuffer', methods=["POST", "GET"])
def audioBuffer():
    filename = "data\\audio\\air_on_the_g_string\\synthesized\\solo.wav"
    y, sr = librosa.load(filename)
    
    buffer_io = io.BytesIO()
    sf.write(buffer_io, y, sr, format='WAV')
    buffer_io.seek(0)
    
    #need to return the audio buffer in base64 format for compatability with native audio players
    audio_base64 = base64.b64encode(buffer_io.read()).decode('utf-8')
    #NOTE: We will need to constantly encode stuff. Need to figure this out (maybe encode in frontend?)
    
    data = {
        "buffer" : audio_base64,
        "sr" : sr
    }
    return jsonify(data)

if __name__ == "__main__":
    print(sendScore())
    app.run(debug=True)