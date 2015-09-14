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
__all__ = ['BME280']

from tentacle_pi.util import SMBusAdapter as Adapter
from ctypes import c_short, c_ushort, c_byte, c_ubyte


class BME280(object):
    """Driver implementation for the BME280 integrated environmental sensor (humidity, pressure, temperature)."""

    SEA_LEVEL = 101325

    REG_T1_L = 0x88
    REG_T2_L = 0x8A
    REG_T3_L = 0x8C

    REG_P1_L = 0x8E
    REG_P2_L = 0x90
    REG_P3_L = 0x92
    REG_P4_L = 0x94
    REG_P5_L = 0x96
    REG_P6_L = 0x98
    REG_P7_L = 0x9A
    REG_P8_L = 0x9C
    REG_P9_L = 0x9E

    REG_H1_L = 0xA1
    REG_H2_L = 0xE1
    REG_H3_L = 0xE3
    REG_H4_L = 0xE4
    REG_H5_L = 0xE5
    REG_H6_L = 0xE7

    OSRS_P0 = 0
    OSRS_P1 = 1
    OSRS_P2 = 2
    OSRS_P4 = 3
    OSRS_P8 = 4
    OSRS_P16 = 5

    OSRS_T0 = 0
    OSRS_T1 = 1
    OSRS_T2 = 2
    OSRS_T4 = 3
    OSRS_T8 = 4
    OSRS_T16 = 5

    OSRS_H0 = 0
    OSRS_H1 = 1
    OSRS_H2 = 2
    OSRS_H4 = 3
    OSRS_H8 = 4
    OSRS_H16 = 5

    POWER_SLEEP = 0
    POWER_FORCED = 1
    POWER_NORMAL = 3

    REG_ID = 0xD0
    CHIP_ID = 0x60
    REG_RESET = 0xE0
    REG_CONFIG = 0xF5
    REG_CTRL_MEAS = 0xF4
    REG_CTRL_HUM = 0xF2
    RESET_VAL = 0xB6

    REG_TMP = 0xFA
    REG_PRE = 0xF7
    REG_HUM = 0xFD

    def __init__(self, addr=0x77, bus=1):
        """Create a BME280 sensor device object.

        :param addr: optional i2c address of the device
        :param bus: optional number of the i2c bus
        :return: BME280 sensor device object.
        """
        self._osrs_h = self.OSRS_H1
        self._osrs_t = self.OSRS_T1
        self._osrs_p = self.OSRS_P1
        self._t_sb = 5
        self._filter = 0
        self._t_fine = None
        self._power_mode = self.POWER_NORMAL
        self._eprom = {}

        self._eprom_names = ['t1', 't2', 't3',
                             'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9',
                             'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

        self._adapter = Adapter(addr, bus)
        self._chip_id = self._read_id()
        self._set_meas_and_hum()
        self._set_config()
        self._read_eprom()

    def ok(self):
        return self.CHIP_ID == self.chip_id

    def _read_id(self):
        return self._adapter.read_byte_data(self.REG_ID)

    def _read_eprom(self):
        for i in range(0, 12):
            name = self._eprom_names[i]
            self._eprom[name] = self._adapter.read_word_data(self.REG_T1_L + 2*i)

        self._eprom['h1'] = self._adapter.read_byte_data(self.REG_H1_L)
        self._eprom['h2'] = self._adapter.read_word_data(self.REG_H2_L)
        self._eprom['h3'] = self._adapter.read_byte_data(self.REG_H3_L)
        self._eprom['h4'] = self._adapter.read_byte_data(self.REG_H4_L) << 4
        self._eprom['h4'] |= self._adapter.read_byte_data(self.REG_H4_L + 1) & 0x0F
        self._eprom['h5'] = self._adapter.read_byte_data(self.REG_H5_L) >> 4
        self._eprom['h5'] |= self._adapter.read_byte_data(self.REG_H5_L + 1) << 4
        self._eprom['h6'] = self._adapter.read_byte_data(self.REG_H6_L)

        for key in ['t1', 'p1']:
            word = self._eprom[key]
            self._eprom[key] = c_ushort(word).value

        for key in ['t2', 't3', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'h2', 'h4', 'h5']:
            word = self._eprom[key]
            self._eprom[key] = c_short(word).value

        for key in ['h1', 'h3']:
            _byte = self._eprom[key]
            self._eprom[key] = c_ubyte(_byte).value

        for key in ['h6']:
            _byte = self._eprom[key]
            self._eprom[key] = c_byte(_byte).value

    def _set_meas(self):
        settings = 0
        settings |= (self._osrs_t << 5)
        settings |= (self._osrs_p << 2)
        settings |= self._power_mode
        self._adapter.write_byte_data(self.REG_CTRL_MEAS, settings)

    def _set_hum(self):
        settings = 0
        settings |= self._osrs_h
        self._adapter.write_byte_data(self.REG_CTRL_HUM, settings)

    def _set_meas_and_hum(self):
        self._set_hum()
        self._set_meas()

    def _set_config(self):
        config = 0
        config |= (self._t_sb << 5)
        config |= (self._filter << 2)
        self._adapter.write_byte_data(self.REG_CONFIG, config)

    def _read_raw_temperature(self):
        data = self._adapter.read_i2c_block_data(self.REG_TMP, 3)
        if data is None:
            raise RuntimeError

        msb, lsb, xlsb = data

        adc_t = (msb << 12) | (lsb << 4) | (xlsb >> 4)
        return adc_t

    def _read_raw_pressure(self):
        data = self._adapter.read_i2c_block_data(self.REG_PRE, 3)
        if data is None:
            raise RuntimeError

        msb, lsb, xlsb = data
        adc_p = (msb << 12) | (lsb << 4) | (xlsb >> 4)
        return adc_p

    def _read_raw_humidity(self):
        data = self._adapter.read_i2c_block_data(self.REG_HUM, 2)
        if data is None:
            raise RuntimeError

        msb, lsb = data
        adc_h = (msb << 8) | lsb
        return adc_h

    def _get_temperature(self):
        try:
            adc_t = self._read_raw_temperature()
            t1 = self._eprom['t1']
            t2 = self._eprom['t2']
            t3 = self._eprom['t3']

            var1 = (((adc_t >> 3) - (t1 << 1)) * t2) >> 11
            var2 = (((((adc_t >> 4) - t1) * ((adc_t >> 4) - t1)) >> 12) * t3) >> 14
            t_fine = var1 + var2
            self._t_fine = t_fine
            t = (t_fine * 5 + 128) >> 8
            return t / 100.0
        except RuntimeError:
                        return None

    def _get_pressure(self):
        try:
            if self._t_fine is None:
                self._get_temperature()

            adc_p = self._read_raw_pressure()
            p9 = self._eprom['p9']
            p8 = self._eprom['p8']
            p7 = self._eprom['p7']
            p6 = self._eprom['p6']
            p5 = self._eprom['p5']
            p4 = self._eprom['p4']
            p3 = self._eprom['p3']
            p2 = self._eprom['p2']
            p1 = self._eprom['p1']

            var1 = self._t_fine - 128000
            var2 = var1 * var1 * p6
            var2 += ((var1 * p5) << 17)
            var2 += (p4 << 35)
            var1 = ((var1 * var1 * p3) >> 8) + ((var1 * p2) << 12)

            var1 = ((1 << 47) + var1) * p1 >> 33

            if var1 == 0:
                return 0  # avoid exception caused by division by zero

            p = 1048576 - adc_p
            p = (((p << 31) - var2) * 3125) / var1
            var1 = (p9 * (p >> 13) * (p >> 13)) >> 25
            var2 = (p8 * p) >> 19
            p = ((p + var1 + var2) >> 8) + (p7 << 4)
            return p / 256.0
        except RuntimeError:
                    return None

    def _get_humidity(self):
        try:
            if self._t_fine is None:
                self._get_temperature()

            adc_h = self._read_raw_humidity()
            h1 = self._eprom['h1']
            h2 = self._eprom['h2']
            h3 = self._eprom['h3']
            h4 = self._eprom['h4']
            h5 = self._eprom['h5']
            h6 = self._eprom['h6']

            v_x1_u32r = self._t_fine - 76800
            v_x1_u32r = (((adc_h << 14) - (h4 << 20) - (h5 * v_x1_u32r)) + 16384 >> 15) * \
                        ((((v_x1_u32r * h6 >> 10) *
                           ((v_x1_u32r * h3 >> 11) + 32768) >> 10) + 2097152 * h2 + 8192) >> 14)

            v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * h1) >> 4))

            if v_x1_u32r < 0:
                v_x1_u32r = 0
            elif v_x1_u32r > 419430400:
                v_x1_u32r = 419430400

            h = v_x1_u32r >> 12
            return h / 1024.0
        except RuntimeError:
                    return None

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
    def temperature(self):
        """Return temperature in Celsius.

        :return: return temperature
        """
        return self._get_temperature()

    @property
    def pressure(self):
        """Return pressure in pascal.

        :return: return pressure
        """
        return self._get_pressure()

    @property
    def humidity(self):
        """Return relative humidity..

        :return: return humidity
        """
        return self._get_humidity()

    @property
    def altitude(self):
        """Return altitude in meters.

        :return: return altitude
        """
        p = self.pressure or 0
        alt = self._get_altitude(p)
        return alt

    def measure(self, measurement=None):
        """Take a measurement of all available sensors.

        :param measurement: optional dictionary to store sensor values
        :return: return dictionary with stored sensor values
        """
        measurement = measurement or {}
        temp = self._get_temperature()
        pressure = self._get_pressure()
        humidity = self._get_humidity()
        altitude = self._get_altitude(pressure)

        measurement['temperature'] = temp
        measurement['pressure'] = pressure
        measurement['altitude'] = altitude
        measurement['humidity'] = humidity
        return measurement

    @property
    def osrs_h(self):
        return self._osrs_h

    @osrs_h.setter
    def osrs_h(self, value):
        if self.OSRS_H0 <= value <= self.OSRS_H16:
            self._osrs_h = value

    @property
    def osrs_t(self):
        return self._osrs_t

    @osrs_t.setter
    def osrs_t(self, value):
        if self.OSRS_T0 <= value <= self.OSRS_T16:
            self._osrs_t = value

    @property
    def osrs_p(self):
        return self._osrs_p

    @osrs_p.setter
    def osrs_p(self, value):
        if self.OSRS_P0 <= value <= self.OSRS_P16:
            self._osrs_p = value

    @property
    def power_mode(self):
        return self._power_mode

    @power_mode.setter
    def power_mode(self, value):
        if self.POWER_SLEEP <= value <= self.POWER_NORMAL:
            self._power_mode = value

    def update(self):
        self._set_meas_and_hum()
        self._set_config()


