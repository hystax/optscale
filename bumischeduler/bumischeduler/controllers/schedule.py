from datetime import datetime, timedelta

import logging
import etcd

from kombu import Connection as QConnection, Exchange
from kombu.pools import producers

from optscale_client.rest_api_client.client_v2 import Client as RestClient


LOG = logging.getLogger(__name__)
ROUTING_KEY = 'bumi-task'
EXCHANGE_NAME = 'bumi-tasks'
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}
RESCHEDULE_TIMEOUT = 60 * 60 * 12


class ScheduleController(object):

    def __init__(self, config=None):
        self._config = config
        self._rest_cl = None

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self._config.restapi_url(), verify=False)
            self._rest_cl.secret = self._config.cluster_secret()
        return self._rest_cl

    def get_bumi_worker_params(self):
        try:
            return self._config.read_branch("/bumi_worker")
        except etcd.EtcdKeyNotFound:
            default_values = {
                'task_timeout': 3600,
                'wait_timeout': 7200,
                'max_retries': 5,
                'run_period': 10800
            }
            LOG.warning('Parameters for bumi_worker are not found in etcd. '
                        'Will use default values: %s', default_values)
            return default_values

    def create_tasks(self, tasks):
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self._config.read_branch('/rabbit')),
            transport_options=RETRY_POLICY)

        task_exchange = Exchange(EXCHANGE_NAME, type='direct')
        with producers[queue_conn].acquire(block=True) as producer:
            for task in tasks:
                LOG.debug('Creating task %s', task)
                producer.publish(
                    task,
                    serializer='json',
                    exchange=task_exchange,
                    declare=[task_exchange],
                    routing_key=ROUTING_KEY,
                    retry=True,
                    retry_policy=RETRY_POLICY
                )

    def get_checklists(self):
        _, res = self.rest_cl.checklist_list()
        return res['checklists']

    def generate_tasks(self):
        now = datetime.utcnow()
        checklists = self.get_checklists()
        bumi_worker_params = self.get_bumi_worker_params()
        scheduled = []
        tasks = []
        for checklist in checklists:
            next_run = checklist['next_run']
            last_completed = checklist['last_completed']
            last_run = checklist['last_run']
            if next_run <= int(
                    now.timestamp()) and last_completed == last_run:
                scheduled.append(checklist)
            elif last_run != last_completed and int(
                    now.timestamp()) - last_run >= RESCHEDULE_TIMEOUT:
                LOG.warning('Organization %s checklist stuck. Rescheduling',
                            checklist['organization_id'])
                scheduled.append(checklist)

        LOG.info('Processing %s schedules', len(scheduled))

        run_period = int(bumi_worker_params['run_period'])
        next_run = int((now + timedelta(seconds=run_period)).timestamp())
        for checklist in scheduled:
            self.rest_cl.checklist_update(
                checklist['id'], {'next_run': next_run,
                                  'last_run': int(now.timestamp())})
            tasks.append({
                'last_update': int(
                    datetime.utcnow().timestamp()),
                'tries_count': 0,
                'organization_id': checklist['organization_id'],
                'checklist_id': checklist['id'],
                'created_at': int(now.timestamp()),
                'state': 'created',
                'task_timeout': int(bumi_worker_params['task_timeout']),
                'wait_timeout': int(bumi_worker_params['wait_timeout']),
                'max_retries': int(bumi_worker_params['max_retries'])
            })
        self.create_tasks(tasks)
