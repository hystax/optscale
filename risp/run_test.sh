#!/usr/bin/env bash
set -e

BUILD_TAG='build'

SERVICES=("risp_scheduler" "risp_worker")
for SERVICE in "${SERVICES[@]}"
do
    echo "Started testing ${SERVICE}>>>"
    TEST_IMAGE="${SERVICE}_tests"

    docker build -t ${TEST_IMAGE}:${BUILD_TAG} --build-arg IMAGE=${SERVICE} -f risp/Dockerfile_tests .

    echo "Pycodestyle tests>>>"
    docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} bash -c \
        "pycodestyle --max-line-length=120 risp"
    echo "<<<Pycodestyle tests"

    echo "Pylint tests>>>"
    docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} bash -c \
        "pylint --rcfile=risp/.pylintrc --fail-under=8 --fail-on=E,F ./risp/${SERVICE}"
    echo "<<<Pylint tests"

    if [[ "${SERVICE}" == "risp_worker" ]]; then
        echo "Worker tests>>>"
        docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} \
            bash -c "python3 risp/run_tests.py"
        echo "<<Worker tests"
    fi

    docker rmi ${TEST_IMAGE}:${BUILD_TAG}
done
