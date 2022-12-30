import argparse
import yaml

PVC = """---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {0}
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
"""

ETCD_START_CMD = ''


def basic_cleanup(spec):
    del spec['status']
    del spec['metadata']['resourceVersion']
    del spec['metadata']['creationTimestamp']
    del spec['metadata']['selfLink']
    del spec['metadata']['uid']
    return spec


def edit_pod_spec(spec, cluster_id):
    spec = basic_cleanup(spec)
    del spec['spec']['nodeName']
    spec['metadata']['ownerReferences'][0]['uid'] = cluster_id

    container = spec['spec']['containers'][0]
    token = None
    for line in container['command']:
        if 'initial-cluster-token' in line:
            _, token = line.split('=')

    if not token:
        raise Exception('cluster token not found')

    init_container_spec = {
        'command': [
            '/bin/sh', '-c',
            'mv /var/etcd/data /var/etcd/data_old && etcdctl backup --data-dir '
            '/var/etcd/data_old --backup-dir /var/etcd/data && '
            'ret=$(timeout -s SIGTERM -t 30 /usr/local/bin/etcd '
            '--data-dir=/var/etcd/data --force-new-cluster); '
            'echo -e "$ret\nrestore finished"',
        ],
        'image': spec['spec']['containers'][0]['image'],
        'imagePullPolicy': 'Never',
        'name': 'restore',
        'resources': {},
        'volumeMounts': [{'mountPath': '/var/etcd', 'name': 'etcd-data'}],
    }

    # removing restore init containers if this pod already been used for restore
    for i, container in enumerate(spec['spec']['initContainers'].copy()):
        if container['name'] == 'restore':
            spec['spec']['initContainers'].pop(i)
    spec['spec']['initContainers'].append(init_container_spec)
    return PVC.format(spec['metadata']['name']) + yaml.dump(spec)


def edit_cluster_spec_initial(spec_dict):
    spec = basic_cleanup(spec_dict)
    spec['spec']['paused'] = True
    spec['status'] = {'phase': 'Running'}
    return yaml.dump(spec)


def edit_cluster_spec_unpause(spec):
    spec['spec']['paused'] = False
    return yaml.dump(spec)


def main(input_path, file_type, cluster_id=None):
    with open(input_path) as f:
        input_dict = yaml.load(f)

    if file_type == 'pod':
        if not cluster_id:
            raise Exception('cluster_id is required for pod file type')
        result = edit_pod_spec(input_dict, cluster_id)
    elif file_type == 'cluster-paused':
        result = edit_cluster_spec_initial(input_dict)
    elif file_type == 'cluster-unpause':
        result = edit_cluster_spec_unpause(input_dict)
    else:
        raise Exception('invalid usage')

    with open(input_path, 'w') as f_out:
        f_out.write(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('yaml_path', help='path to etcd pod config')
    parser.add_argument('file_type', help='type of the file you need to edit',
                        choices=['pod', 'cluster-paused', 'cluster-unpause'])
    parser.add_argument('--cluster-id', help='new etcd cluster id')
    args = parser.parse_args()
    main(args.yaml_path, args.file_type, args.cluster_id)
