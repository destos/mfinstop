#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import mfinstop
version = mfinstop.__version__

setup(
    name='mfinstop',
    version=version,
    author='',
    author_email='patrick@forringer.com',
    packages=[
        'mfinstop',
    ],
    include_package_data=True,
    install_requires=[
        'Django>=1.7.1',
    ],
    zip_safe=False,
    scripts=['mfinstop/manage.py'],
)
