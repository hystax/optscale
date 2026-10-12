import logging
import os
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Thread

import clickhouse_connect
import urllib3
from etcd import Lock as EtcdLock
from kombu import Exchange, Queue, Connection as QConnection
from kombu.mixins import ConsumerMixin
from kombu.pools import producers
from pymongo import MongoClient
from urllib3.exceptions import InsecureRequestWarning

from diworker.diworker.migrator import Migrator
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from tools.optscale_telemetry import OpenTelemetryConfig
from tools.optscale_time.optscale_time import startday, utcfromtimestamp

LOG = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 300
DEFAULT_MAX_WORKERS = 4
DEFAULT_MAX_TENANT_WORKERS = 1
ALERT_THRESHOLD = 60 * 60 * 24

EXCHANGE_NAME = 'billing-reports'
QUEUE_ARGUMENTS = {'x-max-priority': 10}
ACTIVITIES_EXCHANGE_NAME = 'activities-tasks'

ORCHESTRATOR_QUEUE = 'report-imports'
RAW_QUEUE = 'report-raw'
CLEAN_QUEUE = 'report-clean'
MIGRATIONS_LOCK = 'diworker_migrations'
MIGRATIONS_PATH = 'diworker/diworker/migrations'


def run_worker(worker_class):
    """Bootstrap and run a worker. setup_worker(config_cl) is called before
    connecting to RabbitMQ (used by the orchestrator to run migrations)."""
    urllib3.disable_warnings(InsecureRequestWarning)
    logging.basicConfig(level=logging.INFO,
                        format='[%(threadName)s] %(levelname)s: %(message)s')

    config_cl_params = {
        'host': os.environ.get('HX_ETCD_HOST'),
        'port': int(os.environ.get('HX_ETCD_PORT')),
    }
    config_cl = ConfigClient(**config_cl_params)
    config_cl.wait_configured()

    worker_class.setup_worker(config_cl)

    conn_str = 'amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit'))
    dw_settings = config_cl.diworker_settings()

    service_name = worker_class.SERVICE_NAME
    LOG.info('Starting %s', service_name)
    with QConnection(conn_str) as conn:
        OpenTelemetryConfig(
            service_name=os.getenv('OTEL_SERVICE_NAME', service_name),
            service_version=os.getenv('OTEL_SERVICE_VERSION', 'local'),
            otel_config=config_cl.read_branch('/opentelemetry'),
            service_config=config_cl.read_branch('diworker/opentelemetry'),
        ).setup_open_telemetry()
        try:
            worker = worker_class(conn, conn_str, dw_settings, config_cl_params)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.executor.shutdown(wait=True)
            LOG.info('%s shutdown', service_name)


def _is_rate_limit_exc(exc):
    if getattr(exc, 'status_code', None) == 429:
        return True
    msg = str(exc).lower()
    return '429' in msg or 'toomanyrequests' in msg or 'too many requests' in msg


