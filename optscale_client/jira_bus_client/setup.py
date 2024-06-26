#!/usr/bin/env python
import sys
from setuptools import setup


requirements = ["requests==2.32.3", "retrying>=1.3.3"]

setup(
    name="jira-bus-client",
    description="OptScale Jira Bus API Client",
    url="http://hystax.com",
    author="Hystax",
    author_email="info@hystax.com",
    package_dir={"jira_bus_client": ""},
    packages=["jira_bus_client"],
    install_requires=requirements,
)
