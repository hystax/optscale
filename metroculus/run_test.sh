#!/usr/bin/env bash
set -e

BUILD_TAG='build'

SERVICES=("metroculus_api" "metroculus_scheduler" "metroculus_worker")
for SERVICE in "${SERVICES[@]}"
do
    echo "Started testing ${SERVICE}>>>"
    TEST_IMAGE="${SERVICE}_tests"
    docker build -t ${TEST_IMAGE}:${BUILD_TAG} --build-arg IMAGE=${SERVICE} -f metroculus/Dockerfile_tests .

    echo "PEP8 tests>>>"
    docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} bash -c "pep8 --max-line-length=120 ."
    echo "<<<PEP8 tests"

    echo "Pylint tests>>>"
    docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} \
        bash -c "pylint --rcfile=metroculus/.pylintrc ./metroculus/${SERVICE}; exit \$(( \$? & 3 ))"
    echo "<<<Pylint tests"

    if [[ "${SERVICE}" == "metroculus_api" ]]; then
        echo "Nose tests>>>"
        docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} bash -c "nosetests --config metroculus/.noserc"
        echo "<<Nose tests"
    fi

    docker rmi ${TEST_IMAGE}:${BUILD_TAG}
    echo "<<<Finished testing ${SERVICE}"
done
