from flask import Flask, request, Response
import redis
from rq import Queue
from rq.job import Job
from time import sleep
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import sys

def fibo(x: int):
    if x == 0:
        return 0
    elif x == 1:
        return 1
    else:
        return fibo(x-1) + fibo(x-2)

def get_env_variable(name):
    try:
        return os.getenv(name)
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")
REDIS_SERVER = get_env_variable("REDIS_SERVER")

app = Flask(__name__)
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
app.config['DEBUG'] = False

redis_conn = redis.Redis(host=REDIS_SERVER, port=6379)
q = Queue(connection=redis_conn)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class fibo_db(db.Model):
    __tablename__ = 'fibonacci'

    id = db.Column(db.Integer, primary_key=True)
    request = db.Column(db.Integer())
    result = db.Column(db.Integer())

    def __init__(self, request, result):
        self.request = request
        self.result = result

results_dict = {}
temp_dict = {}
di = {}

def get_from_cache(x):
    job_id = results_dict[int(x)]
    try:
        res_call = Job.fetch(f'{job_id}', connection=redis_conn)
        if res_call.result is not None:
            res = int(res_call.result)
            return res
    except:
        pass

def enqueue(x):
    result = q.enqueue(fibo, x, result_ttl=300)
    job_id = result.id
    res = 'Запрос помещен в очередь'
    temp_dict[x]=result.id
    results_dict.update(temp_dict)
    di[x] = res
    return res

@app.route("/", methods=['post', 'get'])
def send_fibo():
    try:
        x = int(request.args['x'])
        res = get_from_cache(x)
        if res is None:
            if results_dict[int(x)]:
                del results_dict[x]
            res = enqueue(x)
    except:
        res = enqueue(x)
    return str(res)

@app.route("/dict", methods=['post', 'get'])
def send_dict():
    for key in di:
        result = get_from_cache(key)
        if result is not None:
            di[key] = result
            exist = fibo_db.query.filter_by(request=key).first()
            if not exist:
                new_fibo = fibo_db(request=int(key),result=int(result))
                db.session.add(new_fibo)
                db.session.commit()
    return di

@app.route("/health", methods=['post', 'get'])
def send_health():
    status_code = Response(status=200)
    return status_code