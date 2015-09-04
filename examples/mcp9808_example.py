# -*- coding: utf-8 -*-

"""
@author     Alexander Rüedlinger <a.rueedlinger@gmail.com>
@date       21.08.2015

"""

import time

from tentacle_pi.twi.sensor.mcp9808 import MCP9808


mcp = MCP9808()

if mcp.ok():

    for i in range(0, 5):
        print("t: %s" % mcp.temperature)
        print("")
        time.sleep(3)