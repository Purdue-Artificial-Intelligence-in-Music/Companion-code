from flask import Flask, request, jsonify
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

if __name__ == "__main__":
    app.run(debug=True)