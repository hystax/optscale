#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=diproxy_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f diproxy/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pycodestyle diproxy"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "pylint --rcfile=diproxy/.pylintrc --fail-under=9 --fail-on=E,F ./diproxy"
echo "<<Pylint tests"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE}  bash -c "nosetests --config diproxy/.noserc"
echo "<<Nose tests"

docker rmi ${TEST_IMAGE}
