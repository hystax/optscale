#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=risp_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f risp/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pep8 --max-line-length=120 ./risp"
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pylint --rcfile=risp/.pylintrc ./risp; exit \$(( \$? & 3 ))"
echo "<<Pylint tests"

echo "Worker tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "python3 risp/run_tests.py"
echo "<<Worker tests"

docker rmi ${TEST_IMAGE}