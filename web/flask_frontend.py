from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

requests_array = []
di = {}
@app.route("/", methods=['post', 'get'])
def index():
    if request.method == 'POST':
	    x = str(request.form.get('x'))  # запрос к данным формы
    try:
        requests_array.append(x)
        requests_array_str = ' '.join(requests_array)
        a = requests.get('http://api:5000/?x={}'.format(x))
        result = int(a.content)
        di[x] = result
        return render_template('index.html', variable=result, variable2=requests_array_str, variable3=di)
    except:
        result = 0
        return render_template('index.html', variable=result, variable3=di)