#!/usr/bin/env bash
set -euo pipefail

# Build the unified OptScale application image and first-party data-plane images
# from the repository root.
#
# Usage:
#   ./build-unified.sh              # tags using .env/default compose values
#   ./build-unified.sh latest       # tags as hystax/optscale_app:latest, etc.
#   ./build-unified.sh v1.0 hystax  # tags as hystax/optscale_app:v1.0, etc.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

env_value() {
    local name="$1"
    local default="$2"

    if [[ -f "$ENV_FILE" ]]; then
        local value
        value="$(awk -F= -v name="$name" '$1 == name { value = substr($0, length(name) + 2) } END { if (value != "") printf "%s", value }' "$ENV_FILE")"
        if [[ -n "$value" ]]; then
            printf "%s" "$value"
            return
        fi
    fi

    printf "%s" "$default"
}

TAG="${1:-$(env_value "OPTSCALE_VERSION" "latest")}"
COMPANY="${2:-$(env_value "COMPANY" "hystax")}"
FLAGS=""

if [[ "${NO_CACHE:-}" == "true" ]]; then
    FLAGS="--no-cache"
fi

build_image() {
    local image_name="$1"
    local dockerfile="$2"
    local full_tag

    if [[ -n "$COMPANY" ]]; then
        full_tag="${COMPANY}/${image_name}:${TAG}"
    else
        full_tag="${image_name}:${TAG}"
    fi

    echo ""
    echo "Building ${image_name}: ${full_tag}"
    docker build \
        $FLAGS \
        -f "${REPO_ROOT}/${dockerfile}" \
        -t "${full_tag}" \
        "${REPO_ROOT}"
}

echo "Build context: ${REPO_ROOT}"

build_image "etcd" "docker_images/etcd/Dockerfile"
build_image "mariadb" "docker_images/mariadb/Dockerfile"
build_image "mongo" "docker_images/mongo/Dockerfile"
build_image "redis" "docker_images/redis/Dockerfile"
build_image "influxdb" "docker_images/influxdb/Dockerfile"
build_image "optscale_app" "docker_images/optscale_app/Dockerfile"

echo ""
echo "Done. Built unified OptScale and first-party data-plane images."
