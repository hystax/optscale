#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=katara_service_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f katara/katara_service/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pycodestyle katara"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pylint --rcfile=katara/katara_service/.pylintrc --fail-under=9 --fail-on=E,C,F ./katara"

echo "Alembic down revision tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "tools/check_alembic_down_revisions/check_alembic_down_revisions.py --alembic_versions_path katara/katara_service/alembic/versions"
echo "<<Alembic down revision tests"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "cd katara/katara_service && nosetests --config .noserc"
echo "<<Nose tests"

docker rmi ${TEST_IMAGE}
