#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=rest_api_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f rest_api/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pep8 --max-line-length=120 ./rest_api/"
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c \
    "cd rest_api && pylint --rcfile=.pylintrc ./"
echo "<<Pylint tests"

echo "Unit tests>>>"
docker run -i --rm -v $PWD/rest_api/.clickhouse:/usr/src/app/rest_api/.clickhouse ${TEST_IMAGE} \
    bash -c "./rest_api/prepare_clickhouse_local.sh docker && python3 rest_api/run_tests.py; exit \$(( \${PIPESTATUS[0]} & 3 ))"
echo "<<Unit tests"
docker rmi ${TEST_IMAGE}
