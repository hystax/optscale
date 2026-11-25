"""kombu ConsumerMixin that runs tasks in a thread pool.

The main thread runs the kombu loop and is the only thread that talks to
RabbitMQ: it receives messages, acks them and pauses/resumes the consumer.
Tasks run in a ThreadPoolExecutor and never block that loop, so the
connection stays responsive (heartbeats, channel closes) however long a
task takes.

Every message is acked as soon as it is received. The broker therefore
never holds an unacked delivery while a task runs, and its
consumer_timeout cannot fire. The price is that a task is lost when the
process dies while running it: the producer side must re-schedule tasks
that did not complete (the discovery scheduler does, see observe_timeout).

Acked messages do not count against prefetch, so the only way to bound how
many tasks are taken is to cancel the consumer while every slot is busy
and consume again once one frees up. A delivery can already be in transit
when the cancel is sent; it is accepted, so at most ``concurrency + 1``
tasks run at once.

Health is based on progress, not duration: a task may run for as long as
it keeps calling ``progress()``. A task that reports nothing for
``max_stall_seconds`` is considered hung and makes the consumer unhealthy.
Health keeps being reported while the broker is unreachable: the process
is only unhealthy when its own loop or one of its tasks is stuck.
"""
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from kombu.mixins import ConsumerMixin

LOG = logging.getLogger(__name__)


class _Task:
    """What the main thread tracks about one running task"""
    __slots__ = ('last_progress',)

    def __init__(self):
        self.last_progress = time.monotonic()


class ConcurrentConsumer(ConsumerMixin):

    def __init__(self, connection, task_queue, handler, concurrency=1,
                 max_stall_seconds=1800, on_healthy=None, accept=('json',)):
        """
        :param handler: callable(body), run in a pool thread for each message.
            It should call ``progress()`` whenever it does real work.
        :param max_stall_seconds: a task that reports no progress for this
            long makes the consumer unhealthy
        :param on_healthy: callable(), invoked on every loop iteration while
            the consumer is healthy, e.g. to refresh a liveness file. It is
            not invoked when the loop is stuck or when a task has stalled.
        """
        if concurrency < 1:
            raise ValueError('concurrency must be >= 1')
        self.connection = connection
        self.task_queue = task_queue
        self.handler = handler
        self.concurrency = concurrency
        self.max_stall_seconds = max_stall_seconds
        self.on_healthy = on_healthy or (lambda: None)
        self.accept = list(accept)
        self._pool = ThreadPoolExecutor(max_workers=concurrency,
                                        thread_name_prefix='task')
        self._running = {}      # future -> _Task
        self._local = threading.local()   # .task: _Task of this pool thread
        self._consumer = None   # the kombu Consumer on the current channel
        self._paused = False

    # kombu hooks, all run in the main thread

    def get_consumers(self, Consumer, channel):
        self._consumer = Consumer(queues=[self.task_queue],
                                  accept=self.accept,
                                  callbacks=[self.on_message],
                                  prefetch_count=1)
        return [self._consumer]

    def on_consume_ready(self, connection, channel, consumers, **kwargs):
        # runs after every (re)connect; tasks started before a reconnect
        # still occupy their slots
        self._paused = False
        if self._full():
            self._pause()

    def on_iteration(self):
        # runs at least once a second while connected
        self._reap()
        if self._paused and not self._full():
            self._resume()
        self._check_health()

    def on_connection_error(self, exc, interval):
        # runs before every reconnect attempt (kombu retries at most 30 s
        # apart). The broker being down does not make this process
        # unhealthy: running tasks talk to the clouds and rest_api, not to
        # RabbitMQ, so keep reporting health while waiting for the broker
        super().on_connection_error(exc, interval)
        self._reap()
        self._check_health()

    def on_message(self, body, message):
        message.ack()
        task = _Task()
        self._running[self._pool.submit(self._run, body, task)] = task
        if self._full() and not self._paused:
            self._pause()

    # called from task threads

    def progress(self):
        """Report that the calling task is making progress.

        Call it from the handler whenever real work is done (a page of
        results received, a batch written). It is a no-op when called
        outside a task thread.
        """
        task = getattr(self._local, 'task', None)
        if task is not None:
            task.last_progress = time.monotonic()

    # helpers

    def _run(self, body, task):
        self._local.task = task
        try:
            self.handler(body)
        except Exception:  # pylint: disable=broad-exception-caught
            LOG.exception('Task failed: %s', body)
        finally:
            self._local.task = None

    def _reap(self):
        self._running = {future: task
                         for future, task in self._running.items()
                         if not future.done()}

    def _check_health(self):
        if self.longest_stall_seconds() < self.max_stall_seconds:
            self.on_healthy()

    def _full(self):
        return len(self._running) >= self.concurrency

    def _pause(self):
        # set before cancel(): cancel waits for CancelOk and dispatches the
        # frames read meanwhile, so on_message can run for a delivery that
        # was already in transit
        self._paused = True
        LOG.debug('All %s task slots are busy, pausing the consumer',
                  self.concurrency)
        self._consumer.cancel()

    def _resume(self):
        self._paused = False
        LOG.debug('A task slot is free, resuming the consumer')
        self._consumer.consume()

    @property
    def running_tasks(self):
        return len(self._running)

    def longest_stall_seconds(self):
        """Seconds since the running task with the oldest progress report
        last reported (0 when idle)"""
        if not self._running:
            return 0.0
        return time.monotonic() - min(
            task.last_progress for task in self._running.values())
