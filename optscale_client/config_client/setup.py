#!/usr/bin/env python
import sys
from setuptools import setup


setup(name='config-client',
      description='OptScale Config Client',
      author='Hystax',
      url='http://hystax.com',
      author_email='info@hystax.com',
      package_dir={'config_client': ''},
      install_requires=['python-etcd==0.4.5', 'retrying'],
      packages=['config_client']
      )
