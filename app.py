from flask import Flask, request, render_template
import redis
from rq import Queue
from time import sleep
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

def fibo(x: int):
    if x == 0:
        return 0
    elif x == 1:
        return 1
    else:
        return fibo(x-1) + fibo(x-2)

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")

app = Flask(__name__)
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
app.config['DEBUG'] = True

redis_server = redis.Redis("localhost")
q = Queue(connection=redis_server)

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

@app.route("/", methods=['post', 'get'])
def index():
    x = 0
    if request.method == 'POST':
	    x = int(request.form.get('x'))  # запрос к данным формы
    try:
        result = q.enqueue(fibo, x, result_ttl=60*60*24)
        sleep(5)
        new_fibo = fibo_db(request=x,result=int(result.result))
        db.session.add(new_fibo)
        db.session.commit()
        return render_template('index.html', variable=result.result)
    except:
        pass
