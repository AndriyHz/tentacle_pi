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
__all__ = ['MCP9808']

from tentacle_pi.util import SMBusAdapter as Adapter


class MCP9808(object):
    """Driver implementation for the MCP9808 temperature sensor."""

    REG_CONFIG = 0x01
    REG_TMP_MSB = 0x02
    REG_TMP_LSB = 0x03
    REG_ALERT = 0x04
    REG_TMP = 0x05
    REG_MANUF_ID = 0x06
    REG_DEVICE_ID = 0x07
    REG_RES = 0x08

    MANUF_ID = 0x54
    DEVICE_ID = 0x04

    def __init__(self, addr=0x18, bus=1):
        """Create a MCP9808 sensor device object.

        :param addr: optional i2c address of the device
        :param bus: optional number of the i2c bus
        :return: MCP9808 sensor device object.
        """
        self._adapter = Adapter(addr, bus)
        self._device_id = self._read_device_id()
        self._manuf_id = self._read_manuf_id()

    def ok(self):
        return self._manuf_id == self.MANUF_ID and self._device_id == self.DEVICE_ID

    def _read_device_id(self):
        return self._adapter.read_byte_data(self.REG_DEVICE_ID)

    def _read_manuf_id(self):
        word = self._adapter.read_word_data(self.REG_MANUF_ID)
        return (word & 0xff00) >> 8

    def _get_temperature(self):
        data = self._adapter.read_word_data(self.REG_TMP)
        msb = data & 0x00ff
        lsb = (data & 0xff00) >> 8
        word = (msb << 8) | lsb
        temperature = word & 0x0fff
        temperature /= 16.0

        if word & 0x1000:
            temperature -= 256
        return temperature

    @property
    def chip_id(self):
        return self._device_id

    @property
    def manuf_id(self):
        return self._manuf_id

    @property
    def temperature(self):
        """Return temperature in Celsius.

        :return: return temperature
        """
        return self._get_temperature()

    def measure(self, measurement=None):
        """ Take a measurement of all available sensors.

        :param measurement: optional dictionary to store sensor values
        :return: return dictionary with stored sensor values
        """
        measurement = measurement or {}
        temp = self._get_temperature()

        measurement['temperature'] = temp
        return measurement
