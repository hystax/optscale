import os
import asyncio
from functools import partial
import concurrent.futures

from kombu import Connection as QConnection, Exchange
from kombu.pools import producers


from config_client.client import Client as ConfigClient


class TaskProducer:
    ROUTING_KEY = 'bulldozer-task'
    EXCHANGE_NAME = 'bulldozer-tasks'
    RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                    'interval_step': 1, 'interval_max': 3}
    RESCHEDULE_TIMEOUT = 60 * 60 * 12

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    def __init__(self):
        self._config_cl = None

    @classmethod
    async def run_async(cls, func, *args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        if executor is None:
            executor = cls.executor
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    @property
    def config_cl(self):
        if self._config_cl is None:
            config_cl = ConfigClient(
                host=os.environ.get('HX_ETCD_HOST'),
                port=int(os.environ.get('HX_ETCD_PORT')),
            )
            self._config_cl = config_cl
        return self._config_cl

    def create_task(self, task):
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self.config_cl.read_branch('/rabbit')),
            transport_options=self.RETRY_POLICY)

        task_exchange = Exchange(self.EXCHANGE_NAME, type='direct')
        with producers[queue_conn].acquire(block=True) as producer:
            producer.publish(
                task,
                serializer='json',
                exchange=task_exchange,
                declare=[task_exchange],
                routing_key=self.ROUTING_KEY,
                retry=True,
                retry_policy=self.RETRY_POLICY
            )
