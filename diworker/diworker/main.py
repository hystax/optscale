#!/usr/bin/env python
import os
import time

import urllib3
from config_client.client import Client as ConfigClient
from datetime import datetime
from etcd import Lock as EtcdLock
from kombu import Exchange, Queue, Connection as QConnection
from kombu.pools import producers
from kombu.log import get_logger
from kombu.mixins import ConsumerMixin
from kombu.utils.debug import setup_logging
from pymongo import MongoClient
from urllib3.exceptions import InsecureRequestWarning
from rest_api_client.client_v2 import Client as RestClient
from clickhouse_driver import Client as ClickHouseClient

from diworker.importers.base import BaseReportImporter
from diworker.importers.factory import get_importer_class
from diworker.migrator import Migrator

from herald_client.client_v2 import Client as HeraldClient

ACTIVITIES_EXCHANGE_NAME = 'activities-tasks'
ALERT_THRESHOLD = 60 * 60 * 24
EXCHANGE_NAME = 'billing-reports'
QUEUE_NAME = 'report-imports'
task_exchange = Exchange(EXCHANGE_NAME, type='direct')

ARGUMENTS = {'x-max-priority': 10}
task_queue = Queue(
    QUEUE_NAME, task_exchange,
    routing_key=QUEUE_NAME,
    queue_arguments=ARGUMENTS
)

LOG = get_logger(__name__)
ENVIRONMENT_CLOUD_TYPE = 'environment'


class DIWorker(ConsumerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl
        self._rest_cl = None
        self._mongo_cl = None
        self._clickhouse_cl = None

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    @property
    def mongo_cl(self):
        if self._mongo_cl is None:
            mongo_params = self.config_cl.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_cl = MongoClient(mongo_conn_string)
        return self._mongo_cl

    @property
    def clickhouse_cl(self):
        if not self._clickhouse_cl:
            user, password, host, db_name = self.config_cl.clickhouse_params()
            self._clickhouse_cl = ClickHouseClient(
                host=host, password=password, database=db_name, user=user)
        return self._clickhouse_cl

    def publish_activities_task(self, organization_id, object_id, object_type,
                                action, routing_key):
        task = {
            'organization_id': organization_id,
            'object_id': object_id,
            'object_type': object_type,
            'action': action
        }
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self.config_cl.read_branch('/rabbit')))
        task_exchange = Exchange(ACTIVITIES_EXCHANGE_NAME, type='topic')
        with producers[queue_conn].acquire(block=True) as producer:
            producer.publish(
                task,
                serializer='json',
                exchange=task_exchange,
                declare=[task_exchange],
                routing_key=routing_key,
                retry=True
            )

    def get_consumers(self, Consumer, channel):
        return [Consumer(
            queues=[task_queue],
            accept=['json'],
            callbacks=[self.process_task],
            prefetch_count=1,
        )]

    def report_import(self, task):
        report_import_id = task.get('report_import_id')
        if not report_import_id:
            raise Exception('invalid task received: {}'.format(task))

        _, import_dict = self.rest_cl.report_import_get(report_import_id)
        cloud_acc_id = import_dict.get('cloud_account_id')
        is_recalculation = import_dict.get('is_recalculation', False)
        LOG.info('Starting processing for task: %s, purpose %s',
                 task, 'recalculation ' if is_recalculation else 'import')
        self.rest_cl.report_import_update(report_import_id,
                                          {'state': 'in_progress'})

        importer_params = {
            'cloud_account_id': cloud_acc_id,
            'rest_cl': self.rest_cl,
            'config_cl': self.config_cl,
            'mongo_raw': self.mongo_cl.restapi['raw_expenses'],
            'mongo_resources': self.mongo_cl.restapi['resources'],
            'clickhouse_cl': self.clickhouse_cl,
            'import_file': import_dict.get('import_file'),
            'recalculate': is_recalculation}
        importer = None
        ca = None
        try:
            _, ca = self.rest_cl.cloud_account_get(
                importer_params.get('cloud_account_id'))
            organization_id = ca.get('organization_id')
            start_last_import_ts = ca.get('last_import_at', 0)
            cc_type = ca.get('type')
            importer = get_importer_class(cc_type)(**importer_params)
            importer.import_report()
            self.rest_cl.report_import_update(
                report_import_id, {'state': 'completed'})
            if start_last_import_ts == 0 and cc_type != ENVIRONMENT_CLOUD_TYPE:
                all_reports_finished = True
                _, resp = self.rest_cl.cloud_account_list(organization_id)
                for acc in resp['cloud_accounts']:
                    if (acc['type'] != ENVIRONMENT_CLOUD_TYPE and
                            acc['last_import_at'] == 0):
                        all_reports_finished = False
                        break
                if all_reports_finished:
                    self.publish_activities_task(
                        organization_id, organization_id, 'organization',
                        'report_import_passed',
                        'organization.report_import.passed')
        except Exception as exc:
            if hasattr(exc, 'details'):
                # pylint: disable=E1101
                LOG.error('Mongo exception details: %s', exc.details)
            self.rest_cl.report_import_update(
                report_import_id,
                {'state': 'failed', 'state_reason': str(exc)}
            )
            now = int(time.time())
            if not importer:
                importer = BaseReportImporter(**importer_params)
            importer.update_cloud_import_attempt(now, str(exc))
            # TODO: OS-6259: temporary mute service email
            # if ca:
            #     self.send_service_email(ca, now, str(exc))
            raise

    def send_service_email(self, cloud_account, now, reason):
        last_import_at = cloud_account['last_import_at']
        if not last_import_at:
            last_import_at = cloud_account['created_at']
        if now - last_import_at < ALERT_THRESHOLD:
            return

        _, organization = self.rest_cl.organization_get(
            cloud_account['organization_id'])
        recipient = self.config_cl.optscale_error_email_recipient()
        if not recipient:
            return
        title = "Report import failed"
        subject = '[%s] %s' % (self.config_cl.public_ip(), title)
        template_params = {
            'texts': {
                'organization': {
                    'id': organization['id'],
                    'name': organization['name']},
                'cloud_account': {
                    'id': cloud_account['id'],
                    'name': cloud_account['name'],
                    'type': cloud_account['type'],
                    'last_import_at': datetime.fromtimestamp(
                        last_import_at).strftime('%m/%d/%Y %H:%M:%S UTC')
                },
                'reason': reason,
                'title': title
            }}
        HeraldClient(url=self.config_cl.herald_url(),
                     secret=self.config_cl.cluster_secret()).email_send(
            [recipient], subject, template_params=template_params,
            template_type="report_import_failed")

    def process_task(self, body, message):
        try:
            self.report_import(body)
        except Exception as exc:
            LOG.exception('Data import failed: %s', str(exc))
        message.ack()


if __name__ == '__main__':
    urllib3.disable_warnings(InsecureRequestWarning)
    setup_logging(loglevel='INFO', loggers=[''])

    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()
    migrator = Migrator(config_cl, 'restapi', 'diworker/migrations')
    # Use lock to avoid migration problems with several diworkers
    # starting at the same time on cluster
    with EtcdLock(config_cl, 'diworker_migrations'):
        migrator.migrate()
    LOG.info("starting worker")
    conn_str = 'amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit'))
    with QConnection(conn_str) as conn:
        try:
            worker = DIWorker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
