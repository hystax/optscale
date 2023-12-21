#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=diworker_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f diworker/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pycodestyle --max-line-length=120 diworker"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
  "pylint --rcfile=diworker/.pylintrc --fail-under=9 --fail-on=E,F ./diworker"
echo "<<Pylint tests"

docker rmi ${TEST_IMAGE}
