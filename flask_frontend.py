from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

@app.route("/", methods=['post', 'get'])
def index():
    x = 0
    if request.method == 'POST':
	    x = str(request.form.get('x'))  # запрос к данным формы
    try:
        a = requests.get('http://api:5000/?x={}'.format(x))
        result = int(a.content)
        return render_template('index.html', variable=result)
    except:
        pass