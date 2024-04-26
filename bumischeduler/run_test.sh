#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=bumischeduler_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f bumischeduler/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pycodestyle --max-line-length=120 bumischeduler"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "pylint --rcfile=bumischeduler/.pylintrc --fail-under=9 --fail-on=E,F ./bumischeduler"
echo "<<Pylint tests"

echo "Unit tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "python3 -m unittest discover ./bumischeduler/bumischeduler/tests"
echo "<<Unit tests"

docker rmi ${TEST_IMAGE}
