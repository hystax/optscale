#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=slacker_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f slacker/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pycodestyle --max-line-length=120 slacker"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "pylint --rcfile=slacker/.pylintrc --fail-under=9 --fail-on=E,F ./slacker"
echo "<<Pylint tests"

echo "Alembic down revision tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "tools/check_alembic_down_revisions/check_alembic_down_revisions.py --alembic_versions_path slacker/slacker_server/alembic/versions"
echo "<<Alembic down revision tests"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "nosetests -w slacker/slacker_server/tests --config .noserc 2>&1; exit \$(( \${PIPESTATUS[0]} & 3 ))"
echo "<<Nose tests"

docker rmi ${TEST_IMAGE}
