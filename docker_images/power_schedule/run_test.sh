#!/usr/bin/env bash

set -e

BUILD_TAG='build'
TEST_IMAGE=power_schedule_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} \
    -f docker_images/power_schedule/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pycodestyle docker_images/power_schedule"
echo "<<<Pycodestyle tests"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "cd docker_images/power_schedule/tests && nosetests --config .noserc"
echo "<<Nose tests"

docker rmi ${TEST_IMAGE}
