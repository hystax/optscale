#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=tools_optscale_telemetry_test:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f tools/optscale_telemetry/Dockerfile_tests .

echo "Ruff tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "uv --project tools/optscale_telemetry run ruff check ."
echo "<<<Ruff tests"


echo "pytest tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "uv --project tools/optscale_telemetry run pytest"
echo "<<<pytest tests"

docker rmi ${TEST_IMAGE}
