# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       7.09.2015

"""

import time

from tentacle_pi.twi.sensor.hdc1008 import HDC1008


with HDC1008() as hdc:
    for i in range(0, 5):
        measurement = hdc.measure()
        for key, val in measurement.items():
            print("%s: %s" % (key, val))
        print("")
        time.sleep(3)