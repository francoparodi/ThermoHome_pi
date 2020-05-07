import random

class SensorMock(object):

    def __init__(self):
        self.__low_light = False
        self.__pixels = []

    def get_temperature(self):
        return random.uniform(-20,50)

    def get_humidity(self):
        return random.uniform(0,99)
