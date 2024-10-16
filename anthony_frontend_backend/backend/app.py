from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
app.jinja_options = {}
CORS(app)


@app.route("/")
def hello():
    print(request)
    return "<h1>Hello World!</h1>"

@app.route('/sendWaveform', methods=["POST", "GET"])
def sendWaveform():
    print(request.get_json())
    return 'OK'

if __name__ == "__main__":
    app.run(debug=True)