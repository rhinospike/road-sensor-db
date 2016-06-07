import os
import sys
import json
import datetime
from flask import Flask, request, json, abort, redirect, url_for, render_template
from sqlalchemy import exc, bindparam
from sqlalchemy.ext import baked
from sqlalchemy import desc 
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
app.app_context().push()
db.init_app(app)
db.create_all()

@app.route("/")
def hello():
    return "Welcome to the road sensor network database."

@app.route("/echo/<text>")
def echo(text):
    return text

def dumper(obj):
    try:
        return obj.tojson()
    except:
        return obj.__dict__

@app.route("/sensors")
def getsensors():
    query = db.session.query(Sensor)

    sensorid = request.args.get("sensorid")

    if sensorid:
        sensorid = int(sensorid.replace(':',''), 16)
        query = query.filter(Sensor.sensorid == sensorid)

    result = query.all()

    return json.dumps(result, default=dumper)

@app.route("/sensors", methods = ['POST'])
def register():
    if request.headers['Content-Type'] == 'application/json':

        newsensor = Sensor.fromjson(request.get_json())

        existing = db.session.query(Sensor).filter(Sensor.sensorid == newsensor.sensorid).first()
        if existing:
            existing.latitude = newsensor.latitude
            existing.longitude = newsensor.longitude
        else:
            db.session.add(newsensor)

        try:
            db.session.commit()
            return str(newsensor)

        except exc.IntegrityError as e:
            reason = str(e)

        if reason.find('violates unique constraint') != -1:
            return "Primary key already exists", 422
    else:
        return "Unsupported Media Type", 415

@app.route("/readings")
def getreadings():
    print('get readings', file=sys.stderr)
    sensorid = request.args.get("sensorid")
    if (sensorid != None):
        sensorid = int(sensorid.replace(':',''), 16)
    starttime = request.args.get("starttime")
    endtime = request.args.get("endtime")

    query = db.session.query(SensorReading)

    if sensorid:
        query = query.filter(SensorReading.sensorid == sensorid)
    if starttime:
        query = query.filter(SensorReading.timestamp >= starttime)
    if endtime:
        query = query.filter(SensorReading.timestamp <= endtime)

    result = query.order_by(desc(SensorReading.timestamp)).all()

    return json.dumps(result, default=dumper)

@app.route("/readings", methods = ['POST'])
def insertreadings():
    print('inserting:', file=sys.stderr)

    if request.headers['Content-Type'] == 'application/json':

        for jsonsr in request.get_json():

            sr = SensorReading.fromjson(jsonsr)

            result = "Sensor readings received from sensor {0} @ {1}:".format(sr.sensorid, sr.timestamp)
            print(result, file=sys.stderr)

            # Check if sensor is in database
            q = db.session.query(Sensor).filter(Sensor.sensorid == sr.sensorid)
            if q.first() == None:
                # Add new sensor with unknown coordinates
                newsensor = Sensor(sr.sensorid, 0, 0)
                print('Adding new sensor {0!s}'.format(newsensor), file=sys.stderr)
                db.session.add(newsensor)
                db.session.commit()
                print('Sensor {0!s} added'.format(newsensor), file=sys.stderr)

            db.session.add(sr)

            print(sr.dust, file=sys.stderr)

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
