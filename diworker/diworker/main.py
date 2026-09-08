#!/usr/bin/env python
import os
import time
import logging

import urllib3
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Thread
from etcd import Lock as EtcdLock
from kombu import Exchange, Queue, Connection as QConnection
from kombu.pools import producers
from kombu.mixins import ConsumerMixin
from pymongo import MongoClient
from urllib3.exceptions import InsecureRequestWarning
import clickhouse_connect

from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from tools.optscale_time.optscale_time import (
    startday, utcfromtimestamp, utcnow_timestamp
)
from tools.optscale_telemetry import OpenTelemetryConfig

from diworker.diworker.importers.base import BaseReportImporter
from diworker.diworker.importers.factory import get_importer_class
from diworker.diworker.migrator import Migrator

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

LOG = logging.getLogger(__name__)
ENVIRONMENT_CLOUD_TYPE = 'environment'

ACTIVE_IMPORT_THRESHOLD = 1800
HEARTBEAT_INTERVAL = 300
DEFAULT_MAX_WORKERS = 4
DEFAULT_MAX_TENANT_WORKERS = 1
MIGRATIONS_READY_FILE = '/tmp/diworker-migrations-ready'


def _is_rate_limit_exc(exc):
    if getattr(exc, 'status_code', None) == 429:
        return True
    msg = str(exc).lower()
    return '429' in msg or 'toomanyrequests' in msg or 'too many requests' in msg


class DIWorker(ConsumerMixin):
    def __init__(self, connection, rabbitmq_conn_str, diworker_settings,
                 config_params):
        self.connection = connection
        self.rabbitmq_conn_str = rabbitmq_conn_str
        self.diworker_settings = diworker_settings
        self.config_cl_params = config_params
        self.active_report_import_ids = set()
        self.active_reports_lock = Lock()
        self.running = True
        self.thread = Thread(
            target=self.heartbeat, args=(self.config_cl_params,))
        self.thread.start()
        self.executor = ThreadPoolExecutor(
            max_workers=int(
                self.diworker_settings.get(
                    'max_report_imports_workers',
                    DEFAULT_MAX_WORKERS
                )
            )
        )

    def heartbeat(self, config_params):
        config_cl = self.get_config_cl(config_params)
        rest_cl = self.get_rest_cl(config_cl)
        while self.running:
            with self.active_reports_lock:
                report_import_ids = list(self.active_report_import_ids)
            for report_import_id in report_import_ids:
                try:
                    rest_cl.report_import_update(report_import_id, {})
                except Exception as e:
                    LOG.warning("Heartbeat update failed for %s: %s", report_import_id, e)
            time.sleep(HEARTBEAT_INTERVAL)
        rest_cl.close()

    @staticmethod
    def get_config_cl(config_params):
        return ConfigClient(**config_params)

    @staticmethod
    def get_rest_cl(config_cl):
        url = config_cl.restapi_url()
        secret = config_cl.cluster_secret()
        return RestClient(url=url, verify=False, secret=secret)

    @staticmethod
    def get_mongo_cl(config_cl):
        mongo_params = config_cl.mongo_params()
        return MongoClient(mongo_params[0])

    @staticmethod
    def get_clickhouse_cl(config_cl):
        user, password, host, db_name, port, secure = (
            config_cl.clickhouse_params())
        return clickhouse_connect.get_client(
            host=host, password=password, database=db_name, user=user,
            port=port, secure=secure)

    def publish_activities_task(self, organization_id, object_id, object_type,
                                action, routing_key, meta=None):
        task = {
            'organization_id': organization_id,
            'object_id': object_id,
            'object_type': object_type,
            'action': action,
            'meta': meta
        }
        queue_conn = QConnection(self.rabbitmq_conn_str)
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
            prefetch_count=int(
                self.diworker_settings.get(
                    'max_report_imports_workers',
                    DEFAULT_MAX_WORKERS
                )
            ),
        )]

    def report_import(self, task, config_cl, rest_cl, mongo_cl, clickhouse_cl):
        report_import_id = task.get('report_import_id')
        if not report_import_id:
            raise Exception('invalid task received: {}'.format(task))

        _, import_dict = rest_cl.report_import_get(report_import_id)
        if import_dict.get('state') == 'in_progress':
            # task that is not acked too long and is redelivered by rabbitmq
            updated_at = import_dict.get('updated_at')
            threshold = int(
                self.diworker_settings.get('active_import_threshold_secs')
                or ACTIVE_IMPORT_THRESHOLD)
            if updated_at is None or updated_at >= utcnow_timestamp() - threshold:
                LOG.warning('Import %s is already in progress, skipping '
                            'redelivered task', report_import_id)
                return True
            LOG.warning('Import %s is in progress, but its last heartbeat is '
                        'at %s, will process the task', report_import_id,
                        updated_at)

        with self.active_reports_lock:
            self.active_report_import_ids.add(report_import_id)

        cloud_acc_id = import_dict.get('cloud_account_id')
        _, resp = rest_cl.report_import_list(cloud_acc_id, show_active=True)
        imports = list(filter(
            lambda x: x['id'] != report_import_id, resp['report_imports']))
        if imports:
            reason = 'Import cancelled due another import: %s' % imports[0]['id']
            rest_cl.report_import_update(
                report_import_id,
                {'state': 'failed', 'state_reason': reason}
            )
            return
        is_recalculation = import_dict.get('is_recalculation', False)
        LOG.info('Starting processing for task: %s, purpose %s',
                 task, 'recalculation ' if is_recalculation else 'import')
        rest_cl.report_import_update(report_import_id, {'state': 'in_progress'})
        importer_params = {
            'cloud_account_id': cloud_acc_id,
            'rest_cl': rest_cl,
            'config_cl': config_cl,
            'mongo_raw': mongo_cl.restapi['raw_expenses'],
            'mongo_resources': mongo_cl.restapi['resources'],
            'mongo_report_files': mongo_cl.restapi['report_import_files'],
            'clickhouse_cl': clickhouse_cl,
            'import_file': import_dict.get('import_file'),
            'recalculate': is_recalculation,
            'max_tenant_concurrent': int(self.diworker_settings.get(
                'max_tenant_import_workers', DEFAULT_MAX_TENANT_WORKERS)),
            'csv_rewrite_days': self.diworker_settings.get('csv_rewrite_days')
        }
        importer = None
        ca = None
        previous_attempt_ts = 0
        try:
            _, ca = rest_cl.cloud_account_get(
                importer_params.get('cloud_account_id'))
            organization_id = ca.get('organization_id')
            _, org = rest_cl.organization_get(organization_id)
            if org.get('disabled'):
                reason = ('Import cancelled due to disabled '
                          'organization: %s') % report_import_id
                rest_cl.report_import_update(
                    report_import_id,
                    {'state': 'failed', 'state_reason': reason}
                )
                return
            start_last_import_ts = ca.get('last_import_at', 0)
            previous_attempt_ts = ca.get('last_import_attempt_at', 0)
            cc_type = ca.get('type')
            export_scheme = ca['config'].get('expense_import_scheme')
            importer = get_importer_class(cc_type, export_scheme)(
                **importer_params)
            importer.import_report()
            rest_cl.report_import_update(
                report_import_id, {'state': 'completed'})
            if start_last_import_ts == 0 and cc_type != ENVIRONMENT_CLOUD_TYPE:
                all_reports_finished = True
                _, resp = rest_cl.cloud_account_list(organization_id)
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
            reason = str(exc)
            rest_cl.report_import_update(
                report_import_id,
                {'state': 'failed', 'state_reason': reason}
            )
            now = int(time.time())
            if not importer:
                importer = BaseReportImporter(**importer_params)
            importer.update_cloud_import_attempt(now, reason)
            self.send_report_failed_email(
                ca, previous_attempt_ts, now,
                is_throttled=_is_rate_limit_exc(exc))
            raise

    def send_report_failed_email(self, cloud_account, previous_attempt_ts,
                                 now, is_throttled=False):
        last_import_at = cloud_account['last_import_at']
        if not last_import_at:
            last_import_at = cloud_account['created_at']
        if now - last_import_at < ALERT_THRESHOLD:
            return
        if last_import_at < previous_attempt_ts:
            # previous import failed too
            if startday(utcfromtimestamp(previous_attempt_ts)) == startday(
                    utcfromtimestamp(now)):
                # email already sent today during previous report import fails
                return
        action = ('report_import_throttled' if is_throttled
                  else 'report_import_failed')
        self.publish_activities_task(
            cloud_account['organization_id'], cloud_account['id'],
            'cloud_account', action,
            'organization.report_import.failed')

    def process_task(self, body, message):
        self.executor.submit(self._process_task, body, message)

    def _process_task(self, body, message):
        config_cl = self.get_config_cl(self.config_cl_params)
        rest_cl = self.get_rest_cl(config_cl)
        mongo_cl = self.get_mongo_cl(config_cl)
        clickhouse_cl = self.get_clickhouse_cl(config_cl)
        skipped = False
        try:
            skipped = self.report_import(
                body, config_cl=config_cl, rest_cl=rest_cl,
                mongo_cl=mongo_cl, clickhouse_cl=clickhouse_cl)
        except Exception as exc:
            LOG.exception('Data import failed: %s', str(exc))
        finally:
            mongo_cl.close()
            clickhouse_cl.close()
            rest_cl.close()
            if not skipped:
                with self.active_reports_lock:
                    self.active_report_import_ids.discard(
                        body.get('report_import_id'))
        message.ack()


