#!/usr/bin/env python
import sys
from setuptools import setup


requirements = ["requests==2.32.3", "retrying==1.3.3"]

setup(name='report-client',
      description='OptScale Report Client',
      url='http://hystax.com',
      author='Hystax',
      author_email='info@hystax.com',
      package_dir={'report_client': ''},
      packages=['report_client'],
      install_requires=requirements,
      )
