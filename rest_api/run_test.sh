#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=rest_api_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f rest_api/Dockerfile_tests .

echo "Pycodestyle tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pycodestyle --max-line-length=120 rest_api"
echo "<<<Pycodestyle tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "pylint --rcfile=rest_api/.pylintrc --fail-under=9 --fail-on=E,F ./rest_api"
echo "<<Pylint tests"

echo "Alembic down revision tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "tools/check_alembic_down_revisions/check_alembic_down_revisions.py --alembic_versions_path rest_api/rest_api_server/alembic/versions --ignore_ids 3273906c73ac"
echo "<<Alembic down revision tests"

echo "Unit tests>>>"
docker run -i --rm -v $PWD/rest_api/.clickhouse:/usr/src/app/rest_api/.clickhouse ${TEST_IMAGE} \
    bash -c "./rest_api/prepare_clickhouse_local.sh docker && python3 rest_api/run_tests.py; exit \$(( \${PIPESTATUS[0]} & 3 ))"
echo "<<Unit tests"
docker rmi ${TEST_IMAGE}