if __name__ == '__main__':
    urllib3.disable_warnings(InsecureRequestWarning)
    logging.basicConfig(
        level=logging.INFO,
        format='[%(threadName)s] %(levelname)s: %(message)s'
    )

    config_cl_params = {
        'host': os.environ.get('HX_ETCD_HOST'),
        'port': int(os.environ.get('HX_ETCD_PORT'))
    }
    config_cl = ConfigClient(**config_cl_params)
    config_cl.wait_configured()
    migrator = Migrator(config_cl, 'restapi', 'diworker/diworker/migrations')
    # Use lock to avoid migration problems with several diworkers
    # starting at the same time on cluster
    with EtcdLock(config_cl, 'diworker_migrations'):
        migrator.migrate()
    with open(MIGRATIONS_READY_FILE, 'w') as ready_file:
        ready_file.write('ready\n')
    LOG.info("starting worker")
    conn_str = 'amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit'))
    dw_settings = config_cl.diworker_settings()
    with QConnection(conn_str) as conn:
        config = OpenTelemetryConfig(
            service_name=os.getenv("OTEL_SERVICE_NAME", "diworker"),
            service_version=os.getenv("OTEL_SERVICE_VERSION", "local"),
            otel_config=config_cl.read_branch("/opentelemetry"),
            service_config=config_cl.read_branch("diworker/opentelemetry"),
        )
        config.setup_open_telemetry()
        try:
            worker = DIWorker(conn, conn_str, dw_settings, config_cl_params)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.executor.shutdown(wait=True)
            worker.thread.join()
            LOG.info("Shutdown worker")
