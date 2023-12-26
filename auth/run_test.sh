#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=auth_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f auth/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pycodestyle auth"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pylint --rcfile=auth/.pylintrc --fail-under=9 --fail-on=E,C,F ./auth"
echo "<<Pylint tests"

echo "Alembic down revision tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "tools/check_alembic_down_revisions/check_alembic_down_revisions.py --alembic_versions_path auth/auth_server/alembic/versions"
echo "<<Alembic down revision tests"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "cd auth && nosetests --config .noserc"
echo "<<Nose tests"

docker rmi ${TEST_IMAGE}