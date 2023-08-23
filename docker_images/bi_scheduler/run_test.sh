#!/usr/bin/env bash
set -e

BUILD_TAG=${CI_PIPELINE_ID:-'build'}
TEST_IMAGE=bi_scheduler_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f docker_images/bi_scheduler/Dockerfile_tests .
docker run -i --rm ${TEST_IMAGE}  bash -c "python3 -m unittest test_bi_scheduler.py"
docker rmi ${TEST_IMAGE}