class BaseWorker(ConsumerMixin):
    QUEUE_NAME = None
    SERVICE_NAME = None

    @staticmethod
    def setup_worker(config_cl):
        migrator = Migrator(config_cl, 'restapi', MIGRATIONS_PATH)
        with EtcdLock(config_cl, MIGRATIONS_LOCK):
            migrator.migrate()

    def __init__(self, connection, rabbitmq_conn_str, diworker_settings,
                 config_params):
        self.connection = connection
        self.rabbitmq_conn_str = rabbitmq_conn_str
        self.diworker_settings = diworker_settings
        self.config_cl_params = config_params
        self._active_ids = set()
        self._active_lock = Lock()
        self._pending_acks = queue.Queue()
        self.running = True
        Thread(target=self._heartbeat, args=(config_params,),
               daemon=True).start()
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    @property
    def max_workers(self):
        return int(self.diworker_settings.get(
            'max_report_imports_workers', DEFAULT_MAX_WORKERS))

    def _heartbeat(self, config_params):
        config_cl = self.get_config_cl(config_params)
        rest_cl = self.get_rest_cl(config_cl)
        while self.running:
            with self._active_lock:
                ids = list(self._active_ids)
            for report_import_id in ids:
                try:
                    rest_cl.report_import_update(report_import_id, {})
                except Exception as exc:
                    LOG.warning('Heartbeat failed for %s: %s',
                                report_import_id, exc)
            time.sleep(HEARTBEAT_INTERVAL)
        rest_cl.close()

    @staticmethod
    def get_config_cl(config_params):
        return ConfigClient(**config_params)

    @staticmethod
    def get_rest_cl(config_cl):
        return RestClient(url=config_cl.restapi_url(), verify=False,
                          secret=config_cl.cluster_secret())

    @staticmethod
    def get_mongo_cl(config_cl):
        return MongoClient(config_cl.mongo_params()[0])

    @staticmethod
    def get_clickhouse_cl(config_cl):
        user, password, host, db_name, port, secure = (
            config_cl.clickhouse_params())
        return clickhouse_connect.get_client(
            host=host, password=password, database=db_name,
            user=user, port=port, secure=secure)

    def get_importer_params(self, cloud_acc_id, import_dict, config_cl,
                            rest_cl, mongo_cl, clickhouse_cl):
        return {
            'cloud_account_id': cloud_acc_id,
            'rest_cl': rest_cl,
            'config_cl': config_cl,
            'mongo_raw': mongo_cl.restapi['raw_expenses'],
            'mongo_resources': mongo_cl.restapi['resources'],
            'mongo_report_files': mongo_cl.restapi['report_import_files'],
            'clickhouse_cl': clickhouse_cl,
            'import_file': import_dict.get('import_file'),
            'recalculate': import_dict.get('is_recalculation', False),
            'import_from': import_dict.get('import_from'),
            'import_to': import_dict.get('import_to'),
            'reimport': import_dict.get('reimport', False),
            'max_tenant_concurrent': int(self.diworker_settings.get(
                'max_tenant_import_workers', DEFAULT_MAX_TENANT_WORKERS)),
            'csv_rewrite_days': self.diworker_settings.get('csv_rewrite_days'),
        }

    def publish(self, queue_name, task):
        exchange = Exchange(EXCHANGE_NAME, type='direct')
        queue = Queue(queue_name, exchange, routing_key=queue_name,
                      queue_arguments=QUEUE_ARGUMENTS)
        conn = QConnection(self.rabbitmq_conn_str)
        with producers[conn].acquire(block=True) as producer:
            producer.publish(task, serializer='json', exchange=exchange,
                             declare=[exchange, queue],
                             routing_key=queue_name, retry=True)

    def publish_activities_task(self, organization_id, object_id, object_type,
                                action, routing_key, meta=None):
        task = {
            'organization_id': organization_id,
            'object_id': object_id,
            'object_type': object_type,
            'action': action,
            'meta': meta,
        }
        exchange = Exchange(ACTIVITIES_EXCHANGE_NAME, type='topic')
        conn = QConnection(self.rabbitmq_conn_str)
        with producers[conn].acquire(block=True) as producer:
            producer.publish(task, serializer='json', exchange=exchange,
                             declare=[exchange], routing_key=routing_key,
                             retry=True)

    def send_report_failed_email(self, cloud_account, previous_attempt_ts,
                                 now, is_throttled=False):
        last_import_at = cloud_account.get('last_import_at') or cloud_account[
            'created_at']
        if now - last_import_at < ALERT_THRESHOLD:
            return
        if (last_import_at < previous_attempt_ts and
                startday(utcfromtimestamp(previous_attempt_ts)) ==
                startday(utcfromtimestamp(now))):
            return
        action = ('report_import_throttled' if is_throttled
                  else 'report_import_failed')
        self.publish_activities_task(
            cloud_account['organization_id'], cloud_account['id'],
            'cloud_account', action, 'organization.report_import.failed')

    def get_consumers(self, Consumer, channel):
        exchange = Exchange(EXCHANGE_NAME, type='direct')
        queue = Queue(self.QUEUE_NAME, exchange, routing_key=self.QUEUE_NAME,
                      queue_arguments=QUEUE_ARGUMENTS)
        return [Consumer(
            queues=[queue], accept=['json'], callbacks=[self._on_message],
            prefetch_count=self.max_workers)]

    def _on_message(self, body, message):
        self.executor.submit(self._execute, body, message)

    def _execute(self, body, message):
        import_id = body.get('report_import_id')
        config_cl, rest_cl, mongo_cl, clickhouse_cl = None, None, None, None
        locked = True
        try:
            config_cl = self.get_config_cl(self.config_cl_params)
            rest_cl = self.get_rest_cl(config_cl)
            mongo_cl = self.get_mongo_cl(config_cl)
            clickhouse_cl = self.get_clickhouse_cl(config_cl)
            locked = self.process_task(body, config_cl, rest_cl, mongo_cl,
                                       clickhouse_cl)
        except Exception:
            LOG.exception('Task failed: %s', body)
        finally:
            if mongo_cl:
                mongo_cl.close()
            if clickhouse_cl:
                clickhouse_cl.close()
            if rest_cl:
                rest_cl.close()
            if locked:
                with self._active_lock:
                    self._active_ids.discard(import_id)
        self._pending_acks.put(message)

    def on_iteration(self):
        while True:
            try:
                self._pending_acks.get_nowait().ack()
            except queue.Empty:
                break

    def process_task(self, task, config_cl, rest_cl, mongo_cl, clickhouse_cl):
        raise NotImplementedError
