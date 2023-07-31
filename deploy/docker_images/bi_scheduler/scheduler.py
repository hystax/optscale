import logging
import os
from datetime import datetime, timedelta
from functools import cached_property
from typing import Dict, List

from kombu import Connection as QConnection, Exchange
from kombu.pools import producers

from config_client.client import Client as ConfigClient
from rest_api_client.client_v2 import Client as RestClient

DEFAULT_RUN_PERIOD = 86400
TASK_WAIT_TIMEOUT = 3 * 86400

LOG = logging.getLogger(__name__)


RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}

EXCHANGE_NAME = 'bi-exporter'
QUEUE_NAME = 'bi-exporter'

PROCESSING_STATUSES = ['QUEUED', 'RUNNING']


class BIScheduler:
    config_cl: ConfigClient

    def __init__(self, config_cl: ConfigClient) -> None:
        self.config_cl = config_cl
        self.now = datetime.utcnow()

    @cached_property
    def rest_cl(self) -> RestClient:
        rest_cl = RestClient(url=self.config_cl.restapi_url())
        rest_cl.secret = self.config_cl.cluster_secret()
        return rest_cl

    @property
    def queue_conn(self) -> QConnection:
        return QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self.config_cl.read_branch('/rabbit')), transport_options=RETRY_POLICY)

    def _publish_tasks(self, org_bi_ids, next_run):
        task_exchange = Exchange(EXCHANGE_NAME, type='direct')
        with producers[self.queue_conn].acquire(block=True) as producer:
            for org_bi_id in org_bi_ids:
                try:
                    self.rest_cl.bi_update(org_bi_id, {'status': 'QUEUED',
                                                       'next_run': next_run})
                    producer.publish(
                        {'organization_bi_id': org_bi_id},
                        serializer='json',
                        exchange=task_exchange,
                        declare=[task_exchange],
                        routing_key=QUEUE_NAME,
                        retry=True,
                        retry_policy=RETRY_POLICY
                    )
                    LOG.info(f'Task published for org_bi {org_bi_id}')
                except Exception as ex:
                    LOG.exception(f"Failed to publish task for "
                                  f"organization_bi: {org_bi_id}", exc_info=ex)

    def publish_tasks(self, org_bi_ids: List[str]) -> None:
        run_period = int(self.config_cl.bi_settings().get('exporter_run_period',
                                                          DEFAULT_RUN_PERIOD))
        next_run = int((self.now + timedelta(seconds=run_period)).timestamp())
        self._publish_tasks(org_bi_ids, next_run)

    def get_org_bi_ids(self) -> List[str]:
        task_wait_timeout = int(
            self.config_cl.bi_settings().get('task_wait_timeout',
                                             TASK_WAIT_TIMEOUT))
        _, response = self.rest_cl.bi_list()

        def ready(bi: Dict, task_wait_timeout: int) -> bool:
            if bi['next_run'] > int(self.now.timestamp()):
                return False

            if (bi['status'] in PROCESSING_STATUSES and
                    bi['next_run'] + task_wait_timeout > int(self.now.timestamp())):
                return False
            return True

        return [bi['id'] for bi in response['organization_bis']
                if ready(bi, task_wait_timeout)]

    def run(self) -> None:
        ids = self.get_org_bi_ids()
        LOG.info(f"Publishing tasks for the following BIs: {ids}")
        self.publish_tasks(ids)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()

    scheduler = BIScheduler(config_cl)
    scheduler.run()
