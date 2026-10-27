#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=herald_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f herald/Dockerfile_tests .

echo "Linting>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "uv --project herald run ruff format --config herald/pyproject.toml --check --diff herald/"
docker run -i --rm ${TEST_IMAGE} bash -c "uv --project herald run ruff check --config herald/pyproject.toml herald/"
echo "<<<Linting"

echo "Alembic down revision tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "uv --project herald run tools/check_alembic_down_revisions/check_alembic_down_revisions.py --alembic_versions_path herald/herald_server/alembic/versions"
echo "<<Alembic down revision tests"

echo "Unit tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "uv --project herald run pytest herald/herald_server/tests herald/modules/tests/"
echo "<<Unit tests"

docker rmi ${TEST_IMAGE}
