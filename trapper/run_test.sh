set -e

BUILD_TAG='build'
SERVICES=("trapper_scheduler" "trapper_worker")
for SERVICE in "${SERVICES[@]}"
do
  echo "Started testing ${SERVICE}>>>"

  TEST_IMAGE="${SERVICE}_tests"
  docker build -t ${TEST_IMAGE}:${BUILD_TAG} --build-arg IMAGE=${SERVICE} -f trapper/${SERVICE}/Dockerfile_tests .

  echo "Pycodestyle tests>>>"
  docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} bash -c \
      "pycodestyle --max-line-length=120 trapper"
  echo "<<<Pycodestyle tests"

  echo "Pylint tests>>>"
  docker run -i --rm ${TEST_IMAGE}:${BUILD_TAG} \
      bash -c "cd trapper && pylint --rcfile=.pylintrc --fail-under=9 --fail-on=E,F ./${SERVICE}"
  echo "<<<Pylint tests"

  docker rmi ${TEST_IMAGE}:${BUILD_TAG}

  echo "<<<Finished testing ${SERVICE}"
done
