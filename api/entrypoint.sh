#!/bin/bash
python3 db.py
flask db init
#flask db migrate
#flask db upgrade
uwsgi --http 0.0.0.0:5000 --module api:app