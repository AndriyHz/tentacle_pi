## Changelog

##### 1.0.0
 * change license from MIT to GPLv2
 * add support for the following TWI (I2C) devices:
   * BMP280
   * BME280
   * HTU21D
   * HDC1008
 * remove C extension code
 * restructure tentacle_pi module
   * move TWI (I2C) sensor drivers in module: tentacle_pi.twi.sensor
 * rewrite all drivers in 0.6.2 in pure python:
   * AM2315 / AM2321
   * BMP180
   * TSL2561
   * MCP9808
   * MPL115A2
   * LM75

##### 0.6.2
  * fix module names in c extensions

##### 0.6.1
  * forgot to update git submodules. Sry, my bad :-).
  * add tests:
    * test_load_sensors.py
    * test_fixed_segfault.py

##### 0.6.0
  * fix bug: running a python script without sudo results in a segmentation fault

##### 0.5.0
  * update drivers / synchronize drivers with master branch
  * add support for i2c sensor LM75

##### 0.4.0
  * MPL115A2 driver
   * use the suggested temperature formula in http://forums.adafruit.com/viewtopic.php?f=25&t=34787

##### 0.3.0
  * add support for i2c sensor MPL115A2

##### 0.2.0
  * add support for i2c sensor MCP9808

##### 0.1.0
  * first release
  * add support for i2c sensor BMP180
  * add support for i2c sensor AM2315
  * add support for i2c sensor TSL2561
