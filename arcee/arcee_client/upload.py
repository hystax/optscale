#!/usr/bin/env python

import os
import subprocess
import logging
import requests
import re
from distutils.version import LooseVersion


LOG = logging.getLogger()
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.DEBUG)


PYPI_URL = 'http://pypi.dts.loc:8080'
PACKAGE_NAME = 'arcee-client'


def versions():
    url = "%s/simple/%s/" % (PYPI_URL, PACKAGE_NAME)
    resp = requests.get(url)
    links = re.findall('<a href="?\'?([^"\'>]*)', resp.text)
    if links:
        result = list(map((lambda x: x.split(
            '/packages/%s-' % PACKAGE_NAME)[1].split('.tar.gz')[0]), links))
        return result
    return []


def max_ver():
    if not versions():
        return "0.0.1"
    return str(max([LooseVersion(ver) for ver in versions()]))


def increment_ver(ver):
    new_ver = ver.split('.')[:-1]
    new_ver.append(str(int(ver.split('.')[-1]) + 1))
    return '.'.join(new_ver)


def rewrite_version(version):
    with open('version.py', 'w') as fh:
        fh.write('__VERSION__ = "%s"\n' % version)
        return version


def read_ver():
    with open('version.py', 'r') as fh:
        ver = fh.read().replace("'", '"').split('"')[1].split('"')[0] \
            .lstrip().rstrip()
        return ver


def execute(cmd, path=''):
    LOG.info('Executing command %s', ' '.join(cmd))
    myenv = os.environ.copy()
    myenv['PYTHONPATH'] = path
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=myenv)
    proc.communicate()
    LOG.info('Command: %s retcode: %s', ' '.join(cmd), proc.returncode)


if __name__ == '__main__':
    max_version = max_ver()
    LOG.info('Max version from server: %s', max_version)
    version = read_ver()
    LOG.info('Version from setup.py: %s', version)
    if LooseVersion(version) <= LooseVersion(max_version):
        version = rewrite_version(increment_ver(max_version))
    LOG.info('Will upload package with version: %s', version)
    cmd = ['python3', 'setup.py', 'sdist',  'upload', '-r', 'hystax']
    execute(cmd)
