#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=auth_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f auth/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pep8 --max-line-length=120 --ignore=E701 --exclude auth/auth_server/alembic/versions/ ."
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "cd auth/auth_server && pylint --rcfile=.pylintrc ./"
echo "<<Pylint tests"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "cd auth/auth_server && nosetests --config .noserc"
echo "<<Nose tests"

docker rmi ${TEST_IMAGE}