#!/usr/bin/env python
import sys
from setuptools import setup

setup(name='check_alembic_down_revisions',
      description='Alembic down revisions check',
      url='http://hystax.com',
      author='Hystax',
      author_email='info@hystax.com',
      package_dir={'check_alembic_down_revisions': ''},
      packages=['check_alembic_down_revisions'],
      install_requires=[],
      scripts=['check_alembic_down_revisions.py']
      )
