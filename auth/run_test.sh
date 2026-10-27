#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=auth_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f auth/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "uv --project auth run pycodestyle --exclude=.venv auth"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "uv --directory auth run pylint --fail-under=9 --fail-on=E,F auth"
echo "<<Pylint tests"

echo "Alembic down revision tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "uv --project auth run tools/check_alembic_down_revisions/check_alembic_down_revisions.py --alembic_versions_path auth/auth_server/alembic/versions"
echo "<<Alembic down revision tests"

echo "Unit tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "uv --project auth run pytest -n auto auth --disable-warnings"
echo "<<Unit tests"

docker rmi ${TEST_IMAGE}
