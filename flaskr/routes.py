from datetime import datetime
import threading, time, json, random
from flask import current_app as app
from flask import Blueprint, render_template, flash, request, redirect, copy_current_request_context
from flaskr.models import db, Settings, EnvironmentData, Schedule
from flaskr.utils import umConversions

sensorSimulation = False
try:
    import Adafruit_DHT as sensor
except (RuntimeError, ModuleNotFoundError):
    from flaskr.utils.sensorMock import SensorMock
    sensor = SensorMock()
    sensorSimulation = True

DHT_SENSOR = sensor.DHT22
DHT_PIN = 4

from flask_socketio import SocketIO

socketio = SocketIO()

stop_event = threading.Event()
daemon = threading.Thread()
isDaemonStarted = False

temperatureToReach = 20
temperatureReached = False
environmentData = EnvironmentData()

view = Blueprint("view", __name__)

@view.context_processor
def inject():
    settings = Settings.query.get(1)
    schedule = Schedule.query.all()
    return dict(settings=settings, schedule=schedule)

@view.route("/")
def homepage():
    settings = Settings.query.get(1)
    schedule = Schedule.query.all()
    return render_template("homepage.html", settings=settings, schedule=schedule)

@view.route("/settings")
def settings():
    settings = Settings.query.get(1)
    return render_template("settings.html", settings=settings)

@view.route("/updateSettings", methods=["POST"])
def updateSettings():
    try:
        saveSettings(request, db)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        msg = "Failed to update settings"
        print(e)
        flash(msg)
    return redirect("/settings")

@view.route("/updateSchedule", methods=["POST"])
def updateSchedule():
    try:
        saveSchedule(request, db)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        msg = "Failed to update schedule"
        print(e)
        flash(msg)
    return redirect("/homepage")

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
            triggerActuator()
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

def saveSettings(request, db):
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

def saveSchedule(request, db):
    weekDays = [1,2,3,4,5,6,7]
    db.session.query(Schedule).delete()
    for day in weekDays:
        timeValues = request.form.get('timeValue'+str(day)).split(",")
        schedule = Schedule()
        schedule.weekDay = day
        schedule.temperatureReference = float(request.form.get('temperature'+str(day)))
        schedule.temperatureUm = Settings.query.get(1).temperatureUm
        schedule.timeBegin01 = float(timeValues[0])
        schedule.timeEnd01 = float(timeValues[1])
        schedule.timeBegin02 = float(timeValues[2])
        schedule.timeEnd02 = float(timeValues[3])
        schedule.timeBegin03 = float(timeValues[4])
        schedule.timeEnd03 = float(timeValues[5])
        db.session.add(schedule)
        db.session.commit()

def setEnvironmentDataValues():
    temperatureCorrection = float(Settings.query.get(1).temperatureCorrection)
    humidityCorrection = int(Settings.query.get(1).humidityCorrection)
    #temperature = round(sensor.get_temperature(), 1)
    #humidity = round(sensor.get_humidity(), 1)
    humidity, temperature = sensor.read_retry(DHT_SENSOR, DHT_PIN)
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
    if (temperatureToReach < temperature):
        temperatureReached = False
    else:
        temperatureReached = True
    getEnvironmentData().set_temperatureReached(temperatureReached)

def getEnvironmentData():
    return environmentData

def isDataChanged():
    previousTemperature = getEnvironmentData().get_temperature()
    setEnvironmentDataValues()
    currentTemperature = getEnvironmentData().get_temperature()
    deltaAbs = abs(abs(previousTemperature) - abs(currentTemperature))
    minDeltaDataTrigger = float(Settings.query.get(1).minDeltaDataTrigger)
    return deltaAbs >= minDeltaDataTrigger

def triggerActuator():
    day = datetime.today().isoweekday()
    todayReferenceTemperature = float(Schedule.query.get(day).temperatureReference)
    todayCurrentTemperature = getEnvironmentData().get_temperature()
    if (todayCurrentTemperature < todayReferenceTemperature):
        switch(True)
    else:
        switch(False)

def switch(status):
    if (status):
        print('Switch ON')
    else:
        print('Switch OFF')

