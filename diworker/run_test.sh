#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=diworker_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f diworker/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pep8 --max-line-length=120 ./diworker"
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
  "pylint --ignore=diworker/diworker/migrations --rcfile=diworker/.pylintrc ./diworker/; exit \$(( \$? & 3 ))"
echo "<<Pylint tests"

docker rmi ${TEST_IMAGE}
