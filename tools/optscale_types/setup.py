#!/usr/bin/env python
import sys
from setuptools import setup

requirements = ['requests==2.25.0', 'SQLAlchemy==1.1.4',
                'optscale-exceptions==0.0.23', 'netaddr==0.7.18']

setup(name='optscale-types',
      description='OptScale Types',
      url='http://hystax.com',
      author='Hystax',
      author_email='info@hystax.com',
      package_dir={'optscale_types': ''},
      packages=['optscale_types'],
      install_requires=requirements,
      )
