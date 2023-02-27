from flask import Flask, send_from_directory, request
import random

app = Flask(__name__)

@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')

@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)

@app.route("/rand")
def hello():
    return str(random.randint(0,100))

@app.route('/message')
def generate_random():
    args = request.args
    print(args['name'])
    return "Hello " + args['name']

if __name__ == "__main__":
    app.run(debug=True)

