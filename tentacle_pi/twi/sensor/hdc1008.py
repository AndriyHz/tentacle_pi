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
__all__ = ['HDC1008']

from tentacle_pi.util import I2CAdapter as Adapter
import time


class HDC1008(object):
    """Driver implementation for the HDC1008 temperature / humidity sensor."""

    ADDR_1 = 0x40
    ADDR_2 = 0x41
    ADDR_3 = 0x42
    ADDR_4 = 0x43

    TMP_HUM = 1 << 12
    TMP_RES_14 = 0
    TMP_RES_11 = 1 << 10

    HUM_RES_14 = 0
    HUM_RES_11 = 1 << 8
    HUM_RES_8 = 2 << 8

    REG_CONF = 0x02
    REG_SER_ID1 = 0xfb
    REG_SER_ID2 = 0xfc
    REG_SER_ID3 = 0xfd

    def __init__(self, addr=0x40, bus=1):
        """Create a HDC1008 sensor device object.

        :param addr: optional i2c address of the device
        :param bus: optional number of the i2c bus
        :return: HDC1008 sensor device object.
        """
        self._adapter = Adapter(addr, bus)
        self._config = self.TMP_HUM | self.HUM_RES_14 | self.TMP_RES_14
        self._serial_id = self._read_serial()
        self._configure()

    def _configure(self):
        self._adapter.write_bytes([self.REG_CONF, self._config >> 8, self._config & 0xff])
        time.sleep(15 / 1000.0)

    def _read_serial(self):
        self._adapter.write_byte(self.REG_SER_ID1)
        msb, lsb = self._adapter.read_bytes(2)
        id1 = msb << 8 | lsb

        self._adapter.write_byte(self.REG_SER_ID2)
        msb, lsb = self._adapter.read_bytes(2)
        id2 = msb << 8 | lsb

        self._adapter.write_byte(self.REG_SER_ID3)
        msb, lsb = self._adapter.read_bytes(2)
        id3 = msb << 8 | lsb
        serial_id = (id1 << 32) | (id2 << 16) | id3
        serial_id >>= 7
        return serial_id

    def _read_temperature(self):
        self._adapter.write_byte(0x00)
        time.sleep(15 / 1000.0)
        msb, lsb = self._adapter.read_bytes(2)
        word = msb << 8 | lsb
        temp = (word / 65536.0) * 165 - 40
        return temp

    def _read_humidity(self):
        self._adapter.write_byte(0x01)
        time.sleep(15 / 1000.0)
        msb, lsb = self._adapter.read_bytes(2)
        word = msb << 8 | lsb
        hum = (word / 65536.0) * 100
        return hum

    @property
    def temperature(self):
        """Return temperature in Celsius.

        :return: return temperature
        """
        return self._read_temperature()

    @property
    def humidity(self):
        """Return relative humidity.

        :return: return humidity
        """
        return self._read_humidity()

    @property
    def serial(self):
        return self._serial_id

    def measure(self, measurement=None):
        """ Take a measurement of all available sensors.

        :param measurement: optional dictionary to store sensor values
        :return: return dictionary with stored sensor values
        """
        measurement = measurement or {}
        temp = self._read_temperature()
        hum = self._read_humidity()
        measurement['temperature'] = temp
        measurement['humidity'] = hum
        return measurement

    def close(self):
        self._adapter.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self


