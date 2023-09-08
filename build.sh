#!/usr/bin/env bash

set -e

INPUT_TAG=$2
BUILD_TAG=${INPUT_TAG:-'build'}
REGISTRY=$3
LOGIN=$4
PASS=$5

FIND_CMD="find . -mindepth 2 -maxdepth 3 -print | grep Dockerfile | grep -vE '(test|.j2)'"

case $# in
    0)
    ;;
    1|2|3|4|5)
    FIND_CMD="${FIND_CMD} | grep $1/"
    ;;
    *)
    echo "invalid arguments number, use ./build.sh [component] [build tag]"
    exit 1
esac

if [ ! -z "$LOGIN" ]; then
  echo "docker login"
  docker login $REGISTRY -u "${LOGIN}" -p "${PASS}"
  fi

for DOCKERFILE in $(eval ${FIND_CMD} | xargs)
do
    COMPONENT=$(echo "${DOCKERFILE}" | awk -F '/' '{print $(NF-1)}')
    echo "Building image for ${COMPONENT}, build tag: ${BUILD_TAG}"
    docker build -t ${COMPONENT}:${BUILD_TAG} -f ${DOCKERFILE} .
    if [ ! -z "$REGISTRY" ]; then
      echo "Pushing ${COMPONENT} to ${REGISTRY}"

      if [ $REGISTRY == "dr-dev.hystax.com" ]; then
        docker tag "${COMPONENT}:${BUILD_TAG}" "${REGISTRY}/${COMPONENT}:${BUILD_TAG}"
        docker push "${REGISTRY}/${COMPONENT}:${BUILD_TAG}"
      else
        docker tag "${COMPONENT}:${BUILD_TAG}" "hystax/${COMPONENT}:${BUILD_TAG}"
        docker push "hystax/${COMPONENT}:${BUILD_TAG}"
      fi
    fi
done
