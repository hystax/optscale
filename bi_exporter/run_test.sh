#!/usr/bin/env bash

BUILD_TAG='build'
TEST_IMAGE=bi_exporter_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f bi_exporter/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pep8 --ignore=E701 --max-line-length=120 ."
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pylint --rcfile=bi_exporter/.pylintrc ./bi_exporter"
echo "<<Pylint tests"

echo "Worker tests>>>"
docker run -i --rm ${TEST_IMAGE}  bash -c "python3 bi_exporter/run_tests.py"
echo "<<Worker tests"

docker rmi ${TEST_IMAGE}