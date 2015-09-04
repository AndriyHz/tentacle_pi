# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       21.08.2015

"""

import time

from tentacle_pi.twi.sensor.tsl2561 import TSL2561

tsl = TSL2561()

for i in range(0, 5):
    measurement = tsl.measure()
    for key, val in measurement.items():
        print("%s: %s" % (key, val))
        print("")
        time.sleep(3)