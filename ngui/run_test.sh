#!/usr/bin/env bash
set -e

BUILD_TAG='build'
TEST_IMAGE=ngui_tests:${BUILD_TAG}

docker build -t ${TEST_IMAGE} --build-arg BUILDTAG=${BUILD_TAG} -f ngui/Dockerfile_tests .

echo "Linter>>>"
docker run -i --rm ${TEST_IMAGE} sh -c "cd /usr/src/app/ui && pnpm lint:check"
echo "<<<Linter"

echo "Prettier>>>"
docker run -i --rm ${TEST_IMAGE} sh -c "cd /usr/src/app/ui && pnpm prettier:check"
echo "<<Prettier"

# tests are currently disabled

docker rmi ${TEST_IMAGE}
