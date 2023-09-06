#!/usr/bin/env bash

set -e

INPUT_TAG=$2
BUILD_TAG=${INPUT_TAG:-'build'}

FIND_CMD="find . -print | grep Dockerfile | grep -v test | grep -v Dockerfile.j2"

case $# in
    0)
    ;;
    1|2)
    FIND_CMD="${FIND_CMD} | grep $1/"
    ;;
    *)
    echo "invalid arguments number, use ./build.sh [component] [build tag]"
    exit 1
esac

DOCKERFILES=( $(eval ${FIND_CMD}) )
for DOCKERFILE in "${DOCKERFILES[@]}"
do
    COMPONENT=$(echo "${DOCKERFILE}" | awk -F '/' '{print $(NF-1)}')
    echo "Building image for ${COMPONENT}, build tag: ${BUILD_TAG}"
    docker build -t ${COMPONENT}:${BUILD_TAG} -f ${DOCKERFILE} .
done
