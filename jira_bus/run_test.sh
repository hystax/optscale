#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=jira_bus_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f jira_bus/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pycodestyle --max-line-length=120 jira_bus"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "pylint --rcfile=jira_bus/.pylintrc --fail-under=9 --fail-on=E,F ./jira_bus"
echo "<<Pylint tests"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "nosetests --config jira_bus/.noserc jira_bus"
echo "<<Nose tests"

docker rmi ${TEST_IMAGE}
