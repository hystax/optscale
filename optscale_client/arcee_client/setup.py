#!/usr/bin/env python
import sys
from setuptools import setup


requirements = ["requests==2.31.0", "retrying==1.3.3"]

setup(name='arcee-client',
      description='Arcee Cluster client',
      url='http://hystax.com',
      author='Hystax',
      author_email='info@hystax.com',
      package_dir={'arcee_client': ''},
      packages=['arcee_client'],
      install_requires=requirements,
      )
