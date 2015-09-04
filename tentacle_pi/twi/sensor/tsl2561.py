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
__all__ = ['TSL2561']


from tentacle_pi.util import SMBusAdapter as Adapter
import time


class TSL2561(object):

    # T, FN, and CL Package coefficients
    K1T = 0x0040
    B1T = 0x01F2
    M1T = 0x01BE
    K2T = 0x0080
    B2T = 0x0214
    M2T = 0x02D1
    K3T = 0x00C0
    B3T = 0x023F
    M3T = 0x037B
    K4T = 0x0100
    B4T = 0x0270
    M4T = 0x03FE
    K5T = 0x0138
    B5T = 0x016F
    M5T = 0x01fC
    K6T = 0x019A
    B6T = 0x00D2
    M6T = 0x00FB
    K7T = 0x029A
    B7T = 0x0018
    M7T = 0x0012
    K8T = 0x029A
    B8T = 0x0000
    M8T = 0x0000

    # CS package coefficients
    K1C = 0x0043
    B1C = 0x0204
    M1C = 0x01AD
    K2C = 0x0085
    B2C = 0x0228
    M2C = 0x02C1
    K3C = 0x00C8
    B3C = 0x0253
    M3C = 0x0363
    K4C = 0x010A
    B4C = 0x0282
    M4C = 0x03DF
    K5C = 0x014D
    B5C = 0x0177
    M5C = 0x01DD
    K6C = 0x019A
    B6C = 0x0101
    M6C = 0x0127
    K7C = 0x029A
    B7C = 0x0037
    M7C = 0x002B
    K8C = 0x029A
    B8C = 0x0000
    M8C = 0x0000

    REG_CTRL = 0x00
    REG_TIMING = 0x01

    REG_CH0_LOW = 0x0C
    REG_CH0_HIGH = 0x0D
    REG_CH1_LOW = 0x0E
    REG_CH1_HIGH = 0x0F

    CMD_BIT = 0x80
    WORD_BIT = 0x20

    CTRL_PWR_ON = 0x03
    CTRL_PWR_OFF = 0x00

    ADDR_LOW = 0x29
    ADDR_DEFAULT = 0x39
    ADDR_HIGH = 0x49

    GAIN_0X = 0x00
    GAIN_16X = 0x10

    INTEGRATION_TIME_13 = 0x00
    INTEGRATION_TIME_101 = 0x01
    INTEGRATION_TIME_402 = 0x02

    INTEGRATION_TIME_402MS = 0.403
    INTEGRATION_TIME_101MS = 0.101
    INTEGRATION_TIME_13MS = 0.013

    CLIPPING_13MS = 4900
    CLIPPING_101MS = 37000
    CLIPPING_402MS = 65000

    LUX_SCALE = 14
    RATIO_SCALE = 9

    CH_SCALE = 10
    CH_SCALE_TINT0 = 0x7517
    CH_SCALE_TINT1 = 0x0FE7

    TYPE_T = 0
    TYPE_CS = 1

    def __init__(self, addr=0x39, bus=1):
        self._addr = addr
        self._adapter = Adapter(addr, bus)
        self._gain = self.GAIN_0X
        self._integration_time = self.INTEGRATION_TIME_402
        self._type = self.TYPE_T

        self._set_enable()
        self._set_integration_timing()

    def _set_integration_timing(self):
        self._adapter.write_byte_data(self.CMD_BIT | self.REG_TIMING, self._integration_time | self._gain)

    def _set_gain(self):
        self._adapter.write_byte_data(self.CMD_BIT | self.REG_TIMING, self._integration_time | self._gain)

    def _set_enable(self):
        self._adapter.write_byte_data(self.CMD_BIT | self.REG_CTRL, self.CTRL_PWR_ON)

    def _set_disable(self):
        self._adapter.write_byte_data(self.CMD_BIT | self.REG_CTRL, self.CTRL_PWR_OFF)

    def enable(self):
        self._set_enable()

    def disable(self):
        self._set_disable()

    @property
    def gain(self):
        return self._gain

    @gain.setter
    def gain(self, val):
        self._gain = val
        self._set_gain()

    @property
    def integration_time(self):
        return self._integration_time

    @integration_time.setter
    def integration_time(self, val):
        self._integration_time = val
        self._set_integration_timing()

    def _get_illuminance(self):
        ir, broadband = self._read_data()
        if self._integration_time == self.INTEGRATION_TIME_402MS:
            threshold = self.CLIPPING_402MS
        elif self._integration_time == self.INTEGRATION_TIME_101MS:
            threshold = self.CLIPPING_101MS
        elif self._integration_time == self.INTEGRATION_TIME_13MS:
            threshold = self.CLIPPING_13MS
        else:
            threshold = self.CLIPPING_402MS

        if ir > threshold or broadband > threshold:
            return 0

        return self._compute_illuminance(ir, broadband)

    def _compute_illuminance(self, ch0, ch1):
        if self._integration_time == self.INTEGRATION_TIME_101MS:
            ch_scale = self.CH_SCALE_TINT1
        elif self._integration_time == self.INTEGRATION_TIME_13MS:
            ch_scale = self.CH_SCALE_TINT0
        else:
            ch_scale = (1 << self.CH_SCALE)

        if self._gain != self.GAIN_16X:
            ch_scale <<= 4

        channel0 = (ch0 * ch_scale) >> self.CH_SCALE
        channel1 = (ch1 * ch_scale) >> self.CH_SCALE
        ratio, ratio1 = 0, 0

        if channel0 != 0:
            ratio1 = (channel1 << (self.RATIO_SCALE + 1)) / channel0

        ratio = int(ratio1 + 1) >> 1
        b, m = 0, 0

        if self._type == self.TYPE_CS:
            if 0 <= ratio <= self.K1C:
                b, m = self.B1C, self.M1C
            elif ratio <= self.K2C:
                b, m = self.B2C, self.M2C
            elif ratio <= self.K3C:
                b, m = self.B3C, self.M3C
            elif ratio <= self.K4C:
                b, m = self.B4C, self.M4C
            elif ratio <= self.K5T:
                b, m = self.B5C, self.M5C
            elif ratio <= self.K6T:
                b, m = self.B6C, self.M6C
            elif ratio <= self.K7T:
                b, m = self.B7C, self.M7C
            elif ratio <= self.K8C:
                b, m = self.B8C, self.M8C
        else:
            if 0 <= ratio <= self.K1T:
                b, m = self.B1T, self.M1T
            elif ratio <= self.K2T:
                b, m = self.B2T, self.M2T
            elif ratio <= self.K3T:
                b, m = self.B3T, self.M3T
            elif ratio <= self.K4T:
                b, m = self.B4T, self.M4T
            elif ratio <= self.K5T:
                b, m = self.B5T, self.M5T
            elif ratio <= self.K6T:
                b, m = self.B6T, self.M6T
            elif ratio <= self.K7T:
                b, m = self.B7T, self.M7T
            elif ratio <= self.K8T:
                b, m = self.B8T, self.M8T

        tmp = (channel0 * b) - (channel1 * m)
        if tmp < 0:
            tmp = 0

        tmp += (1 << self.LUX_SCALE - 1)
        illuminance = (tmp >> self.LUX_SCALE)
        return illuminance

    def _read_data(self):
        self._set_enable()

        if self._integration_time == self.INTEGRATION_TIME_402MS:
            time.sleep(self.INTEGRATION_TIME_402MS)
        elif self._integration_time == self.INTEGRATION_TIME_101MS:
            time.sleep(self.INTEGRATION_TIME_101MS)
        elif self._integration_time == self.INTEGRATION_TIME_13MS:
            time.sleep(self.INTEGRATION_TIME_13MS)
        else:
            time.sleep(self.INTEGRATION_TIME_402MS)

        broadband = self._adapter.read_word_data(self.CMD_BIT | self.WORD_BIT | self.REG_CH0_LOW)
        ir = self._adapter.read_word_data(self.CMD_BIT | self.WORD_BIT | self.REG_CH1_LOW)

        self._set_disable()

        return broadband, ir

    @property
    def illuminance(self):
        return self._get_illuminance()

    def measure(self, measurement=None):
        measurement = measurement or {}
        measurement['illuminance'] = self._get_illuminance()
        return measurement