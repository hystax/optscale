#!/usr/bin/env bash

set -e

BUILD_TAG='build'
TEST_IMAGE=resource_discovery_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} \
    -f docker_images/resource_discovery/Dockerfile_tests .

echo "Unit tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "cd docker_images/resource_discovery && uv run pytest"
echo "<<<Unit tests"

docker rmi ${TEST_IMAGE}
