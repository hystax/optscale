#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=herald_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f herald/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pep8 --max-line-length=120 --ignore=E701 ."
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "cd herald/herald_server && ls && pylint --rcfile=.pylintrc ./"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "cd herald/herald_server && nosetests --config .noserc"
echo "<<Nose tests"

docker rmi ${TEST_IMAGE}