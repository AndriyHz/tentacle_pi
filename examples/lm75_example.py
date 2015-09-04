# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       21.08.2015

"""

import time

from tentacle_pi.twi.sensor.lm75 import LM75


lm = LM75()


for i in range(0, 5):
    print("t: %s" % lm.temperature)
    print("")
    time.sleep(3)