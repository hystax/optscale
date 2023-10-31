#!/usr/bin/env python
from setuptools import setup


requirements = ["requests==2.31.0", "retrying==1.3.3"]

setup(name='insider-client',
      description='Hystax Insider Client',
      url='http://hystax.com',
      author='Hystax',
      author_email='info@hystax.com',
      package_dir={'insider_client': ''},
      packages=['insider_client'],
      install_requires=requirements,
      )
