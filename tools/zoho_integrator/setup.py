#!/usr/bin/env python
from setuptools import setup, find_packages


requirements = ['zcrmsdk==3.1.0']

setup(name='zoho-integrator',
      description='Zoho CRM Integrator',
      url='http://hystax.com',
      author='Hystax',
      author_email='info@hystax.com',
      packages=find_packages(),
      install_requires=requirements,
      )
