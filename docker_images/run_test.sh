#!/usr/bin/env bash
set -e
BUILD_TAG='build'
IMAGE_NAME=$1
TEST_IMAGE=${IMAGE_NAME}_tests:${BUILD_TAG}
docker build -t ${TEST_IMAGE} --build-arg IMAGE=$1 --build-arg PROJECT=${IMAGE_NAME} -f docker_images/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "uv --directory docker_images/${IMAGE_NAME} run pycodestyle --max-line-length=120 --exclude=.venv ."
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "uv --project docker_images/${IMAGE_NAME} run pylint --fail-under=9 --fail-on=E,F --ignore=.venv docker_images/${IMAGE_NAME}"
echo "<<<Pylint tests"

docker rmi ${TEST_IMAGE}
