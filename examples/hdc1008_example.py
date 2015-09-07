# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       21.08.2015

"""

import time

from tentacle_pi.twi.sensor.am2315 import AM2315


with AM2315() as am:
    for i in range(0, 5):
        measurement = am.measure()
        for key, val in measurement.items():
            print("%s: %s" % (key, val))
        print("")
        time.sleep(3)