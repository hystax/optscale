#!/usr/bin/env python
import argparse
import logging
import os

import docker
import yaml
from kubernetes import client as k8s_client, config as k8s_config

LOG = logging.getLogger(__name__)
LABELS = ['build_url', 'commit']
CONFIGMAP_NAME = 'optscale-version'
NAMESPACE = 'default'


class ClusterInfo(object):
    def __init__(self, config, host, no_urls):
        self.host = host
        self.config = config
        k8s_config.load_kube_config(self.config)
        self.core_api = k8s_client.CoreV1Api()
        self.docker_host = host
        self.no_urls = no_urls
        self._docker_cl = None

    @property
    def docker_cl(self):
        if self._docker_cl is None:
            if self.host is None:
                self._docker_cl = docker.from_env()
            else:
                if self.host.find(':') == -1:
                    self.host = self.host + ':2376'
                self._docker_cl = docker.DockerClient(
                    base_url='tcp://%s' % self.host)
        return self._docker_cl

    def get_cluster_info(self):
        version_map_data = self.core_api.read_namespaced_config_map(
            name=CONFIGMAP_NAME, namespace=NAMESPACE).data
        version_map = yaml.load(version_map_data['component_versions.yaml'])
        if self.no_urls:
            return version_map

        for image in version_map['images'].copy():
            try:
                d_image = self.docker_cl.images.get('{0}:local'.format(image))
            except docker.errors.ImageNotFound:
                LOG.warning('image %s not found', image)
                del version_map['images'][image]
                continue

            labels = d_image.labels or {}
            version_map['images'][image] = {
                'commit_tag': version_map['images'][image],
                'build_url': labels.get('build_url'),
            }
        return version_map


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Get OptScale cluster info')
    parser.add_argument(
        '--config',
        default=os.path.join(os.environ.get('HOME'), '.kube/config'),
        help='Path to k8s config file',
    )
    parser.add_argument(
        '--no-urls',
        action='store_true',
        help='Only show content of the OptScale version configmap, don\'t print '
             'build urls for images',
    )
    parser.add_argument(
        '--host',
        help='Ip of the host on which docker images must be examined',
        default=None,
    )
    arguments = parser.parse_args()

    info = ClusterInfo(arguments.config, arguments.host, arguments.no_urls)
    result = info.get_cluster_info()
    print(yaml.dump(result, default_flow_style=False))
