import threading
import time
import uuid
from unittest.mock import MagicMock

import pytest
from kombu import Connection, Exchange, Queue

from docker_images.resource_discovery.consumer import ConcurrentConsumer

WAIT = 5


class BlockingHandler:
    """Handler whose calls block until release(task_id) is called"""

    def __init__(self):
        self._events = {}
        self._lock = threading.Lock()

    def __call__(self, body):
        event = threading.Event()
        with self._lock:
            self._events[body['id']] = event
        assert event.wait(WAIT), 'handler was never released'

    def release(self, task_id):
        deadline = time.monotonic() + WAIT
        while task_id not in self._events:
            assert time.monotonic() < deadline, f'task {task_id} never started'
            time.sleep(0.01)
        self._events[task_id].set()

    def release_all(self):
        with self._lock:
            events = list(self._events.values())
        for event in events:
            event.set()


@pytest.fixture
def blocking_handler():
    handler = BlockingHandler()
    yield handler
    handler.release_all()


def make_consumer(handler, **kwargs):
    """A 'connected' consumer: get_consumers and on_consume_ready have run
    with a mocked kombu Consumer"""
    consumer = ConcurrentConsumer(None, MagicMock(), handler, **kwargs)
    kombu_consumer = MagicMock()
    consumer.get_consumers(MagicMock(return_value=kombu_consumer), None)
    consumer.on_consume_ready(None, None, [kombu_consumer])
    return consumer, kombu_consumer


def wait_running(consumer, expected):
    """Iterate the loop until `expected` tasks are still running"""
    deadline = time.monotonic() + WAIT
    while True:
        consumer.on_iteration()
        if consumer.running_tasks == expected:
            return
        assert time.monotonic() < deadline, 'tasks did not finish'
        time.sleep(0.01)


def test_concurrency_must_be_positive():
    with pytest.raises(ValueError):
        ConcurrentConsumer(None, MagicMock(), print, concurrency=0)


def test_get_consumers_uses_prefetch_one():
    task_queue = MagicMock()
    consumer = ConcurrentConsumer(None, task_queue, print, concurrency=3)
    factory = MagicMock()
    consumer.get_consumers(factory, None)
    factory.assert_called_once_with(
        queues=[task_queue], accept=['json'],
        callbacks=[consumer.on_message], prefetch_count=1)


def test_message_is_acked_before_the_task_runs(blocking_handler):
    consumer, _ = make_consumer(blocking_handler)
    message = MagicMock()
    consumer.on_message({'id': 1}, message)
    message.ack.assert_called_once()
    assert consumer.running_tasks == 1
    blocking_handler.release(1)
    wait_running(consumer, 0)
    message.ack.assert_called_once()


def test_handler_runs_outside_the_main_thread():
    threads = []
    consumer, _ = make_consumer(
        lambda body: threads.append(threading.current_thread()))
    consumer.on_message({'id': 1}, MagicMock())
    wait_running(consumer, 0)
    assert threads[0] is not threading.current_thread()


def test_pause_when_full_and_resume_when_a_slot_frees(blocking_handler):
    consumer, kombu_consumer = make_consumer(blocking_handler, concurrency=2)
    consumer.on_message({'id': 1}, MagicMock())
    kombu_consumer.cancel.assert_not_called()
    consumer.on_message({'id': 2}, MagicMock())
    kombu_consumer.cancel.assert_called_once()

    consumer.on_iteration()          # nothing finished yet: still paused
    kombu_consumer.consume.assert_not_called()

    blocking_handler.release(1)
    wait_running(consumer, 1)
    kombu_consumer.consume.assert_called_once()
    kombu_consumer.cancel.assert_called_once()


def test_delivery_in_transit_during_pause_is_accepted(blocking_handler):
    consumer, kombu_consumer = make_consumer(blocking_handler, concurrency=1)
    late_message = MagicMock()
    # basic.cancel waits for CancelOk and dispatches the frames read
    # meanwhile: a delivery already in transit re-enters on_message
    kombu_consumer.cancel.side_effect = (
        lambda: consumer.on_message({'id': 2}, late_message))

    consumer.on_message({'id': 1}, MagicMock())

    kombu_consumer.cancel.assert_called_once()
    late_message.ack.assert_called_once()
    assert consumer.running_tasks == 2     # concurrency + 1 at most
    blocking_handler.release(1)
    blocking_handler.release(2)
    wait_running(consumer, 0)
    kombu_consumer.consume.assert_called_once()


