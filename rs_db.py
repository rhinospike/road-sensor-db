import os
import sys
import json
import datetime
from flask import Flask, request, json, abort, redirect, url_for, render_template
from sqlalchemy import exc, bindparam
from sqlalchemy.ext import baked
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
app.app_context().push()
db.init_app(app)
db.create_all()

SENSOR_ID = "sensorid"
TIMESTAMP = "timestamp"
SENSORS = "sensors"
SENSOR_TYPE = "sensor"
SENSOR_VALUE = "value"

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/echo/<text>")
def echo(text):
    return text

def dumper(obj):
    try:
        return obj.tojson()
    except:
        return obj.__dict__

@app.route("/retrieve")
def retrieve():
    sensorid = request.args.get("sensorid")
    starttime = request.args.get("starttime")
    endtime = request.args.get("endtime")

    query = db.session.query(SensorReading)

    if sensorid:
        query = query.filter(SensorReading.sensorid == sensorid)
    if starttime:
        query = query.filter(SensorReading.timestamp >= starttime)
    if endtime:
        query = query.filter(SensorReading.timestamp <= endtime)

    result = query.all()

    return json.dumps(result, default=dumper)

def validate(json):
    if SENSOR_ID in json and TIMESTAMP in json and SENSORS in json:
        if len(json[SENSORS]) > 0:
            return True
    return False

@app.route("/insert", methods = ['POST'])
def insert():
    if request.headers['Content-Type'] == 'application/json':
        parsed = request.get_json()

        sensorid = parsed[SENSOR_ID];
        timestamp = parsed[TIMESTAMP];
        readings = parsed[SENSORS];

        result = "Sensor readings received from sensor {0} @ {1}:".format(sensorid, timestamp)
        print(result, file=sys.stderr)

        sr = SensorReading(sensorid, timestamp, readings.get("gas"), readings.get("dust"), readings.get("noise"))
        db.session.add(sr)

        try:
            db.session.commit()
            return str(sr)

        except exc.IntegrityError as e:
            reason = str(e)

            if reason.find("AllNullCheck") != -1:
                return "No sensor values", 422

            if reason.find('violates unique constraint') != -1:
                return "Primary key already exists", 422

            return "Unkown Error", 500
    else:
        return "Unsupported Media Type", 415

if __name__ == "__main__":
    #app.debug = True
    app.run(host='0.0.0.0', port=int(os.environ['PORT']))
