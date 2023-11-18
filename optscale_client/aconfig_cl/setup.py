#!/usr/bin/env python
import sys
from setuptools import setup


setup(name='aconfig-cl',
      description='OptScale Async Config Client Prototype',
      author='Hystax',
      url='http://hystax.com',
      author_email='info@hystax.com',
      package_dir={'aconfig_cl': ''},
      install_requires=['aiohttp==3.8.6'],
      packages=['aconfig_cl']
      )
