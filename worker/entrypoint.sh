#!/bin/bash
python3 db.py
uwsgi --http 0.0.0.0:5000 --module api:app