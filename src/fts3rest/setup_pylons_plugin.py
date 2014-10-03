#!/usr/bin/env python
from setuptools import setup

setup(
    entry_points="""
[nose.plugins]
pylons = pylons.test:PylonsPlugin
"""
)

