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
__all__ = ['AM2315']


import time
from tentacle_pi.util import I2CAdapter as Adapter


class AM2315(object):
    """
    Based on discussion in the adafruit community:
    https://forums.adafruit.com/viewtopic.php?f=45&t=48285&start=45
    """

    REG_RH_H = 0x00
    REG_RH_L = 0x01

    REG_TMP_H = 0x02
    REG_TMP_L = 0x03

    REG_VERSION = 0x0A
    REG_STATUS = 0x0F
    FUNCTION_CODE = 0x03

    WAIT_TIME = 1/1000.0

    I2C_SLAVE = 0x0703

    def __init__(self, addr=0x5c, bus=1):
        self._adapter = Adapter(addr, bus)

    def _read_data(self):
        self._wakeup()
        self._adapter.write_bytes([self.FUNCTION_CODE, 0x00, 0x04])
        time.sleep(0.01)
        data = self._adapter.read_bytes(8)
        return data

    def _get_humidity(self, data):
        msb = data[2] << 8
        lsb = data[3]
        hum = msb | lsb
        return hum / 10.0

    def _get_temperature(self, data):
        msb = (data[4] & 0x7F)  # ignore sign bit
        msb <<= 8
        lsb = data[5]
        temp = msb | lsb

        if data[4] & 0x80:
            temp *= -1

        return temp / 10.0

    @property
    def temperature(self):
        data = self._read_data()
        return self._get_temperature(data)

    @property
    def humidity(self):
        data = self._read_data()
        return self._get_humidity(data)

    def measure(self, measurement=None):
        measurement = measurement or {}
        data = self._read_data()
        temp = self._get_temperature(data)
        hum = self._get_humidity(data)

        measurement['humidity'] = hum
        measurement['temperature'] = temp
        return measurement

    def _wakeup(self):
        try:
            self._adapter.write_byte(0x00)
        except IOError:
            pass

        time.sleep(0.01)

    def close(self):
        self._adapter.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self