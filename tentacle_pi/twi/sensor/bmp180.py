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
__all__ = ['BMP280']

from tentacle_pi.util import SMBusAdapter as Adapter
import time
from ctypes import c_short, c_ushort


class BMP180(object):

    SEA_LEVEL = 101325

    REG_AC1_H = 0xAA
    REG_AC2_H = 0xAC
    REG_AC3_H = 0xAE
    REG_AC4_H = 0xB0
    REG_AC5_H = 0xB2
    REG_AC6_H = 0xB4

    REG_B1_H = 0xB6
    REG_B2_H = 0xB8
    REG_MB_H = 0xBA
    REG_MC_H = 0xBC
    REG_MD_H = 0xBE

    PRE_OSS_LOW = 0
    PRE_OSS_STANDARD = 1
    PRE_OSS_HIGH = 2
    PRE_OSS_ULTRA_HIGH = 3

    CTRL_PRE_OSS_LOW = 0x34
    CTRL_PRE_OSS_STANDARD = 0x74
    CTRL_PRE_OSS_HIGH = 0xB4
    CTRL_PRE_OSS_ULTRA_HIGH = 0xF4
    CTRL_TMP = 0x2E

    REG_OUT_XLSB = 0xF8  # adc out: bits 7-3
    REG_OUT_LSB = 0xF7  # adc out: bits 7-0
    REG_OUT_MSB = 0xF6  # adc out: bits 7-0

    REG_CTRL_MEAS = 0xF4
    REG_SOF = 0xE0  # reset
    REG_ID = 0xD0
    CHIP_ID = 0x55

    WAITING_TIME = 5/1000.0  # s

    def __init__(self, addr=0x77, bus=1):
        self._oss = self.PRE_OSS_LOW

        self._adapter = Adapter(addr, bus)
        self._chip_id = self._read_id()
        self._eprom = {}
        self._eprom_names = ['ac1', 'ac2', 'ac3', 'ac4', 'ac5', 'ac6', 'b1', 'b2', 'mb', 'mc', 'md']
        self._read_eprom()

    def ok(self):
        return self.CHIP_ID == self.chip_id

    def _read_id(self):
        return self._adapter.read_byte_data(self.REG_ID)

    def _read_eprom(self):
        eprom_data = self._adapter.read_i2c_block_data(self.REG_AC1_H, 22)
        for i in range(0, len(self._eprom_names)):
            name = self._eprom_names[i]
            msb, lsb = eprom_data[2*i], eprom_data[2*i + 1]
            self._eprom[name] = (msb << 8) | lsb

        for key in ['ac1', 'ac2', 'ac3', 'b1', 'b2', 'mb', 'mc', 'md']:
            word = self._eprom[key]
            self._eprom[key] = c_short(word).value

        for key in ['ac4', 'ac5', 'ac6']:
            word = self._eprom[key]
            self._eprom[key] = c_ushort(word).value

    def _read_raw_temperature(self):
        self._adapter.write_byte_data(self.REG_CTRL_MEAS, self.CTRL_TMP)
        time.sleep(self.WAITING_TIME)
        data = self._adapter.read_i2c_block_data(self.REG_OUT_MSB, 2)
        if data is None:
            raise RuntimeError

        msb, lsb = data
        msb <<= 8
        adc_t = msb | lsb
        return adc_t

    def _read_raw_pressure(self):
        cmd = self._get_pressure_cmd()
        self._adapter.write_byte_data(self.REG_CTRL_MEAS, cmd)
        time.sleep(self.WAITING_TIME)
        data = self._adapter.read_i2c_block_data(self.REG_OUT_MSB, 3)
        if data is None:
            raise RuntimeError

        msb, lsb, xlsb = data
        lsb <<= 8
        msb <<= 16
        adc_p = (msb | lsb | xlsb) >> (8 - self._oss)
        return adc_p

    def _get_temperature(self):
        try:
            UT = self._read_raw_temperature()
            ac6 = self._eprom['ac6']
            ac5 = self._eprom['ac5']
            md = self._eprom['md']
            mc = self._eprom['mc']
            X1 = ((UT - ac6) * ac5) >> 15
            X2 = (mc << 11) / (X1 + md)
            B5 = X1 + X2
            T = ((B5 + 8) >> 4) / 10.0
            return T

        except RuntimeError:
            return None

    def _get_pressure(self):
        try:
            UT = self._read_raw_temperature()
            UP = self._read_raw_pressure()
            ac6 = self._eprom['ac6']
            ac5 = self._eprom['ac5']
            ac4 = self._eprom['ac4']
            ac3 = self._eprom['ac3']
            ac2 = self._eprom['ac2']
            ac1 = self._eprom['ac1']
            b1 = self._eprom['b1']
            b2 = self._eprom['b2']
            md = self._eprom['md']
            mc = self._eprom['mc']

            X1 = ((UT - ac6) * ac5) >> 15
            X2 = (mc << 11) / (X1 + md)
            B5 = X1 + X2
            B6 = B5 - 4000
            X1 = (b2 * (B6 * B6) >> 12) >> 11
            X2 = (ac2 * B6) >> 11
            X3 = X1 + X2

            B3 = ((((ac1 * 4) + X3) << self._oss) + 2) / 4
            X1 = (ac3 * B6) >> 13
            X2 = (b1 * ((B6 * B6) >> 12)) >> 16
            X3 = ((X1 + X2) + 2) >> 2

            B4 = ac4 * (X3 + 32768) >> 15
            B7 = (UP - B3) * (50000 >> self._oss)

            if B7 < 0x80000000:
                p = (B7 * 2) / B4
            else:
                p = (B7 / B4) * 2

            X1 = (p >> 8) * (p >> 8)
            X1 = (X1 * 3038) >> 16
            X2 = (-7357 * p) >> 16
            p += ((X1 + X2 + 3791) >> 4)
            return p

        except RuntimeError:
            return None

    def _get_pressure_cmd(self):
        if self._oss == self.PRE_OSS_LOW:
            return self.CTRL_PRE_OSS_LOW
        elif self._oss == self.PRE_OSS_STANDARD:
            return self.CTRL_PRE_OSS_STANDARD
        elif self._oss == self.PRE_OSS_HIGH:
            return self.CTRL_PRE_OSS_HIGH
        elif self._oss == self.PRE_OSS_ULTRA_HIGH:
            return self.CTRL_PRE_OSS_ULTRA_HIGH
        else:
            self._oss = self.PRE_OSS_STANDARD
            return self.CTRL_PRE_OSS_STANDARD

    def _get_altitude(self, pressure):
        alt = 44330 * (1 - pow((float(pressure) / self.SEA_LEVEL), 1/5.255))
        return alt

    @property
    def chip_id(self):
        return self._chip_id

    @property
    def eprom(self):
        return self._eprom

    @property
    def pressure(self):
        return self._get_pressure()

    @property
    def temperature(self):
        return self._get_temperature()

    @property
    def altitude(self):
        p = self.pressure or 0
        alt = self._get_altitude(p)
        return alt

    def measure(self, measurement=None):
        measurement = measurement or {}
        temp = self._get_temperature()
        pressure = self._get_pressure()
        altitude = self._get_altitude(pressure)

        measurement['temperature'] = temp
        measurement['pressure'] = pressure
        measurement['altitude'] = altitude
        return measurement

    @property
    def oss(self):
        return self._oss

    @oss.setter
    def oss(self, value):
        if 0 <= value <= 3:
            self._oss = value