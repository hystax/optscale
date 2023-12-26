#!/usr/bin/env bash
set -e
BUILD_TAG='build'
IMAGE_NAME=$1
DIR=${2:-'docker_images'}

TEST_IMAGE=${IMAGE_NAME}_tests:${BUILD_TAG}
docker build -t ${TEST_IMAGE} --build-arg IMAGE=$1 -f docker_images/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pycodestyle --max-line-length=120 $DIR"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "pylint --rcfile=.pylintrc --fail-under=9 --fail-on=E,F ./$DIR"
echo "<<<Pylint tests"

docker rmi ${TEST_IMAGE}
