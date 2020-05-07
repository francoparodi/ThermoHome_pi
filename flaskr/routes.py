from datetime import datetime
import threading, time, json, random
from flask import current_app as app
from flask import Blueprint, render_template, flash, request, redirect, copy_current_request_context
from flaskr.models import db, Settings, EnvironmentData
from flaskr.utils import umConversions

sensorSimulation = False
try:
    from sense_hat import SenseHat
    sense = SenseHat()
except (RuntimeError, ModuleNotFoundError):
    from flaskr.utils.sensorMock import SensorMock
    sense = SensorMock()
    sensorSimulation = True

from flask_socketio import SocketIO

socketio = SocketIO()

stop_event = threading.Event()
daemon = threading.Thread()
isDaemonStarted = False

environmentData = EnvironmentData()

view = Blueprint("view", __name__)

@view.context_processor
def inject_settings():
    settings = Settings.query.get(1)
    return dict(settings=settings)

@view.route("/")
def homepage():
    settings = Settings.query.get(1)
    return render_template("homepage.html", settings=settings)

@view.route("/settings")
def settings():
    settings = Settings.query.get(1)
    return render_template("settings.html", settings=settings)

@view.route("/update", methods=["POST"])
def update():
    try:
        requestDataToDB(request, db)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        msg = "Failed to update settings"
        print(e)
        flash(msg)
    return redirect("/settings")

@socketio.on('connect')
def on_connect():
    socketio.emit('daemonProcess', getEnvironmentData().toJson())

@socketio.on('handleDaemon')
def on_handleDaemon(data):
    action=data['action']

    @copy_current_request_context
    def daemonProcess(name, stop_event):
        while not stop_event.is_set():
            emitIfChanges()
            time.sleep(int(Settings.query.get(1).readFromSensorInterval))
    
    def emitIfChanges():
        if(isDataChanged()):
            socketio.emit('daemonProcess', getEnvironmentData().toJson())

    global isDaemonStarted
    if action == 'START':
        if not isDaemonStarted:
            daemon.__init__(target=daemonProcess, args=('ThermoPi', stop_event), daemon=True)
            daemon.start()
            isDaemonStarted = True
    else:
        stop_event.set()
        daemon.join()
        stop_event.clear()
        isDaemonStarted = False

def requestDataToDB(request, db):
    temperatureUm = request.form.get("temperatureUm")
    readFromSensorInterval = request.form.get("readFromSensorInterval")

    minDeltaDataTrigger = request.form.get("minDeltaDataTrigger")
    temperatureCorrection = request.form.get("temperatureCorrection")
    humidityCorrection = request.form.get("humidityCorrection")
    
    settings = Settings.query.get(1)
    settings.temperatureUm = temperatureUm
    settings.readFromSensorInterval = readFromSensorInterval

    settings.minDeltaDataTrigger = float( '0.0' if minDeltaDataTrigger == '' else minDeltaDataTrigger )
    settings.temperatureCorrection = float( '0.0' if temperatureCorrection == '' else temperatureCorrection )
    settings.humidityCorrection = int( '0' if humidityCorrection == '' else humidityCorrection )

def setEnvironmentDataValues():
    temperatureCorrection = float(Settings.query.get(1).temperatureCorrection)
    humidityCorrection = int(Settings.query.get(1).humidityCorrection)
    temperature = round(sense.get_temperature(), 1)
    humidity = round(sense.get_humidity(), 1)
    temperatureUm = Settings.query.get(1).temperatureUm
    if (temperatureUm == '°F'):
        temperature = umConversions.celsiusToFahrenheit(temperature, 1)
    humidityUm = '%'

    temperature = round(temperature + temperatureCorrection, 1)
    humidity = round(humidity + humidityCorrection, 1)
    dateTime = str(datetime.now())

    getEnvironmentData().set_dateTime(dateTime)
    getEnvironmentData().set_temperature(temperature) 
    getEnvironmentData().set_humidity(humidity)
    getEnvironmentData().set_temperatureUm(temperatureUm)  
    getEnvironmentData().set_humidityUm(humidityUm)
    getEnvironmentData().set_sensorSimulation(sensorSimulation)

def getEnvironmentData():
    return environmentData

def isDataChanged():
    previousTemperature = getEnvironmentData().get_temperature()
    setEnvironmentDataValues()
    currentTemperature = getEnvironmentData().get_temperature()
    deltaAbs = abs(abs(previousTemperature) - abs(currentTemperature))
    minDeltaDataTrigger = float(Settings.query.get(1).minDeltaDataTrigger)
    return deltaAbs >= minDeltaDataTrigger
