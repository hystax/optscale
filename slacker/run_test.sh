#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=slacker_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f slacker/Dockerfile_tests .

echo "PEP8 tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pep8 --max-line-length=120 ./slacker"
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
docker run -i --rm ${TEST_IMAGE} bash -c "pylint --rcfile=slacker/.pylintrc ./slacker; exit \$(( \$? & 3 ))"
echo "<<Pylint tests"

echo "Nose tests>>>"
docker run -i --rm ${TEST_IMAGE} \
    bash -c "nosetests -w slacker/slacker_server/tests --config .noserc 2>&1; exit \$(( \${PIPESTATUS[0]} & 3 ))"
echo "<<Nose tests"

#docker rmi ${TEST_IMAGE}
