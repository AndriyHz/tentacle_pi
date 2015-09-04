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

from setuptools import setup, find_packages

VERSION = "1.0.0.dev"

setup(
    name="tentacle_pi",
    packages=find_packages('.', exclude=["tests", "test"]),
    entry_points={

    },
    version=VERSION,
    install_requires=[],
    description="tentacle_pi",
    author="Alexander Rüedlinger",
    author_email="a.rueedlinger@gmail.com",
    license="GPLv2",
    classifiers=[],
    ext_modules=[],
    long_description="""\
Tentacle Pi - A collection of drivers for TWI/SMBus devices.
-------------------------------------


"""
)
