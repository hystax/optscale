import logging
import requests
import os
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient

LOG = logging.getLogger(__name__)
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}
SUPPORTED_CLOUD_TYPES = {'aws_cnr', 'azure_cnr', 'alibaba_cnr',
                         'kubernetes_cnr', 'gcp_cnr', 'nebius'}


def publish_tasks(config_cl):
    queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit')),
        transport_options=RETRY_POLICY)

    task_exchange = Exchange('metroculus-tasks', type='direct')
    cloud_account_ids = get_cloud_account_ids(config_cl)
    if cloud_account_ids:
        with producers[queue_conn].acquire(block=True) as producer:
            for cloud_account_id in cloud_account_ids:
                producer.publish(
                    {'cloud_account_id': cloud_account_id},
                    serializer='json',
                    exchange=task_exchange,
                    declare=[task_exchange],
                    routing_key='metroculus-task',
                    retry=True,
                    retry_policy=RETRY_POLICY
                )
                LOG.info('Task published for cloud_account_id %s',
                         cloud_account_id)


def get_cloud_account_ids(config_cl):
    rest_cl = RestClient(url=config_cl.restapi_url(), verify=False)
    rest_cl.secret = config_cl.cluster_secret()

    _, response = rest_cl.organization_list()
    cloud_account_ids = []
    for org_id in list(map(lambda x: x['id'], response['organizations'])):
        try:
            _, cloud_accounts = rest_cl.cloud_account_list(org_id)
        except requests.exceptions.HTTPError as ex:
            LOG.error(
                'Failed to publish tasks for org %s: %s',
                org_id,
                str(ex))
            continue
        cloud_account_ids.extend([
            ca['id'] for ca in cloud_accounts['cloud_accounts']
            if ca['type'] in SUPPORTED_CLOUD_TYPES
        ])
    return cloud_account_ids


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = int(os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT))

    config_cl = ConfigClient(host=etcd_host, port=etcd_port)
    config_cl.wait_configured()
    publish_tasks(config_cl)
