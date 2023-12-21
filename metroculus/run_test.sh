#!/usr/bin/env bash
set -e

BUILD_TAG='build'

SERVICES=("metroculus_api" "metroculus_scheduler" "metroculus_worker")
for SERVICE in "${SERVICES[@]}"
do
    echo "Started testing ${SERVICE}>>>"
    TEST_IMAGE="${SERVICE}_tests"
    docker build -t ${TEST_IMAGE}:${BUILD_TAG} --build-arg IMAGE=${SERVICE} -f metroculus/Dockerfile_tests .

    echo "Pycodestyle tests>>>"
    docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} bash -c \
        "pycodestyle --max-line-length=120 metroculus"
    echo "<<<Pycodestyle tests"

    echo "Pylint tests>>>"
    docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} bash -c \
        "pylint --rcfile=metroculus/.pylintrc --fail-under=9 --fail-on=E,F ./metroculus/${SERVICE}"
    echo "<<<Pylint tests"

    if [[ "${SERVICE}" == "metroculus_api" ]]; then
        echo "Nose tests>>>"
        docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} bash -c \
            "nosetests --config metroculus/.noserc ./metroculus/${SERVICE}"
        echo "<<Nose tests"
    fi

    docker rmi ${TEST_IMAGE}:${BUILD_TAG}
    echo "<<<Finished testing ${SERVICE}"
done
