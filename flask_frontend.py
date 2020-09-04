from flask import Flask, request, render_template
from dotenv import load_dotenv
import requests
import os
load_dotenv()

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

app = Flask(__name__)
FLASK_API_PORT = get_env_variable("FLASK_API_PORT")

@app.route("/", methods=['post', 'get'])
def index():
    x = 0
    if request.method == 'POST':
	    x = int(request.form.get('x'))  # запрос к данным формы
    try:
        result = int(requests.get('localhost:{}/?x={}'.format(FLASK_API_PORT, x)))
        return render_template('index.html', variable=str(result))
    except:
        pass