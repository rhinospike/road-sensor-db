import sys
from flask.ext.sqlalchemy import SQLAlchemy
from flask import json
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import CheckConstraint

db = SQLAlchemy()

class SensorReading(db.Model):
    __tablename__ = "sensors"

    sensorid = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.DateTime, primary_key=True)
    gas = db.Column(db.Float)
    dust = db.Column(db.Float)
    noise = db.Column(db.Float)

    __table_args__ = (
        CheckConstraint('NOT(gas IS NULL AND dust IS NULL AND noise IS NULL)', name='AllNullCheck'),
        )

    def __init__(self, sensorid, timestamp, gas=None, dust=None, noise=None):
        self.sensorid = int(sensorid.replace(':', ''), 16)
        print("{:012x}".format(self.sensorid), file=sys.stderr)
        self.timestamp = timestamp
        self.gas = gas
        self.dust = dust
        self.noise = noise

    def tojson(self):
        return {
            "sensorid": "{:012x}".format(self.sensorid),
            "timestamp": str(self.timestamp),
            "sensors": {
                "gas": self.gas,
                "dust": self.dust,
                "noise": self.noise
            }
        }

    def __repr__(self):
        return str(self.tojson())

