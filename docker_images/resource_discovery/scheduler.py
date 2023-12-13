import logging
import os
import requests
from datetime import datetime
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers
from collections import defaultdict

from tools.cloud_adapter.cloud import Cloud
from tools.cloud_adapter.model import RES_MODEL_MAP
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient

LOG = logging.getLogger(__name__)
IGNORED_CLOUD_TYPES = ['environment']
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}


def publish_tasks(tasks_map):
    queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit')),
        transport_options=RETRY_POLICY)
    task_exchange = Exchange('resource-discovery', type='direct')
    with producers[queue_conn].acquire(block=True) as producer:
        for tasks in tasks_map.values():
            for task in tasks:
                cloud_account_id, resource_type = task
                producer.publish(
                    {'cloud_account_id': cloud_account_id,
                     'resource_type': resource_type},
                    serializer='json',
                    exchange=task_exchange,
                    declare=[task_exchange],
                    routing_key='discovery',
                    retry=True,
                    retry_policy=RETRY_POLICY
                )


def _update_discovery_info(rest_cl, cloud_account_type, cloud_account_id,
                           discovery_infos):
    """
    Checks and dynamically updates discovery_info for cloud account according
    to the cloud account type. Deletes discovery_info not supported for cloud
    type, creates discovery_info if they are missing for cloud_account_id but
    supported according to the cloud account type

    :param rest_cl: (obj) instance of rest_api_client.client_v2.Client
    :param cloud_account_type: (str) type of cloud account
    :param cloud_account_id: (str) id of cloud account
    :param discovery_infos: (dict) discovery_info for cloud account (response
    of discovery_info list API)

    :return: updated discovery_info dictionary
    """
    existing_r_types = set(x['resource_type']
                           for x in discovery_infos['discovery_info'])
    adapter = Cloud.get_adapter({'type': cloud_account_type})
    discovery_calls = adapter.discovery_calls_map()
    cloud_supported_r_types = set(
        rt for rt, model in RES_MODEL_MAP.items()
        if model in discovery_calls.keys())

    r_types_to_create = cloud_supported_r_types - existing_r_types
    if r_types_to_create:
        create_payload = {'discovery_info': [{
            'resource_type': r_type
        } for r_type in r_types_to_create]}
        rest_cl.discovery_info_create_bulk(cloud_account_id, create_payload)
        LOG.info('Created discovery info for resource types %s cloud '
                 'account %s' % (r_types_to_create, cloud_account_id))

    r_types_to_delete = existing_r_types - cloud_supported_r_types
    if r_types_to_delete:
        d_info_ids = [x['id'] for x in discovery_infos['discovery_info']
                      if x['resource_type'] in r_types_to_delete]
        rest_cl.discovery_info_delete_bulk(cloud_account_id, d_info_ids)
        LOG.info('Deleted discovery info id %s for cloud account %s' % (
            d_info_ids, cloud_account_id))

    if r_types_to_delete or r_types_to_create:
        _, discovery_infos = rest_cl.discovery_info_list(cloud_account_id)
    return discovery_infos


def process(config_cl):
    rest_cl = RestClient(url=config_cl.restapi_url(), verify=False,
                         secret=config_cl.cluster_secret())
    _, response = rest_cl.organization_list({'with_connected_accounts': True})
    tasks_map = defaultdict(list)
    now = int(datetime.utcnow().timestamp())
    _, _, _, observe_timeout = config_cl.resource_discovery_params()
    for organization in response['organizations']:
        try:
            _, ca_resp = rest_cl.cloud_account_list(organization['id'])
        except requests.exceptions.HTTPError as ex:
            LOG.error('Failed to publish tasks for org %s: %s',
                      organization['id'], str(ex))
            continue
        for ca in ca_resp['cloud_accounts']:
            if ca['type'] in IGNORED_CLOUD_TYPES:
                continue
            try:
                _, r = rest_cl.discovery_info_list(ca['id'])
                discovery_infos = _update_discovery_info(rest_cl, ca['type'],
                                                         ca['id'], r)
                for di_info in discovery_infos['discovery_info']:
                    resource_type = di_info['resource_type']
                    if (max(
                        [di_info['last_discovery_at'], di_info['last_error_at']]
                    ) < di_info['observe_time'] and
                            di_info['enabled'] is True and
                            di_info['observe_time'] > (now - observe_timeout)):
                        LOG.info('skip %s for %s', resource_type, ca['id'])
                        continue
                    if di_info['enabled']:
                        rest_cl.discovery_info_update(
                            di_info['id'], {
                                'observe_time': int(
                                    datetime.utcnow().timestamp())})
                        tasks_map[organization['id']].append(
                            (ca['id'], di_info['resource_type']))
            except requests.exceptions.HTTPError as ex:
                LOG.error(
                    'Failed to publish tasks for cloud account %s: %s',
                    ca['id'], str(ex))
                continue
    return tasks_map


def main(config_cl):
    start_time = datetime.utcnow()
    tasks_map = process(config_cl)
    exec_time = (datetime.utcnow() - start_time).total_seconds()
    if tasks_map:
        publish_tasks(tasks_map)
        LOG.info('Published %s tasks (%s seconds) for orgs: %s' % (
            sum(len(x) for x in tasks_map.values()), exec_time,
            list(tasks_map.keys())))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()
    main(config_cl)