def test_reconnect_with_a_full_pool_pauses_the_new_consumer(blocking_handler):
    consumer, _ = make_consumer(blocking_handler, concurrency=1)
    consumer.on_message({'id': 1}, MagicMock())
    new_kombu_consumer = MagicMock()
    consumer.get_consumers(MagicMock(return_value=new_kombu_consumer), None)
    consumer.on_consume_ready(None, None, [new_kombu_consumer])
    new_kombu_consumer.cancel.assert_called_once()
    blocking_handler.release(1)
    wait_running(consumer, 0)
    new_kombu_consumer.consume.assert_called_once()


def test_failing_task_is_logged_and_frees_its_slot(caplog):
    def handler(_body):
        raise RuntimeError('boom')

    consumer, kombu_consumer = make_consumer(handler, concurrency=1)
    consumer.on_message({'id': 1}, MagicMock())
    wait_running(consumer, 0)
    kombu_consumer.consume.assert_called_once()   # paused, then resumed
    assert 'Task failed' in caplog.text
    assert 'boom' in caplog.text


def test_on_healthy_is_called_while_idle():
    on_healthy = MagicMock()
    consumer, _ = make_consumer(print, on_healthy=on_healthy)
    consumer.on_iteration()
    on_healthy.assert_called_once()


def test_on_healthy_is_called_while_a_task_is_progressing(blocking_handler):
    on_healthy = MagicMock()
    consumer, _ = make_consumer(blocking_handler, max_stall_seconds=60,
                                on_healthy=on_healthy)
    consumer.on_message({'id': 1}, MagicMock())
    consumer.on_iteration()
    on_healthy.assert_called_once()


def test_on_healthy_is_not_called_when_a_task_has_stalled(blocking_handler,
                                                          mocker):
    on_healthy = MagicMock()
    consumer, _ = make_consumer(blocking_handler, max_stall_seconds=60,
                                on_healthy=on_healthy)
    consumer.on_message({'id': 1}, MagicMock())
    mocker.patch.object(consumer, 'longest_stall_seconds', return_value=120)
    consumer.on_iteration()
    on_healthy.assert_not_called()


def test_longest_stall_seconds(blocking_handler):
    consumer, _ = make_consumer(blocking_handler, concurrency=2)
    assert consumer.longest_stall_seconds() == 0
    consumer.on_message({'id': 1}, MagicMock())
    time.sleep(0.05)
    consumer.on_message({'id': 2}, MagicMock())
    assert consumer.longest_stall_seconds() >= 0.05


def test_progress_reported_by_a_task_resets_its_stall():
    """A task may run for any length of time as long as it reports
    progress"""
    report = threading.Event()
    reported = threading.Event()
    done = threading.Event()
    consumer = None

    def handler(_body):
        assert report.wait(WAIT)
        consumer.progress()
        reported.set()
        assert done.wait(WAIT)

    consumer, _ = make_consumer(handler)
    consumer.on_message({'id': 1}, MagicMock())
    time.sleep(0.05)
    assert consumer.longest_stall_seconds() >= 0.05
    report.set()
    assert reported.wait(WAIT)
    assert consumer.longest_stall_seconds() < 0.05
    done.set()
    wait_running(consumer, 0)


def test_progress_outside_a_task_thread_is_ignored(blocking_handler):
    consumer, _ = make_consumer(blocking_handler)
    consumer.progress()                 # idle: nothing to do, no error
    consumer.on_message({'id': 1}, MagicMock())
    time.sleep(0.05)
    consumer.progress()                 # main thread: not the task's own
    assert consumer.longest_stall_seconds() >= 0.05


def test_end_to_end_with_kombu_memory_transport():
    """Real ConsumerMixin loop: all messages are processed, at most
    concurrency + 1 at a time, and the loop stops on should_stop"""
    name = f'test-{uuid.uuid4().hex}'
    exchange = Exchange(name, type='direct')
    task_queue = Queue(name, exchange, routing_key=name)
    total, concurrency = 6, 2
    processed = []
    running = []
    max_running = []
    lock = threading.Lock()

    def handler(body):
        with lock:
            running.append(body['id'])
            max_running.append(len(running))
        time.sleep(0.05)
        with lock:
            running.remove(body['id'])
            processed.append(body['id'])

    with Connection('memory://') as conn:
        with conn.Producer() as producer:
            for i in range(total):
                producer.publish({'id': i}, exchange=exchange,
                                 routing_key=name, declare=[task_queue],
                                 serializer='json')
        consumer = ConcurrentConsumer(conn, task_queue, handler,
                                      concurrency=concurrency)
        thread = threading.Thread(target=consumer.run, daemon=True)
        thread.start()
        deadline = time.monotonic() + 10
        while len(processed) < total and time.monotonic() < deadline:
            time.sleep(0.05)
        consumer.should_stop = True
        thread.join(WAIT)

    assert sorted(processed) == list(range(total))
    assert max(max_running) <= concurrency + 1
    assert not thread.is_alive()
