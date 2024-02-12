#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=arcee_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f arcee/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pycodestyle ./arcee"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "cd arcee && pylint --rcfile=.pylintrc ./"
echo "<<Pylint tests"

echo "Unit tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pytest ./arcee/arcee_receiver/tests/"
echo "<<Unit tests"
docker rmi ${TEST_IMAGE}