#!/usr/bin/env bash

# Golden image pre-requirements:
# /optscale/startup/old_ip must be created with proper ip inside (ip of the instance used for image creation)
# /etc/rc.local must execute this script (which must be executable)
# kubelet and docker services must be disabled (not started on boot)

set -x

STARTUP_PATH="/optscale/startup"
OLD_IP_PATH="$STARTUP_PATH/old_ip"
K8S_PATH="/etc/kubernetes"
USER_K8S_CONFIG="/home/user/.kube/config"

default_iface="$(awk '$2 == 00000000 { print $1 }' /proc/net/route)"

current_ip="$(ip addr show dev "$default_iface" | awk '$1 == "inet" { sub("/.*", "", $2); print $2; exit }')"

if [[ "$current_ip" == "" ]]; then
    echo "ERROR: detected empty IP address"
    exit 1
fi

old_ip="$(cat ${OLD_IP_PATH})"

if [[ "$current_ip" == "$old_ip" ]]; then
    service docker start
    service kubelet start
    exit 0
fi

declare -a k8s_files=("scheduler.conf" "manifests/kube-apiserver.yaml" "manifests/etcd.yaml" "admin.conf" "kubelet.conf" "controller-manager.conf")

for f in "${k8s_files[@]}"; do
    sed -i "s/$old_ip/$current_ip/g" "$K8S_PATH/$f"
done
sed -i "s/$old_ip/$current_ip/g" $USER_K8S_CONFIG

for f in apiserver.crt apiserver.key; do
    rm "$K8S_PATH/pki/$f"
done

kube_version=$(kubectl version --client -o json | python -c "import sys,json;version=json.load(sys.stdin);print version['clientVersion']['gitVersion']")
kubeadm init phase certs apiserver --kubernetes-version "${kube_version}"

cp "$K8S_PATH/admin.conf" "/home/engineer/.kube/config"
chmod 600 "/home/engineer/.kube/config"

service docker start
service kubelet start

export KUBECONFIG="$K8S_PATH/admin.conf"

until kubectl get pod; do
    echo "waiting for apiserver startup"
    sleep 10
done

config_map_path="$STARTUP_PATH/proxy-configmap.yaml"

until kubectl -n kube-system get configmap kube-proxy -o yaml > "$config_map_path"; do sleep 1; done
sed -i "s/$old_ip/$current_ip/g" "$config_map_path"

until kubectl apply -f "$config_map_path"; do
    echo "waiting for applying kube-proxy configmap"
    sleep 10
done

kubectl -n kube-system delete pod "$(kubectl -n kube-system get pod | awk '/proxy/ {print $1}')"
echo "$current_ip" > "$OLD_IP_PATH"
