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
__all__ = ['MPL115A2']

from tentacle_pi.util import SMBusAdapter as Adapter
import time
from ctypes import c_short


class MPL115A2(object):
    """Driver implementation for the MCP9808 pressure / temperature sensor."""

    SEA_LEVEL = 101325

    REG_PADC_M = 0x00
    REG_TADC_M = 0x02
    CMD_CONVERT = 0x12

    REG_A0_M = 0x04
    REG_B1_M = 0x06
    REG_B2_M = 0x08
    REG_C12_M = 0x0A

    def __init__(self, addr=0x60, bus=1):
        """Create a MPL115A2 sensor device object.

        :param addr: optional i2c address of the device
        :param bus: optional number of the i2c bus
        :return: MPL115A2 sensor device object.
        """
        self._adapter = Adapter(addr, bus)
        self._coefficient_names = ['a0', 'b1', 'b2', 'c12']
        self._coefficients = {}
        self._read_coefficients()

    def _read_coefficients(self):
        for i in range(0, len(self._coefficient_names)):
            name = self._coefficient_names[i]
            msb, lsb = self._adapter.read_i2c_block_data(self.REG_A0_M + 2*i, 2)
            word = (msb << 8) | lsb
            self._coefficients[name] = c_short(word).value

        self._coefficients['a0'] /= 8.0
        self._coefficients['b1'] /= 8192.0
        self._coefficients['b2'] /= 16384.0
        self._coefficients['c12'] /= 16777216.0

    @property
    def coefficients(self):
        return self._coefficients

    def _get_adc_t(self):
        msb, lsb = self._adapter.read_i2c_block_data(self.REG_TADC_M, 2)
        adc_t = ((msb << 8) | lsb) >> 6
        return adc_t

    def _get_pressure(self):
        a0 = self._coefficients['a0']
        b1 = self._coefficients['b1']
        b2 = self._coefficients['b2']
        c12 = self._coefficients['c12']

        self._adapter.write_byte_data(self.CMD_CONVERT, 0x00)
        time.sleep(5/1000.0)

        adc_t = self._get_adc_t()
        msb, lsb = self._adapter.read_i2c_block_data(self.REG_PADC_M, 2)
        adc_p = ((msb << 8) | lsb) >> 6
        p_comp = a0 + (b1 + c12 * adc_t) * adc_p + b2 * adc_t
        return ((p_comp / 15.737) + 50.0) * 1000

    def _get_temperature(self):
        # black magic temperature formula: http://forums.adafruit.com/viewtopic.php?f=25&t=34787
        # thx @park
        self._adapter.write_byte_data(self.CMD_CONVERT, 0x00)
        time.sleep(5/1000.0)

        adc_t = self._get_adc_t()
        t = adc_t * -0.1706 + 112.27
        return t

    def _get_altitude(self, pressure):
        alt = 44330 * (1 - pow((pressure / self.SEA_LEVEL), 1/5.255))
        return alt

    @property
    def pressure(self):
        """Return pressure in pascal.

        :return: return pressure
        """
        return self._get_pressure()

    @property
    def temperature(self):
        """Return temperature in Celsius.

        :return: return temperature
        """
        return self._get_temperature()

    @property
    def altitude(self):
        """Return altitude in meters.

        :return: return altitude
        """
        p = float(self.pressure)
        alt = 44330 * (1 - pow((p / self.SEA_LEVEL), 1/5.255))
        return alt

    def measure(self, measurement=None):
        """ Take a measurement of all available sensors.

        :param measurement: optional dictionary to store sensor values
        :return: return dictionary with stored sensor values
        """
        measurement = measurement or {}
        temp = self._get_temperature()
        pressure = self._get_pressure()
        altitude = self._get_altitude(pressure)

        measurement['temperature'] = temp
        measurement['pressure'] = pressure
        measurement['altitude'] = altitude
        return measurement

