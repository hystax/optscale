#!/bin/bash
set -e
CLICKHOUSE_ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
mkdir -p $CLICKHOUSE_ROOT_DIR/.clickhouse
ln -sf /usr/bin/clickhouse $CLICKHOUSE_ROOT_DIR/.clickhouse/clickhouse