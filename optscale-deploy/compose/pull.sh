#!/usr/bin/env bash
set -euo pipefail

# Pull all Docker Compose images one at a time to avoid Docker Hub rate limits.
# Usage:
#   ./pull.sh              # pull all services sequentially
#   ./pull.sh --parallel   # fall back to default parallel pull

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ "${1:-}" == "--parallel" ]]; then
    echo "Pulling all images in parallel..."
    docker compose pull
    exit 0
fi

SERVICES=$(docker compose config --services 2>/dev/null)
TOTAL=$(echo "$SERVICES" | wc -l | tr -d ' ')
CURRENT=0

echo "Pulling $TOTAL service images sequentially..."
for svc in $SERVICES; do
    CURRENT=$((CURRENT + 1))
    IMAGE=$(docker compose config --format json 2>/dev/null \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['services']['$svc']['image'])" 2>/dev/null || true)
    echo "[$CURRENT/$TOTAL] $svc ($IMAGE)"
    docker compose pull --quiet "$svc" 2>/dev/null || {
        echo "  Warning: pull failed for $svc — may use a locally built image"
    }
done
echo "All images pulled."
