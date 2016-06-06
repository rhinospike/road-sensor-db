import sys
from flask import json
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import CheckConstraint

db = SQLAlchemy()

SENSOR_ID = "sensorid"
TIMESTAMP = "timestamp"
SENSORS = "sensors"
SENSOR_TYPE = "sensor"
SENSOR_VALUE = "value"
LONGITUDE = "longitude"
LATITUDE = "latitude"

def MACToInt(macstring):
    return int(macstring.replace(':',''), 16)

def intToMAC(val):
    full = '%012x' % (val)
    pieces = [full[i:i+2] for i in range(0, 12, 2)]
    return ':'.join(pieces).upper()

class Sensor(db.Model):
    __tablename__ = "sensors"

    sensorid = db.Column(db.BigInteger, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def fromjson(json):
        return Sensor(MACToInt(json[SENSOR_ID]),
                json.get(LATITUDE),
                json.get(LONGITUDE))

    def tojson(self):
        return {
            "sensorid" : intToMAC(self.sensorid),
            "latitude" : self.latitude,
            "longitude" : self.longitude
        }

    def __init__(self, sensorid, latitude, longitude):
        self.sensorid = sensorid
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return str(self.sensorid)

class SensorReading(db.Model):
    __tablename__ = "readings"

    sensorid = db.Column(db.BigInteger, ForeignKey('sensors.sensorid'), primary_key=True)
    timestamp = db.Column(db.DateTime, primary_key=True)
    gas = db.Column(db.Float)
    dust = db.Column(db.Float)
    noise = db.Column(db.Float)

    __table_args__ = (
        CheckConstraint('NOT(gas IS NULL AND dust IS NULL AND noise IS NULL)', name='AllNullCheck'),
        )

    def __init__(self, sensorid, timestamp, gas=None, dust=None, noise=None):
        self.sensorid = sensorid
        self.timestamp = timestamp
        self.gas = gas
        self.dust = dust
        self.noise = noise

    def fromjson(data):
        readings = data[SENSORS]
        return SensorReading(
                MACToInt(data[SENSOR_ID]),
                data[TIMESTAMP],
                readings.get("gas"),
                readings.get("dust"),
                readings.get("noise"))

    def tojson(self):
        return {
            "sensorid": intToMAC(self.sensorid),
            "timestamp": str(self.timestamp),
            "sensors": {
                "gas": self.gas,
                "dust": self.dust,
                "noise": self.noise
            }
        }

    def __repr__(self):
        return str(self.tojson())

