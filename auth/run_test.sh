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

echo "Unit tests with coverage>>>"
docker run -i --rm -v $(pwd)/coverage_html:/coverage_html ${TEST_IMAGE} \
    bash -c "coverage run --source=auth -m unittest discover ./auth/auth_server/tests && coverage html -d /coverage_html"
echo "<<Unit tests with coverage"

docker rmi ${TEST_IMAGE}
