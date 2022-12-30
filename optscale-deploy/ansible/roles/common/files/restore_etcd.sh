#!/usr/bin/env bash

set -e

FIRST_POD_CONF="etcd_first_pod.yaml"
CLUSTER_CONF="etcd_cluster.yaml"
TOOLS_PYTHON_PATH="/optscale/tools/venv_for_tools/bin/python"
RESTORE_EDITOR="/optscale/tools/restore_editor.py"

for pod_name in $(kubectl get pod -l etcd_cluster=etcd | awk '/etcd/ {print $1}'); do
  if kubectl get pod "$pod_name" -o yaml | grep -q "\-\-initial-cluster-state=new"
  then
    first_pod_name="$pod_name"
  fi
done
echo "Saving first etcd pod $first_pod_name to use as a seed member"
kubectl get pod "$first_pod_name" -o yaml >"$FIRST_POD_CONF"

echo "Saving etcd cluster resource for restore"
kubectl get etcdclusters.etcd.database.coreos.com etcd -o yaml >"$CLUSTER_CONF"

echo "Deleting existing etcd cluster"
kubectl delete etcdclusters.etcd.database.coreos.com etcd

echo "Waiting for etcd pods removal"
until ! kubectl get pod -l etcd_cluster=etcd | grep -q 'etcd'; do
  sleep 2
done

echo "Fixing cluster resource for restore"
$TOOLS_PYTHON_PATH "$RESTORE_EDITOR" "$CLUSTER_CONF" "cluster-paused"

echo "Creating new paused cluster in Running state"
kubectl apply -f "$CLUSTER_CONF"

cluster_id=$(kubectl get etcdclusters.etcd.database.coreos.com etcd -o yaml | awk '/uid/ {print $2}')
echo "New cluster id: $cluster_id"

for pv in $(kubectl get pv | awk '/etcd/ {print $1}'); do
  if kubectl get pv -o yaml "$pv" | grep -q "$(hostname)";
  then
    volume_on_current_host="$pv"
  fi
done
echo "Removing claimRef for the pv $volume_on_current_host on the current host"
kubectl patch pv "$volume_on_current_host" --type merge --patch '{"spec": {"claimRef": null}}'

echo "Fixin pod resource for restore"
$TOOLS_PYTHON_PATH "$RESTORE_EDITOR" "$FIRST_POD_CONF" "pod" --cluster-id "$cluster_id"

echo "Starting first pod"
kubectl apply -f "$FIRST_POD_CONF"

echo "Waiting for pod to be running"
until kubectl get pod -l etcd_cluster=etcd | grep -q '1/1'; do
  sleep 2
done

pod_name=$(kubectl get pod -l etcd_cluster=etcd | awk '/etcd/ {print $1}')
member_id=$(kubectl exec -ti "$pod_name" -- etcdctl member list | awk -F ":" '{print $1}')
echo "Updating peerUrl for pod"
kubectl exec -ti "$pod_name" -- etcdctl member update "$member_id" "http://$pod_name.etcd.default.svc:2380"

echo "Removing claimRefs for other PVs"
for pv in $(kubectl get pv | awk '/etcd/ {print $1}'); do
  if ! kubectl get pv -o yaml "$pv" | grep -q "$(hostname)";
  then
    kubectl patch pv "$pv" --type merge --patch '{"spec": {"claimRef": null}}'
  fi
done

echo "Fixing cluster resource for unpause"
$TOOLS_PYTHON_PATH "$RESTORE_EDITOR" "$CLUSTER_CONF" "cluster-unpause"

echo "Unpausing cluster"
kubectl apply -f "$CLUSTER_CONF"
