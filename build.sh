#!/usr/bin/env bash

# ./build.sh [component] [tag] [-r registry] [-u username] [-p password]
# leave registry empty if default registry [docker.io] used

# Initialize default values
COMPANY="hystax"
REGISTRY=""
LOGIN=""
PASSWORD=""
COMPONENT=""
INPUT_TAG=""


# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -r) REGISTRY="$2"; shift ;;
        -u) LOGIN="$2"; shift ;;
        -p) PASSWORD="$2"; shift ;;
        *)
            # Check if COMPONENT is empty
            if [[ -z "$COMPONENT" ]]; then
                COMPONENT="$1"
            else
                # If COMPONENT is already set, then set BUILD_TAG
                INPUT_TAG="$1"
            fi
            ;;
    esac
    shift
done

COMMIT_ID=$(git rev-parse --verify HEAD)

use_registry() {
  if [[ -n "${LOGIN}" && -n "${PASSWORD}" ]]; then
    true
  else
    false
fi
}

BUILD_TAG=${INPUT_TAG:-'local'}
FIND_CMD="find . -mindepth 2 -maxdepth 3 -print | grep Dockerfile | grep -vE '(test|.j2)'"
FIND_CMD="${FIND_CMD} | grep $COMPONENT/"


if use_registry; then
  echo "docker login"
  docker login ${REGISTRY} -u "${LOGIN}" -p "${PASSWORD}"
fi

retag() {
if use_registry; then
     if [ -z $3 ]; then
       if docker pull "${COMPANY}/$1:${COMMIT_ID}"; then
         docker tag "${COMPANY}/$1:${COMMIT_ID}" "$1:$2"
         return 0
       else
         return 1
       fi
    else
      if docker pull "$3/$1:${COMMIT_ID}"; then
        docker tag "$3/$1:${COMMIT_ID}" "$1:$2"
        return 0
      else
        return 1
      fi
    fi
fi
return 1
}

push_image () {
   echo "Pushing $1:$2"
    if [ -z $3 ]; then
      docker tag "$1:$2" "$COMPANY/$1:$2"
      docker tag "$1:$2" "$COMPANY/$1:$COMMIT_ID"
      docker push "$COMPANY/$1:$2"
      docker push "$COMPANY/$1:$COMMIT_ID"
    else
      docker tag "$1:$2" "$3/$1:$2"
      docker tag "$1:$2" "$3/$1:$COMMIT_ID"
      docker push "$3/$1:$2"
      docker push "$3/$1:$COMMIT_ID"
    fi
}

for DOCKERFILE in $(eval ${FIND_CMD} | xargs)
do
    COMPONENT=$(echo "${DOCKERFILE}" | awk -F '/' '{print $(NF-1)}')
    retag  $COMPONENT $BUILD_TAG $REGISTRY
    if [ "$?" -eq 0 ]; then
      echo "component $COMPONENT re-tagged $COMMIT_ID -> $BUILD_TAG"
    else
      echo "Building image for ${COMPONENT}, build tag: ${BUILD_TAG}"
      docker build -t ${COMPONENT}:${BUILD_TAG} -f ${DOCKERFILE} .
    fi

    if use_registry; then
      push_image $COMPONENT $BUILD_TAG $REGISTRY
    fi
done
