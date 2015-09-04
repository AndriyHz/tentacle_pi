#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
Tentacle Pi - A collection of drivers for I2C/SMBus devices.
-------------------------------------


"""
)
