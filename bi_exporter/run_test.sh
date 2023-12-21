#!/usr/bin/env bash

set -e

BUILD_TAG='build'
TEST_IMAGE=bi_exporter_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f bi_exporter/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pycodestyle --max-line-length=120 bi_exporter"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "pylint --rcfile=bi_exporter/.pylintrc --fail-under=9 --fail-on=E,F ./bi_exporter"
echo "<<Pylint tests"

echo "Worker tests>>>"
docker run -i --rm ${TEST_IMAGE}  bash -c "python3 bi_exporter/run_tests.py"
echo "<<Worker tests"

docker rmi ${TEST_IMAGE}
