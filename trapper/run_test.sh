set -e

BUILD_TAG='build'
SERVICES=("trapper_scheduler" "trapper_worker")
for SERVICE in "${SERVICES[@]}"
do
  echo "Started testing ${SERVICE}>>>"

  TEST_IMAGE="${SERVICE}_tests"
  docker build -t ${TEST_IMAGE}:${BUILD_TAG} --build-arg IMAGE=${SERVICE} -f trapper/${SERVICE}/Dockerfile_tests .

  echo "PEP8 tests>>>"
  docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} bash -c "pep8 --max-line-length=120 ."
  echo "<<<PEP8 tests"

  echo "Pylint tests>>>"
  docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} \
        bash -c "cd trapper && pylint --rcfile=.pylintrc ./${SERVICE}; exit \$(( \$? & 3 ))"
  echo "<<<Pylint tests"

  echo "Nose tests>>>"
  docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG}  bash -c "nosetests --config=trapper/.noserc"
  echo "<<Nose tests"

  docker rmi ${TEST_IMAGE}:${BUILD_TAG}

  echo "<<<Finished testing ${SERVICE}"
done