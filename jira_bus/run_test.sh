#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=jira_bus_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f jira_bus/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pep8 --max-line-length=120 --ignore=E701,E203,E231 ."
echo "<<<PEP8 tests"


echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "cd jira_bus/jira_bus_server && pylint --rcfile=.pylintrc ./"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "cd jira_bus/jira_bus_server && nosetests --config .noserc"
echo "<<Nose tests"

docker rmi ${TEST_IMAGE}
