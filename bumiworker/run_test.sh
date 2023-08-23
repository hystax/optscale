#!/usr/bin/env bash

set -e

BUILD_TAG='build'
TEST_IMAGE=bumiworker_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f bumiworker/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pep8 --max-line-length=125 ./bumiworker"
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pylint --rcfile=bumiworker/.pylintrc ./bumiworker; exit \$(( \$? & 3 ))"
echo "<<Pylint tests"

docker rmi ${TEST_IMAGE}
