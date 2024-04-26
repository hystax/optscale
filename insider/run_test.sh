#!/usr/bin/env bash
set -e

BUILD_TAG='build'

SERVICES=("insider_api" "insider_scheduler" "insider_worker")
for SERVICE in "${SERVICES[@]}"
do
    echo "Started testing ${SERVICE}>>>"
    TEST_IMAGE="${SERVICE}_tests"
    docker build -t ${TEST_IMAGE}:${BUILD_TAG} --build-arg IMAGE=${SERVICE} -f insider/Dockerfile_tests .

    echo "Pycodestyle tests>>>"
    docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} bash -c \
        "pycodestyle --max-line-length=120 insider"
    echo "<<<Pycodestyle tests"

    echo "Pylint tests>>>"
    docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} bash -c \
        "pylint --rcfile=insider/.pylintrc --fail-under=9 --fail-on=E,F ./insider/${SERVICE}"
    echo "<<<Pylint tests"

    if [[ "${SERVICE}" == "insider_api" ]]; then
        echo "Unit tests>>>"
        docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG}  bash -c \
            "python3 -m unittest discover ./insider/insider_api/tests"
        echo "<<Unit tests"
    fi

    docker rmi ${TEST_IMAGE}:${BUILD_TAG}
    echo "<<<Finished testing ${SERVICE}"
done
