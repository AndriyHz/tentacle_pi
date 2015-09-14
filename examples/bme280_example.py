# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       21.08.2015

"""

import time

from tentacle_pi.twi.sensor import BME280


bme = BME280()

for i in range(0, 5):
    # take measurements from all sensors
    measurement = bme.measure()

    # iterate over measurements
    for key, val in measurement.items():
        print("%s: %s" % (key, val))
    print("")

    time.sleep(2)

temp = bme.temperature  # measure temperature in Celsius
hum = bme.humidity  # measure relative humidity
pressure = bme.pressure  # measure pressure in pascal
print("temperature[C]: %s" % temp)
print("pressure[pa]: %s" % pressure)
print("rel. humidity: %s" % hum)