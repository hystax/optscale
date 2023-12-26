#!/usr/bin/env bash

set -e

BUILD_TAG='build'
TEST_IMAGE=layout_cleaner_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f docker_images/layout_cleaner/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pycodestyle docker_images/layout_cleaner/"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pylint --rcfile=docker_images/layout_cleaner/.pylintrc docker_images/layout_cleaner/; exit \$(( \$? & 3 ))"
echo "<<Pylint tests"

docker rmi ${TEST_IMAGE}
