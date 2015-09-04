# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       21.08.2015

"""

import time

from tentacle_pi.twi.sensor.bme280 import BME280


bme = BME280()

if bme.ok():
    for i in range(0, 5):
        measurement = bme.measure()
        for key, val in measurement.items():
            print("%s: %s" % (key, val))
        print("")
        time.sleep(3)