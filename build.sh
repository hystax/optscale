#!/usr/bin/env bash
# Usage: ./build.sh [component] [legacy-tag] | [component ... --tag tag] [--push] [-r registry] [-u username] [-p password] [--no-cache] [--use-nerdctl]

set -e

COMPANY="hystax"
REGISTRY=""
LOGIN=""
PASSWORD=""
COMPONENTS_LIST=()
POSITIONAL_ARGS=()
INPUT_TAG=""
TAG_PROVIDED=false
NO_CACHE=false
USE_NERDCTL=false
BUILD_TOOL="docker"
PUSH=false

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --tag|-r|-u|-p)
            if [[ "$#" -lt 2 ]]; then
                echo "Error: $1 requires a value" >&2
                exit 2
            fi
            case "$1" in
                --tag) INPUT_TAG="$2"; TAG_PROVIDED=true ;;
                -r) REGISTRY="$2" ;;
                -u) LOGIN="$2" ;;
                -p) PASSWORD="$2" ;;
            esac
            shift
            ;;
        --push) PUSH=true ;;
        --no-cache) NO_CACHE=true ;;
        --use-nerdctl) USE_NERDCTL=true ;;
        *) POSITIONAL_ARGS+=("$1") ;;
    esac
    shift
done

if [[ "$TAG_PROVIDED" != true && ${#POSITIONAL_ARGS[@]} -eq 2 ]]; then
    COMPONENTS_LIST=("${POSITIONAL_ARGS[0]}")
    INPUT_TAG="${POSITIONAL_ARGS[1]}"
else
    COMPONENTS_LIST=("${POSITIONAL_ARGS[@]}")
fi

BUILD_TAG=${INPUT_TAG:-local}

if [[ "$USE_NERDCTL" == true ]]; then
    BUILD_TOOL="nerdctl"
fi

BUILD_FLAGS=()
if [[ "$NO_CACHE" == true ]]; then
    BUILD_FLAGS+=(--no-cache)
fi

if [[ -n "$LOGIN" && -n "$PASSWORD" ]]; then
    PUSH=true
fi

if [[ "$PUSH" == true ]]; then
    if [[ -z "$LOGIN" || -z "$PASSWORD" ]]; then
        echo "Error: --push requires -u (username) and -p (password)" >&2
        exit 1
    fi
    if [[ -n "$REGISTRY" ]]; then
        "$BUILD_TOOL" login "$REGISTRY" -u "$LOGIN" -p "$PASSWORD"
    else
        "$BUILD_TOOL" login -u "$LOGIN" -p "$PASSWORD"
    fi
fi

discover_dockerfiles() {
    find . -mindepth 2 -maxdepth 3 -print | grep Dockerfile | grep -vE '(test|.j2)'
}

push_image() {
    local component=$1
    local target

    if [[ -n "$REGISTRY" ]]; then
        target="$REGISTRY/$component:$BUILD_TAG"
    else
        target="$COMPANY/$component:$BUILD_TAG"
    fi

    "$BUILD_TOOL" tag "$component:$BUILD_TAG" "$target"
    "$BUILD_TOOL" push "$target"
}

build_and_push_component() {
    local dockerfile=$1
    local component=$2

    echo "[$component] Starting build with tag $BUILD_TAG"
    "$BUILD_TOOL" build "${BUILD_FLAGS[@]}" --platform linux/amd64 \
        -t "$component:$BUILD_TAG" -f "$dockerfile" .

    if [[ "$PUSH" == true ]]; then
        echo "[$component] Pushing image"
        push_image "$component"
    fi
}

pids=()
components=()
while IFS= read -r dockerfile; do
    component=${dockerfile%/*}
    component=${component##*/}

    if [[ ${#COMPONENTS_LIST[@]} -gt 0 ]]; then
        selected=false
        for requested in "${COMPONENTS_LIST[@]}"; do
            if [[ "$component" == "$requested" ]]; then
                selected=true
                break
            fi
        done
        [[ "$selected" == true ]] || continue
    fi

    echo "Queuing $component with tag $BUILD_TAG"
    build_and_push_component "$dockerfile" "$component" &
    pids+=("$!")
    components+=("$component")
done < <(discover_dockerfiles)

if [[ ${#pids[@]} -eq 0 ]]; then
    echo "Error: no matching Dockerfiles found" >&2
    exit 1
fi

failed=false
failed_components=()
for i in "${!pids[@]}"; do
    if wait "${pids[$i]}"; then
        echo "[${components[$i]}] Complete"
    else
        status=$?
        echo "[${components[$i]}] Failed (exit code $status)" >&2
        failed=true
        failed_components+=("${components[$i]}")
    fi
done

if [[ "$failed" == true ]]; then
    echo "Failed components: ${failed_components[*]}" >&2
    exit 1
fi
