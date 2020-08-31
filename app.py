from flask import Flask, request, render_template
import redis
from rq import Queue
from time import sleep

def fibo(x: int):
    if x == 0:
        return 0
    elif x == 1:
        return 1
    else:
        return fibo(x-1) + fibo(x-2)

app = Flask(__name__)
redis_server = redis.Redis("localhost")
q = Queue(connection=redis_server)

@app.route("/", methods=['post', 'get'])
def index():
    x = 0
    if request.method == 'POST':
	    x = int(request.form.get('x'))  # запрос к данным формы
    try:
        result = q.enqueue(fibo, x, result_ttl=60*60*24)
        sleep(5)
        return render_template('index.html', variable=result.result)
    except:
        pass
