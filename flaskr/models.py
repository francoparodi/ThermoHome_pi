import json
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    temperatureUm = db.Column(db.String(2), unique=False, default='°C')
    humidityUm = db.Column(db.String(1), unique=False, default='%')
    readFromSensorInterval = db.Column(db.Integer(), unique=False, default=10)
    minDeltaDataTrigger = db.Column(db.Float(1), unique=False, default=1)
    temperatureCorrection = db.Column(db.Float(1), unique=False, default=0.0)
    humidityCorrection = db.Column(db.Integer, unique=False, default=0)
    sensorSimulation = db.Column(db.Boolean, unique=False, default=False)

    def __repr__(self):
        repr = "{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(
            { self.id },
            { self.created_at },
            { self.temperatureUm },
            { self.humidityUm },
            { self.readFromSensorInterval },
            { self.minDeltaDataTrigger },
            { self.temperatureCorrection },
            { self.humidityCorrection },
            { self.sensorSimulation }
        )
        return repr

class EnvironmentData(object):
    def __init__(self):
        self.__dateTime = str(datetime.now())
        self.__temperature = 0.0
        self.__humidity = 0.0
        self.__temperatureUm = '°C'  
        self.__humidityUm = '%'
        self.__sensorSimulation = False
        self.__temperatureReached = False

    # getters
    def get_dateTime(self):
        return self.__dateTime
    
    def get_temperature(self):
        return self.__temperature
    
    def get_humidity(self):
        return self.__humidity
    
    def get_temperatureUm(self):
        return self.__temperatureUm

    def get_humidityUm(self):
        return self.__humidityUm
    
    def get_sensorSimulation(self):
        return self.__sensorSimulation

    def get_temperatureReached(self):
        return self.__temperatureReached

    # setters
    def set_dateTime(self, value):
        self.__dateTime = value
    
    def set_temperature(self, value):
        self.__temperature = value
    
    def set_humidity(self, value):
        self.__humidity = value
    
    def set_temperatureUm(self, value):
        self.__temperatureUm = value

    def set_humidityUm(self, value):
        self.__humidityUm = value

    def set_sensorSimulation(self, value):
        self.__sensorSimulation = value

    def set_temperatureReached(self, value):
        self.__temperatureReached = value

    def __repr__(self):
        repr = "{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(
            { self.__dateTime },
            { self.__temperature },
            { self.__humidity },
            { self.__temperatureUm },
            { self.__humidityUm },
            { self.__sensorSimulation },
            { self.__temperatureReached }
        )
        return repr

    def toJson(self):
        return json.dumps(self.__dict__)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    weekDay = db.Column(db.String(3), unique=True)
    temperatureReference = db.Column(db.Float(1), unique=False, default=20.0)
    temperatureUm = db.Column(db.String(2), unique=False, default='°C')
    timeBegin01 = db.Column(db.Float(1), unique=False, default=6.0)
    timeEnd01 = db.Column(db.Float(1), unique=False, default=8.5)
    timeBegin02 = db.Column(db.Float(1), unique=False, default=11.0)
    timeEnd02 = db.Column(db.Float(1), unique=False, default=14.0)
    timeBegin03 = db.Column(db.Float(1), unique=False, default=17.0)
    timeEnd03 = db.Column(db.Float(1), unique=False, default=22.5)

    def __repr__(self):
        repr = "{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}".format(
            { self.id },
            { self.created_at },
            { self.weekDay },
            { self.temperatureReference },
            { self.temperatureUm },
            { self.timeBegin01 },
            { self.timeEnd01 },
            { self.timeBegin02 },
            { self.timeEnd02 },
            { self.timeBegin03 },
            { self.timeEnd03 }

        )
        return repr  