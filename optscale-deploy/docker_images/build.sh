#!/usr/bin/env bash
set -ex

source vars.sh

DEFAULT_WORKDIR=.

TARGET_TAG=${CI_PIPELINE_ID:-'build'}
OUTPUT="$1:${TARGET_TAG}"
WORKDIR="${2:-$DEFAULT_WORKDIR}"
BUILD_URL=${BUILD_URL:-$CI_PIPELINE_URL}

pushd "$1"
docker build -t ${OUTPUT} -f Dockerfile --label commit=$(git rev-parse HEAD) --label build_url=${BUILD_URL:-'none'} ${WORKDIR}
popd
