#!/usr/bin/env bash

set -e

BUILD_TAG='build'
TEST_IMAGE=bumiworker_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f bumiworker/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pycodestyle --max-line-length=120 bumiworker"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "pylint --rcfile=bumiworker/.pylintrc --fail-under=9 --fail-on=E,F ./bumiworker"
echo "<<Pylint tests"

docker rmi ${TEST_IMAGE}
