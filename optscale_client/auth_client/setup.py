#!/usr/bin/env python
import sys
from setuptools import setup


requirements = ["requests==2.31.0", "retrying==1.3.3"]

setup(name='auth-client',
      description='OptScale Auth Client',
      url='http://hystax.com',
      author='Hystax',
      author_email='info@hystax.com',
      package_dir={'auth_client': ''},
      packages=['auth_client'],
      install_requires=requirements,
      )
