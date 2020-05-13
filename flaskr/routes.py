from datetime import datetime
import sys, threading, time, json, random
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

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    sys.modules['smbus'] = fake_rpi.smbus
    import RPi.GPIO as GPIO
    import smbus

RELAY_GPIO = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_GPIO, GPIO.OUT)

from flask_socketio import SocketIO
socketio = SocketIO()
environmentData = EnvironmentData()

stop_event = threading.Event()
daemon = threading.Thread()
isDaemonStarted = False
flameOn = False

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
        updateSettings(request, db)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        msg = "Failed to update settings"
        print(e)
        flash(msg)
    return redirect("/settings")

@view.route("/saveSchedule", methods=["POST"])
def saveSchedule():
    try:
        saveSchedule(request, db)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        msg = "Failed to save schedule"
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
            if(isDataChanged()):
                triggerActuator()
                socketio.emit('daemonProcess', getEnvironmentData().toJson())
            time.sleep(int(Settings.query.get(1).readFromSensorInterval))
    
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

def updateSettings(request, db):
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
    day = datetime.today().isoweekday()
    schedule = Schedule.query.get(day)
    if (schedule.temperatureReference < temperature):
        flameOn = False
    else:
        flameOn = True
    getEnvironmentData().set_flameOn(flameOn)

def getEnvironmentData():
    return environmentData

def isDataChanged():
    previousTemperature = getEnvironmentData().get_temperature()
    setEnvironmentDataValues()
    currentTemperature = getEnvironmentData().get_temperature()
    delta = abs(abs(previousTemperature) - abs(currentTemperature))
    minDeltaDataTrigger = float(Settings.query.get(1).minDeltaDataTrigger)
    return delta >= minDeltaDataTrigger

def triggerActuator():
    day = datetime.today().isoweekday()
    schedule = Schedule.query.get(day)
    if (isInRangeTime(schedule) and getEnvironmentData().get_temperature() < schedule.temperatureReference):
        print('Switch ON')
        GPIO.output(RELAY_GPIO, GPIO.LOW)
        getEnvironmentData().set_flameOn(True)
    else:
        print('Switch OFF')
        GPIO.output(RELAY_GPIO, GPIO.HIGH)
        getEnvironmentData().set_flameOn(False)

def isInRangeTime(schedule):
    dt = datetime.now()
    currentTime = dt.hour
    # From minutes to number for comparison (7:25 -> 7.0 , 7:31 -> 7.5)
    if (dt.minute > 29):
        currentTime += 0.5
    if ((currentTime >= schedule.timeBegin01 and currentTime <= schedule.timeEnd01) or
        (currentTime >= schedule.timeBegin02 and currentTime <= schedule.timeEnd02) or
        (currentTime >= schedule.timeBegin03 and currentTime <= schedule.timeEnd03)):
        return True
    return False


