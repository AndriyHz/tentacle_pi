# -*- coding: utf-8 -*-

"""
Tentacle Pi - A collection of drivers for TWI/SMBus devices.
Copyright (c) 2015 Alexander Rüedlinger <a.rueedlinger@gmail.com>

This file is part of Tentacle Pi:
https://github.com/lexruee/tentacle_pi

Tentacle Pi is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Tentacle Pi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

__author__ = 'Alexander Rüedlinger'
__all__ = ['LM75']

from tentacle_pi.util import SMBusAdapter as Adapter


class LM75(object):

    REG_TMP = 0x00
    REG_CONF = 0x01
    REG_THYST = 0x02
    REG_TOS = 0x03

    def __init__(self, addr=0x48, bus=1):
        self._adapter = Adapter(addr, bus)

    def ok(self):
        return True

    def _get_temperature(self):
        data = self._adapter.read_word_data(self.REG_TMP)
        msb = data & 0x00ff
        lsb = data & 0xff00
        temperature = msb + 0.5 * ((lsb & 0x80) >> 7)
        return temperature

    @property
    def temperature(self):
        return self._get_temperature()

    def measure(self, measurement=None):
        measurement = measurement or {}
        temp = self._get_temperature()

        measurement['temperature'] = temp
        return measurement