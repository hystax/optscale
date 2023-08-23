import argparse
import os
from datetime import datetime
from typing import Optional

from kombu import Exchange, Queue, Connection
from kombu.log import get_logger
from kombu.utils.debug import setup_logging
from kombu.mixins import ConsumerMixin

from optscale_client.rest_api_client.client_v2 import Client as RestClient
from optscale_client.config_client.client import Client as ConfigClient

from bi_exporter.bumblebi.exporter.exporter_factory import ExporterFactory

EXCHANGE_NAME = 'bi-exporter'
QUEUE_NAME = 'bi-exporter'
task_exchange = Exchange(EXCHANGE_NAME, type='direct')
task_queue = Queue(QUEUE_NAME, task_exchange, routing_key=QUEUE_NAME)
LOG = get_logger(__name__)
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80


class Worker(ConsumerMixin):
    config_cl: ConfigClient
    _rest_cl: Optional[RestClient]

    def __init__(self, connection, config_client) -> None:
        self.connection = connection
        self.config_cl = config_client
        self._rest_cl = None

    @property
    def rest_cl(self) -> RestClient:
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[task_queue], accept=['json'],
                         callbacks=[self.process_task], prefetch_count=3)]

    @staticmethod
    def _now_ts():
        return int(datetime.utcnow().timestamp())

    @property
    def valid_states_for_export(self):
        return ['QUEUED']

    def _running(self, bi_id: str) -> None:
        body = {
            "status": "RUNNING",
            "last_run": self._now_ts(),
        }

        self.rest_cl.bi_update(bi_id, body)
        LOG.info("Status updated to RUNNING for BI %s", bi_id)

    def _success(self, bi_id: str) -> None:
        body = {
            "status": "SUCCESS",
            "last_completed": self._now_ts(),
        }

        self.rest_cl.bi_update(bi_id, body)
        LOG.info("Status updated to SUCCESS for BI %s", bi_id)

    def _fail(self, bi_id: str, error_msg: str) -> None:
        body = {
            "status": "FAILED",
            "last_status_error": error_msg,
        }
        try:
            self.rest_cl.bi_update(bi_id, body)
            LOG.info("Status updated to FAILED for BI %s", bi_id)
        except Exception as ex:
            LOG.warning(
                "Not able to update status to FAILED for BI %s: %s", bi_id, ex)

    def process_task(self, body, message):
        bi_id = body.get('organization_bi_id')
        if not bi_id:
            LOG.warning(
                'Invalid task body. organization_bi_id is missing: %s', body)
            message.reject()
            return

        try:
            _, bi = self.rest_cl.bi_get(bi_id)
            if bi['status'] not in self.valid_states_for_export:
                raise Exception(
                    'BI %s in wrong status for export: %s',
                    bi["id"], bi["status"])
            bi_credentials = bi['meta']

            exporter = ExporterFactory.get(
                bi['type'], self.config_cl, bi_credentials)
            self._running(bi_id)
            exporter.export(bi_id)

            LOG.info("Successful export for BI %s", bi_id)
            self._success(bi_id)

        except Exception as ex:
            LOG.warning("Failed export for %s: %s", bi_id, str(ex))
            self._fail(bi_id, str(ex))
        finally:
            message.ack()


def main(config_client: ConfigClient) -> None:
    conn_str = 'amqp://{user}:{pass}@{host}:{port}'.format(
        **config_client.read_branch('/rabbit'))
    with Connection(conn_str) as conn:
        try:
            worker = Worker(conn, config_client)
            LOG.info('Starting to consume...')
            worker.run()
        except KeyboardInterrupt:
            LOG.info('Interrupted by user')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process export of data to external')
    parser.add_argument('--log_lvl', type=str, default="INFO")
    args = parser.parse_args()

    setup_logging(loglevel=args.log_lvl, loggers=[''])

    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST),
        port=int(os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)),
    )

    config_cl.wait_configured()
    main(config_cl)
