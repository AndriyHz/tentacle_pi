# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       21.08.2015

"""

import time

from tentacle_pi.twi.sensor.bmp180 import BMP180


bmp = BMP180()

if bmp.ok():
    for i in range(0, 5):
        measurement = bmp.measure()
        for key, val in measurement.items():
            print("%s: %s" % (key, val))
        print("")
        time.sleep(3)