import os
import logging
import requests
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient


LOG = logging.getLogger(__name__)
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}
SUPPORTED_CLOUD_TYPES = {'aws_cnr'}
TASK_EXCHANGE = Exchange('risp-tasks', type='direct')


def get_cloud_accounts(config_cl):
    cloud_accounts_list = []
    rest_cl = RestClient(url=config_cl.restapi_url(), verify=False)
    rest_cl.secret = config_cl.cluster_secret()
    _, response = rest_cl.organization_list()
    for org in response['organizations']:
        try:
            _, cloud_accounts = rest_cl.cloud_account_list(org['id'])
            cloud_accounts_list.extend(
                [x['id'] for x in cloud_accounts['cloud_accounts']
                 if x['type'] in SUPPORTED_CLOUD_TYPES])
        except requests.exceptions.HTTPError as ex:
            LOG.error('Failed to publish tasks for org %s: %s',
                      org['id'], str(ex))
            continue
    return cloud_accounts_list


def publish_tasks(config_cl):
    queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit')),
        transport_options=RETRY_POLICY)
    cloud_accounts = get_cloud_accounts(config_cl)
    if cloud_accounts:
        with producers[queue_conn].acquire(block=True) as producer:
            for cloud_account_id in cloud_accounts:
                producer.publish(
                    {'cloud_account_id': cloud_account_id},
                    serializer='json',
                    exchange=TASK_EXCHANGE,
                    declare=[TASK_EXCHANGE],
                    routing_key='risp-task',
                    retry=True,
                    retry_policy=RETRY_POLICY
                )
    LOG.info('Published %s tasks', len(cloud_accounts))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()
    publish_tasks(config_cl)
