#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=rest_api_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f rest_api/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "uv --project rest_api run pycodestyle --max-line-length=120 --exclude=.venv rest_api"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "uv --directory rest_api run pylint --fail-under=8.5 --fail-on=E,F rest_api"
echo "<<Pylint tests"

echo "Alembic down revision tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "uv --project rest_api run tools/check_alembic_down_revisions/check_alembic_down_revisions.py --alembic_versions_path rest_api/rest_api_server/alembic/versions --ignore_ids 3273906c73ac"
echo "<<Alembic down revision tests"

echo "Unit tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "uv --project rest_api run pytest -n auto rest_api --maxprocesses 3 --dist no --disable-warnings"
echo "<<Unit tests"
docker rmi ${TEST_IMAGE}

