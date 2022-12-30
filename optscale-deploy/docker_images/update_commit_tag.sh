#!/usr/bin/env bash

set -ex

source vars.sh

COMMIT=${CI_COMMIT_SHA}
img_name="$DREGISTRY/$1"

if check_image_exists $(basename $img_name) ${COMMIT}; then
    echo "Image for current commit already exists, skipping retag"
    exit 0
else
    echo "Looking for latest image to retag"
    for hash in $(git log --pretty=format:%H ${COMMIT}); do
        if check_image_exists $(basename $img_name) ${hash}; then
            echo "Using image from commit $hash to retag"
            docker pull "$img_name:$hash"
            docker tag "$img_name:$hash" "$img_name:$COMMIT"
            docker push "$img_name:$COMMIT"
            exit 0
        fi
    done
    echo "Unable to find image for retag"
    exit 1
fi
