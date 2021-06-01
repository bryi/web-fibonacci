from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

@app.route("/", methods=['post', 'get'])
def index():
    if request.method == 'POST':
	    x = str(request.form.get('x'))  # запрос к данным формы
    try:
        a = requests.get('http://api:5000/?x={}'.format(x))
        dictin = requests.get('http://api:5000/dict')
        result = int(a.content)
        di = dictin.json()

    except:
        result = 0
        di = {}
    return render_template('index.html', variable=result, variable3=di)