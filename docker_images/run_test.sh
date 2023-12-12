#!/usr/bin/env bash
set -e
BUILD_TAG='build'
IMAGE_NAME=$1
DIR=${2:-'docker_images'}

TEST_IMAGE=${IMAGE_NAME}_tests:${BUILD_TAG}
docker build -t ${TEST_IMAGE} --build-arg IMAGE=$1 -f docker_images/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pep8 --max-line-length=120 --ignore=E701 ./$DIR"
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pylint --rcfile=.pylintrc ./$DIR; exit \$(( \$? & 3 ))"
echo "<<<Pylint tests"

docker rmi ${TEST_IMAGE}
