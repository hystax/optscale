import logging
import os
from datetime import datetime
from functools import cached_property
import pytz
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers
from requests import HTTPError

from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient

from docker_images.power_schedule.utils import is_schedule_outdated

LOG = logging.getLogger(__name__)


RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}

EXCHANGE_NAME = 'power-schedule'
QUEUE_NAME = 'power-schedule'


class PowerScheduler:
    config_cl: ConfigClient

    def __init__(self, config_client: ConfigClient) -> None:
        self.config_cl = config_client

    @cached_property
    def rest_cl(self) -> RestClient:
        rest_cl = RestClient(url=self.config_cl.restapi_url(),
                             secret=self.config_cl.cluster_secret())
        return rest_cl

    @property
    def queue_conn(self) -> QConnection:
        return QConnection(
            'amqp://{user}:{pass}@{host}:{port}'.format(
                **self.config_cl.read_branch('/rabbit')),
            transport_options=RETRY_POLICY)

    def publish_tasks(self, power_schedule_ids):
        task_exchange = Exchange(EXCHANGE_NAME, type='direct')
        with producers[self.queue_conn].acquire(block=True) as producer:
            for ps_id in power_schedule_ids:
                try:
                    producer.publish(
                        {'power_schedule_id': ps_id},
                        serializer='json',
                        exchange=task_exchange,
                        declare=[task_exchange],
                        routing_key=QUEUE_NAME,
                        retry=True,
                        retry_policy=RETRY_POLICY
                    )
                    LOG.info('Task published for power schedule %s', ps_id)
                except HTTPError as exc:
                    LOG.error("Failed to publish task for "
                              "power schedule %s: %s", ps_id, str(exc))

    def run(self) -> None:
        ps_ids = set()
        _, orgs = self.rest_cl.organization_list({'is_demo': False})
        for org in orgs['organizations']:
            try:
                _, ps_list = self.rest_cl.power_schedule_list(org['id'])
            except HTTPError as exc:
                LOG.exception("Failed to get power schedules for "
                              "organization %s: %s", org['id'], str(exc))
                continue
            for schedule in ps_list['power_schedules']:
                if not schedule['enabled']:
                    continue
                if not is_schedule_outdated(schedule):
                    ps_ids.add(schedule['id'])
        if ps_ids:
            self.publish_tasks(ps_ids)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()

    scheduler = PowerScheduler(config_cl)
    scheduler.run()
