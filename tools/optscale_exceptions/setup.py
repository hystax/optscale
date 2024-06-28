#!/usr/bin/env python
import sys
from setuptools import setup


requirements = ['tornado==6.4.1', 'requests==2.32.3']

setup(name='optscale-exceptions',
      description='OptScale Exceptions',
      url='http://hystax.com',
      author='Hystax',
      author_email='info@hystax.com',
      package_dir={'optscale_exceptions': ''},
      packages=['optscale_exceptions'],
      install_requires=requirements,
      )
