# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       21.08.2015

"""

import time
from tentacle_pi.twi.sensor import AM2315


with AM2315() as am:
    for i in range(0, 5):
        # take measurements from all sensors
        measurement = am.measure()

        # iterate over measurements
        for key, val in measurement.items():
            print("%s: %s" % (key, val))
        print("")

        time.sleep(2)

    temp = am.temperature  # measure temperature in Celsius
    hum = am.humidity  # measure relative humidity
    print("temperature[C]: %s" % temp)
    print("rel. humidity: %s" % hum)