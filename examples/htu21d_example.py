# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       4.09.2015

"""

import time

from tentacle_pi.twi.sensor import HTU21D


with HTU21D() as htu:
    for i in range(0, 5):
        measurement = htu.measure()
        for key, val in measurement.items():
            print("%s: %s" % (key, val))
        print("")
        time.sleep(3)

    temp = htu.temperature  # measure temperature in Celsius
    hum = htu.humidity  # measure relative humidity
    print("temperature[C]: %s" % temp)
    print("rel. humidity: %s" % hum)