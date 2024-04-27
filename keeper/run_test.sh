#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=keeper_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f keeper/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pycodestyle --max-line-length=120 keeper"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "pylint --rcfile=.pylintrc --fail-under=8 --fail-on=E,F ./keeper"
echo "<<<Pylint tests"

echo "Unit tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "python3 -m unittest discover ./keeper/report_server/tests"
echo "<<Unit tests"

docker rmi ${TEST_IMAGE}
