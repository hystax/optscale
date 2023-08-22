#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=bumischeduler_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f bumischeduler/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pep8 --max-line-length=120 ."
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pylint --rcfile=bumischeduler/.pylintrc ./bumischeduler"
echo "<<Pylint tests"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "nosetests --config .noserc"
echo "<<Nose tests"

docker rmi ${TEST_IMAGE}