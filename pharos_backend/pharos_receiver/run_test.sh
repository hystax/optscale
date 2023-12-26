#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=pharos_receiver_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f pharos_backend/pharos_receiver/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pycodestyle --max-line-length=120 pharos_backend"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pylint --rcfile=.pylintrc --fail-under=8 --fail-on=E,F ./pharos_backend"
echo "<<<Pylint tests"

docker rmi ${TEST_IMAGE}

