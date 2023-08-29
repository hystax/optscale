#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=diproxy_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f diproxy/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pep8 --max-line-length=80 ./diproxy"
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "pylint --rcfile=diproxy/.pylintrc ./diproxy; exit \$(( \$? & 3 ))"
echo "<<Pylint tests"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE}  bash -c "nosetests --config diproxy/.noserc"
echo "<<Nose tests"

docker rmi ${TEST_IMAGE}
