from flask import Flask, request, Response, make_response
import redis
from rq import Queue
from rq.job import Job
from time import sleep
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import sys
from flask_cors import CORS

def fibo(x: int):
    if x == 0:
        return 0
    elif x == 1:
        return 1
    else:
        return fibo(x-1) + fibo(x-2)

def calc_and_write_to_db(x):
    result = q.enqueue(fibo, int(x), result_ttl=5)
    while True:
        if result.result is not None:
            exist = fibo_db.query.filter_by(request=int(x)).first()
            if exist is not None:
                exist.result = int(result.result)
                db.session.commit()
            else:
                new_fibo = fibo_db(request=int(x),result=int(result.result), job_id=str(result.id))
                db.session.add(new_fibo)
                db.session.commit()
            break
    return int(result.result)

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
CORS(app)
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
app.config['DEBUG'] = False

redis_conn = redis.Redis(host=REDIS_SERVER, port=6379)
q = Queue(connection=redis_conn, default_timeout=3600)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class fibo_db(db.Model):
    __tablename__ = 'fibonacci'

    id = db.Column(db.Integer, primary_key=True)
    request = db.Column(db.Integer())
    result = db.Column(db.Text())
    job_id = db.Column(db.String())

    def __init__(self, request, result, job_id):
        self.request = request
        self.result = result
        self.job_id = job_id

di = {}

def get_from_cache(x):
    if x == 0:
        res = 0
        di[x] = res
    elif x == 1:
        res = 1
        di[x] = res
    else:
        exist = fibo_db.query.filter_by(request=int(x)).first()
        if exist:
            job_id = exist.job_id
            try:
                res_call = Job.fetch(f'{job_id}', connection=redis_conn)
                if res_call.result is not None:
                    res = int(res_call.result)
                elif res_call.result is None and res_call.id == job_id:
                    res = 'Запрос находится в обработке'
            except:
                if exist.result == 'Запрос помещен в очередь':
                    db.session.delete(exist)
                    db.session.commit()
                    res = None
                else:
                    res = exist.result
        else:
            res = None
    return res

def enqueue(x):
    result = q.enqueue(calc_and_write_to_db, x, result_ttl=60)
    job_id = result.id
    res = 'Запрос помещен в очередь'
    exist = fibo_db.query.filter_by(request=int(x)).first()
    if exist is not None:
        exist.result = res
        exist.job_id = job_id
        db.session.commit()
    else:
        new_fibo = fibo_db(request=int(x),result=res, job_id=str(job_id))
        db.session.add(new_fibo)
        db.session.commit()
    return res

@app.route("/fib/", methods=['post', 'get'])
def send_fibo():
    x = int(request.args['x'])
    res = get_from_cache(x)
    if res is None:    
        res = enqueue(x)
    return str(res)

@app.route("/dict", methods=['post', 'get'])
def send_dict():
    db_items = fibo_db.query.all()
    for item in db_items:
        di[item.request] = item.result
    return di

@app.route("/health", methods=['post', 'get'])
def send_health():
    status_code = Response(status=200, response='OK!')
    return status_code