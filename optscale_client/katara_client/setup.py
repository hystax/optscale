#!/usr/bin/env python
import sys
from setuptools import setup


requirements = ["requests==2.25.0", "retrying==1.3.3"]

setup(name='katara-client',
      description='Katara Client',
      url='http://hystax.com',
      author='Hystax',
      author_email='info@hystax.com',
      package_dir={'katara_client': ''},
      packages=['katara_client'],
      install_requires=requirements,
      )
