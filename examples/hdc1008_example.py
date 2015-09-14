# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       7.09.2015

"""

import time

from tentacle_pi.twi.sensor import HDC1008


with HDC1008() as hdc:
    for i in range(0, 5):
        # take measurements from all sensors
        measurement = hdc.measure()

        # iterate over measurements
        for key, val in measurement.items():
            print("%s: %s" % (key, val))
        print("")

    time.sleep(2)

    temp = hdc.temperature  # measure temperature in Celsius
    hum = hdc.humidity  # measure relative humidity
    print("temperature[C]: %s" % temp)
    print("rel. humidity: %s" % hum)