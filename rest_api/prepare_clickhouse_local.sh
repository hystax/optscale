#!/bin/bash
set -e

CLICKHOUSE_MAC_URL=macos
CLICKHOUSE_LINUX_URL=amd64
BINARIES=($CLICKHOUSE_LINUX_URL)
OS_URL=$CLICKHOUSE_LINUX_URL
CLICKHOUSE_ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

if [[ "$OSTYPE" == "darwin"* ]]; then
    BINARIES+=($CLICKHOUSE_MAC_URL)
    OS_URL=$CLICKHOUSE_MAC_URL
fi
for os in ${BINARIES[@]};
do
    CLICKHOUSE_FOLDER_PATH=$CLICKHOUSE_ROOT_DIR/.clickhouse/$os
    CLICKHOUSE_BIN_PATH=$CLICKHOUSE_FOLDER_PATH/clickhouse
    if [[ ! -e "$CLICKHOUSE_BIN_PATH" ]]; then
        mkdir -p $CLICKHOUSE_FOLDER_PATH
        tar_path=$CLICKHOUSE_BIN_PATH.tar.gz
        cat $CLICKHOUSE_ROOT_DIR/rest_api_server/tests/binaries/clickhouse/$os/clickhouse.?? > $tar_path
        tar -xzvf $tar_path -C $CLICKHOUSE_FOLDER_PATH
        rm -rf $tar_path
        chmod +x $CLICKHOUSE_BIN_PATH
    fi
done
ln -f $CLICKHOUSE_ROOT_DIR/.clickhouse/$OS_URL/clickhouse $CLICKHOUSE_ROOT_DIR/.clickhouse/clickhouse
