#!/usr/bin/env bash
set -ex

if [[ $# -ne 1 ]]; then
    echo "Tag specified image with commit tag and push into registry"
    echo "Usage: $0 <base_image>"
    echo "Example: $0 busybox:build"
    exit 1
fi

source vars.sh

image_name=$(echo $1 | awk -F ":" '{print $1}')
base_image=$1
commit=${CI_COMMIT_SHA:-$(git rev-parse HEAD)}
strategy=${PUSH_STRATEGY:-'skip-existing'}

if [[ "$strategy" == "skip-existing" ]]; then
    echo "Using skip-existing strategy"
    if check_image_exists ${image_name} ${commit}; then
        echo "Image $image_name:$commit already present in registry"
        exit 0
    fi
    echo "Image not found, pushing it"
fi

docker tag ${base_image} "$DREGISTRY/$image_name:${commit}"
docker push "$DREGISTRY/$image_name:${commit}"
