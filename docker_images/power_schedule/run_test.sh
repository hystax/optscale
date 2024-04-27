#!/usr/bin/env bash

set -e

BUILD_TAG='build'
TEST_IMAGE=power_schedule_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} \
    -f docker_images/power_schedule/Dockerfile_tests .

echo "Unit tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "python3 -m unittest discover ./docker_images/power_schedule/tests"
echo "<<<Unit tests"

docker rmi ${TEST_IMAGE}
