import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config, Logger
from flaskr.models import db, Settings, Schedule
from flaskr import create_app

print('Setup started (log to {0})'.format(Logger.LOG_FILENAME))
Logger.logger.debug('Setup started')

database_file = Config.SQLALCHEMY_DATABASE_FILENAME
if os.path.exists(database_file):
    Logger.logger.debug('Remove DB {0}'.format(database_file))
    os.remove(database_file)

app = create_app()
with app.test_request_context():
    app.config.from_object(Config)
    db.init_app(app)
    Logger.logger.debug('Create DB {0}'.format(database_file))
    db.create_all()

    Logger.logger.debug('Populate Settings DB {0}'.format(database_file))
    settings = Settings(
                temperatureUm = '°C', 
                humidityUm = '%',
                readFromSensorInterval = 10, 
                minDeltaDataTrigger = 0.5, 
                temperatureCorrection = 0.0, 
                humidityCorrection = 0
                )
    db.session.add(settings)
    db.session.commit()

    Logger.logger.debug('Populate Schedule DB {0}'.format(database_file))
    weekDays = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    for day in weekDays:
        schedule = Schedule()
        schedule.weekDay = day
        schedule.temperatureReference = 19.5
        schedule.temperatureUm = '°C'
        schedule.timeBegin01 = 6.0
        schedule.timeEnd01 = 8.5
        schedule.timeBegin02 = 11.0
        schedule.timeEnd02 = 14.0
        schedule.timeBegin03 = 17.0
        schedule.timeEnd03 = 22.5
        db.session.add(schedule)
        db.session.commit()

Logger.logger.debug('Setup completed')
print('Setup completed')


exit()