# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       21.08.2015

"""

import time

from tentacle_pi.twi.sensor.mpl115a2 import MPL115A2


mpl = MPL115A2()

for i in range(0, 5):
    measurement = mpl.measure()
    for key, val in measurement.items():
        print("%s: %s" % (key, val))
    print("")
    time.sleep(3)


temp = mpl.temperature  # measure temperature in Celsius
pressure = mpl.pressure  # measure pressure in pascal
print("temperature[C]: %s" % temp)
print("pressure[pa]: %s" % pressure)