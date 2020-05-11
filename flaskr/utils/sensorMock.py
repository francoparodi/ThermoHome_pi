import random

class SensorMock(object):

    DHT22 = 'DHT22'

    def get_temperature(self):
        return random.uniform(-20,50)

    def get_humidity(self):
        return random.uniform(0,99)
    
    def read_retry(self, DHT_SENSOR, DHT_PIN):
        return self.get_humidity(), self.get_temperature()