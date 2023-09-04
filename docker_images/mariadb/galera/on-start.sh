#! /bin/bash

GALERA_CONF="${GALERA_CONF:-"/etc/mysql/conf.d/galera.cnf"}"

if ! [ -f "${GALERA_CONF}" ]; then
    cp /opt/galera/galera.cnf "${GALERA_CONF}"
fi

function join {
    local IFS="$1"; shift; echo "$*";
}

HOSTNAME=$(hostname)
# Parse out cluster name, formatted as: petset_name-index
IFS='-' read -ra ADDR <<< "$(hostname)"
CLUSTER_NAME="acura_galera"

while read -ra LINE; do
    if [[ "${LINE}" == *"${HOSTNAME}"* ]]; then
        MY_NAME=$LINE
    else
        PEERS=("${PEERS[@]}" $LINE)
    fi
done

if [ "${#PEERS[@]}" = 0 ]; then
    export WSREP_CLUSTER_ADDRESS=""
else
    export WSREP_CLUSTER_ADDRESS=$(join , "${PEERS[@]}")
fi
sed -i -e "s|^wsrep_node_address[[:space:]]*=.*$|wsrep_node_address=${MY_NAME}|" "${GALERA_CONF}"
sed -i -e "s|^wsrep_cluster_name[[:space:]]*=.*$|wsrep_cluster_name=${CLUSTER_NAME}|" "${GALERA_CONF}"
sed -i -e "s|^wsrep_cluster_address[[:space:]]*=.*$|wsrep_cluster_address=gcomm://${WSREP_CLUSTER_ADDRESS}|" "${GALERA_CONF}"

# don't need a restart, we're just writing the conf in case there's an
# unexpected restart on the node.

if [ -n "$WSREP_CLUSTER_ADDRESS" ]; then
    mkdir -p "$DATADIR/mysql"
    echo "*** [Galera] Joining cluster: $WSREP_CLUSTER_ADDRESS"
else
    echo "*** [Galera] Starting new cluster!"
fi

