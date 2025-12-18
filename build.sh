#!/usr/bin/env bash
# ./build.sh [component] [--tag tag] [--push] [-r registry] [-u username] [-p password] [--no-cache] [--use-nerdctl]
# leave registry empty if default registry [docker.io] used

set -ex

# Initialize default values
COMPANY="hystax"
REGISTRY=""
LOGIN=""
PASSWORD=""
COMPONENT=""
INPUT_TAG=""
FLAGS=""
NO_CACHE=false
USE_NERDCTL=false
BUILD_TOOL="docker"
PUSH=false

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --tag) INPUT_TAG="$2"; shift ;;
        --push) PUSH=true ;;
        -r) REGISTRY="$2"; shift ;;
        -u) LOGIN="$2"; shift ;;
        -p) PASSWORD="$2"; shift ;;
        --no-cache) NO_CACHE=true ;;
        --use-nerdctl) USE_NERDCTL=true ;;
        *)
            # Set COMPONENT if not already set
            if [[ -z "$COMPONENT" ]]; then
                COMPONENT="$1"
            fi
            ;;
    esac
    shift
done

# Set build tool based on flag
if [[ "$USE_NERDCTL" == true ]]; then
    BUILD_TOOL="nerdctl"
fi

# Set --no-cache flag
if [[ "$NO_CACHE" == true ]]; then
    FLAGS="--no-cache"
fi

BUILD_TAG=${INPUT_TAG:-'local'}
FIND_CMD="find . -mindepth 2 -maxdepth 3 -print | grep Dockerfile | grep -vE '(test|.j2)'"
FIND_CMD="${FIND_CMD} | grep $COMPONENT/"

# Login to registry if push is enabled
if [[ "$PUSH" == true ]]; then
  if [[ -z "${LOGIN}" || -z "${PASSWORD}" ]]; then
    echo "Error: --push requires -u (username) and -p (password)"
    exit 1
  fi
  echo "$BUILD_TOOL login"
  $BUILD_TOOL login -u "${LOGIN}" -p "${PASSWORD}"
fi

push_image () {
   echo "Pushing $1:$2"
    if [ -z $3 ]; then
      $BUILD_TOOL tag "$1:$2" "$COMPANY/$1:$2"
      $BUILD_TOOL push "$COMPANY/$1:$2"
    else
      $BUILD_TOOL tag "$1:$2" "$3/$1:$2"
      $BUILD_TOOL push "$3/$1:$2"
    fi
}

for DOCKERFILE in $(eval ${FIND_CMD} | xargs)
do
    COMPONENT=$(echo "${DOCKERFILE}" | awk -F '/' '{print $(NF-1)}')
    echo "Building image for ${COMPONENT}, build tag: ${BUILD_TAG}"
    $BUILD_TOOL build $FLAGS -t ${COMPONENT}:${BUILD_TAG} -f ${DOCKERFILE} . --platform linux/amd64

    if [[ "$PUSH" == true ]]; then
      push_image $COMPONENT $BUILD_TAG $REGISTRY
    fi
done
