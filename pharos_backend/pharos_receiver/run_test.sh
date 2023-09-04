#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=pharos_receiver_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f pharos_backend/pharos_receiver/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pep8 --max-line-length=120 --ignore=E701 ."
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "cd pharos_backend/pharos_receiver && pylint --rcfile=.pylintrc ./"

docker rmi ${TEST_IMAGE}

