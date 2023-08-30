import logging
import requests
import os
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient


LOG = logging.getLogger(__name__)
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}
SUPPORTED_CLOUD_TYPES = {'aws_cnr', 'azure_cnr', 'alibaba_cnr', 'gcp_cnr',
                         'nebius'}


def publish_tasks(config_cl):
    queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit')),
        transport_options=RETRY_POLICY)

    task_exchange = Exchange('trapper-tasks', type='direct')
    cloud_account_map = get_cloud_account_map(config_cl)
    if cloud_account_map:
        with producers[queue_conn].acquire(block=True) as producer:
            for cloud_account_id, _type in cloud_account_map.items():
                producer.publish(
                    {'cloud_account_id': cloud_account_id, 'cloud_type': _type},
                    serializer='json',
                    exchange=task_exchange,
                    declare=[task_exchange],
                    routing_key='traffic-processing',
                    retry=True,
                    retry_policy=RETRY_POLICY
                )
    LOG.info('Published %s tasks', len(cloud_account_map))


def get_cloud_account_map(config_cl):
    rest_cl = RestClient(url=config_cl.restapi_url(), verify=False)
    rest_cl.secret = config_cl.cluster_secret()

    _, response = rest_cl.organization_list()
    cloud_account_map = {}
    for org_id in list(map(lambda x: x['id'], response['organizations'])):
        try:
            _, cloud_accounts = rest_cl.cloud_account_list(org_id)
        except requests.exceptions.HTTPError as ex:
            LOG.error('Failed to publish tasks for org %s: %s', org_id, str(ex))
            continue
        cloud_account_map.update({
            ca['id']: ca['type'] for ca in cloud_accounts['cloud_accounts']
            if ca['type'] in SUPPORTED_CLOUD_TYPES
        })
    return cloud_account_map


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()
    publish_tasks(config_cl)
