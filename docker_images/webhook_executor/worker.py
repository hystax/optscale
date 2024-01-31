#!/usr/bin/env python
import os
import time
import json
from datetime import datetime
from threading import Thread
import urllib3
import requests
from pymongo import MongoClient
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu import Exchange, Queue, binding
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient


QUEUE_NAME = 'webhook-task'
MAX_RESPONSE_LENGHT = 5000
LOG = get_logger(__name__)
TASK_EXCHANGE = Exchange('activities-tasks', type='topic')
TASK_QUEUE = Queue(QUEUE_NAME, TASK_EXCHANGE, bindings=[
    binding(TASK_EXCHANGE, routing_key='booking.#')])


class HttpClient:
    def __init__(self):
        self._session = None

    @property
    def session(self):
        if not self._session:
            self._session = requests.session()
        return self._session

    def request(self, url, method, body, headers=None):
        response = self.session.request(
            method, url, data=json.dumps(body), headers=headers, verify=False,
            timeout=10)
        response_body = None
        try:
            response.raise_for_status()
        except Exception as ex:
            response_body = str(ex)
        if response.status_code != requests.codes.get('no_content'):
            if 'application/json' in response.headers['Content-Type']:
                response_body = json.loads(
                    response.content.decode('utf-8'))
            if 'text/plain' in response.headers['Content-Type']:
                response_body = response.content.decode()
        return response.status_code, response_body

    def post(self, url, body, headers=None):
        return self.request(url, "POST", body, headers)

    def __del__(self):
        self.session.close()


class WebhookExecutorWorker(ConsumerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl
        self._rest_cl = None
        self.running = True
        self.thread = Thread(target=self.heartbeat)
        self.thread.start()
        self._mongo_cl = None

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._rest_cl

    @property
    def mongo_cl(self):
        if not self._mongo_cl:
            mongo_params = self.config_cl.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_cl = MongoClient(mongo_conn_string)
        return self._mongo_cl

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[TASK_QUEUE], accept=['json'],
                         callbacks=[self.process_task], prefetch_count=10)]

    def get_environment_meta(self, webhook, meta_info):
        _, environment = self.rest_cl.cloud_resource_get(
            webhook['object_id'])
        booking_id = meta_info['booking_id']
        _, booking = self.rest_cl.shareable_book_get(booking_id)
        if booking:
            ssh_key_map_json = booking.get('ssh_key')
            if ssh_key_map_json:
                ssh_key_map = json.loads(ssh_key_map_json)
                ssh_key = ssh_key_map.get('key')
                booking['ssh_key'] = ssh_key
        owner_id = booking.get('acquired_by_id')
        owner = {}
        if owner_id:
            _, owner = self.rest_cl.employee_get(owner_id)
        return {
            'environment': environment,
            'booking_details': booking,
            'booking_owner': owner
        }

    def get_hook_meta(self, webhook, meta_info=None):
        object_meta_map = {
            'environment': self.get_environment_meta
        }
        get_func = object_meta_map.get(webhook['object_type'])
        if get_func:
            return get_func(webhook, meta_info)

    @staticmethod
    def post_webhook(webhook, body):
        http_client = HttpClient()
        headers = json.loads(
            webhook['headers']) if webhook.get('headers') else None
        result = http_client.post(webhook['url'], body, headers)
        return result

    def validate_webhook(self, webhook, meta_info=None):
        object_meta_map = {
            'environment': self.validate_enironment_webhook
        }
        get_func = object_meta_map.get(webhook['object_type'])
        if get_func:
            return get_func(webhook, meta_info)

    def validate_enironment_webhook(self, webhook, meta_info):
        trigger_time = meta_info.get('time', 0)
        if trigger_time < webhook['created_at']:
            return False
        return True

    def execute_webhook(self, task):
        start_time = datetime.utcnow()
        org_id = task.get('organization_id')
        object_id = task.get('object_id')
        action = task.get('action')
        task_params = {
            'organization_id': org_id,
            'object_type': task.get('object_type'),
            'object_id': object_id,
            'action': action,
        }
        if any(map(lambda x: x is None, task_params.values())):
            raise Exception('Invalid task received: {}'.format(task))

        _, resp = self.rest_cl.webhook_list(org_id)
        if not resp.get('webhooks'):
            return
        webhooks_map = {
            (w['object_id'], w['action']): w for w in resp['webhooks']
        }
        _, booking = self.rest_cl.shareable_book_get(object_id)
        if not booking.get('resource_id'):
            return
        webhook = webhooks_map.get((booking['resource_id'], action))
        if not webhook:
            return
        action_time_field = {'booking_acquire': 'acquired_since',
                             'booking_release': 'released_at'}
        meta = {'booking_id': booking['id'],
                'time': booking[action_time_field.get(action)]}
        if not self.validate_webhook(webhook, meta):
            return
        # skip inactive webhooks
        if not webhook.get('active'):
            return
        try:
            meta_info = self.get_hook_meta(webhook, meta)
        except Exception:
            LOG.error('Unable to collect meta information')
            meta_info = {}

        request_body = {
            'webhook_id': webhook['id'],
            'action': webhook['action'],
            'object_type': webhook['object_type'],
            'object_id': webhook['object_id'],
            'description': meta_info
        }
        try:
            code, result = self.post_webhook(webhook, request_body)
            if len(str(result)) > MAX_RESPONSE_LENGHT:
                result = 'Response is too long'
            success = True if code and 200 <= code < 300 else False
        except Exception as ex:
            LOG.warning('Unable to execute webhook %s' % webhook['id'])
            result = str(ex)
            code = 500
            success = False
        log_info = {
            'organization_id': org_id,
            'webhook_id': webhook['id'],
            'url': webhook['url'],
            'headers': webhook['headers'],
            'body': json.dumps(request_body),
            'success': success,
            'execution_time': int(datetime.utcnow().timestamp()),
            'execution_result': '%s, %s' % (code, result)
        }
        self.mongo_cl.restapi.webhook_logs.insert_one(log_info)
        LOG.info('Webhook executor for %s (%s) completed in %s seconds',
                 webhook['object_type'], webhook['object_id'],
                 (datetime.utcnow() - start_time).total_seconds())

    def process_task(self, body, message):
        try:
            self.execute_webhook(body)
        except Exception as exc:
            LOG.exception('Webhook executor failed: %s', str(exc))
        message.ack()

    def heartbeat(self):
        while self.running:
            self.connection.heartbeat_check()
            time.sleep(1)


if __name__ == '__main__':
    urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
    debug = os.environ.get('DEBUG', False)
    log_level = 'DEBUG' if debug else 'INFO'
    setup_logging(loglevel=log_level, loggers=[''])

    config_client = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_client.wait_configured()
    conn_str = 'amqp://{user}:{pass}@{host}:{port}'.format(
        **config_client.read_branch('/rabbit'))
    with Connection(conn_str) as conn:
        try:
            worker = WebhookExecutorWorker(conn, config_client)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.thread.join()
            LOG.info('Shutdown received')
