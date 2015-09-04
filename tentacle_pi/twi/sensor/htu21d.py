# -*- coding: utf-8 -*-

"""
Tentacle Pi - A collection of drivers for TWI/SMBus devices.
Copyright (c) 2015 Alexander Rüedlinger <a.rueedlinger@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

__author__ = 'Alexander Rüedlinger'
__all__ = ['HTU21D']


from tentacle_pi.util import I2CAdapter as Adapter
import time


class HTU21D(object):

    CMD_TEMP_MEAS = 0xf3
    CMD_HUM_MEAS = 0xf5
    CMD_TEMP_MEAS_HOLD = 0xe3
    CMD_HUM_MEAS_HOLD = 0xe5
    CMD_SOFT_RESET = 0xfe

    REG_WRITE = 0xe6
    REG_READ = 0xe7

    def __init__(self, addr=0x40, bus=1):
        self._adapter = Adapter(addr, bus)
        self._reset()

    def _reset(self):
        self._adapter.write_byte(self.CMD_SOFT_RESET)

    def _read_temperature(self):
        self._adapter.write_byte(self.CMD_TEMP_MEAS)
        time.sleep(50/1000.0)
        msb, lsb, crc = self._adapter.read_bytes(3)
        out = (msb << 8) | lsb
        temp = -46.85 + 175.72 * out / 65536.0
        return temp

    def _read_humidity(self):
        self._adapter.write_byte(self.CMD_HUM_MEAS)
        time.sleep(20/1000.0)
        msb, lsb, crc = self._adapter.read_bytes(3)
        out = (msb << 8) | lsb
        rh = -6 + 125.0 * out / 65536.0
        return rh

    @property
    def temperature(self):
        temp = self._read_temperature()
        return temp

    @property
    def humidity(self):
        hum = self._read_humidity()
        return hum

    def measure(self, measurement=None):
        measurement = measurement or {}
        temp = self._read_temperature()
        hum = self._read_humidity()
        measurement['temperature'] = temp
        measurement['humidity'] = hum
        return measurement

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._adapter.close()

    def __enter__(self):
        return self