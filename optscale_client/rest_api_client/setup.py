#!/usr/bin/env python
from setuptools import setup


requirements = ["requests==2.31.0", "retrying==1.3.3"]

setup(name='restapi-client',
      description='OptScale REST API Client',
      url='http://hystax.com',
      author='Hystax',
      author_email='info@hystax.com',
      package_dir={'rest_api_client': ''},
      packages=['rest_api_client'],
      install_requires=requirements,
      )
