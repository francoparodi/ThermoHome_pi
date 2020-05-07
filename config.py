import os
import logging

APP_NAME = "flaskr"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

class Config():
    SQLALCHEMY_DATABASE_FILENAME = os.path.join(PROJECT_DIR, APP_NAME, "db/application.db")
    SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(SQLALCHEMY_DATABASE_FILENAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)

class Logger():
    LOG_FILENAME = "/var/tmp/flaskr.log"
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOG_FILENAME)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)