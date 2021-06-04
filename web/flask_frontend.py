from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

@app.route("/", methods=['post', 'get'])
def index():
    if request.method == 'POST':
        x = str(request.form.get('x'))  # запрос к данным формы
        a = requests.get('http://api:5000/?x={}'.format(x))
    #try:
    #    dictin = requests.get('http://api:5000/dict')
    #    di = dictin.json()
    #except:
    #    di = {}
    #return render_template('index.html', variable3=di)
    return render_template('index.html')