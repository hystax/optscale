import threading
import time
from unittest.mock import MagicMock

import pytest

from docker_images.resource_discovery import worker as worker_module
from docker_images.resource_discovery.worker import (
    CHUNK_SIZE, DiscoveryWorker, ResourcesSaver, touch_liveness_file)

WAIT = 5
WRITING_TIMEOUT = 5


class FakeResource:
    def __init__(self, name):
        self.name = name
        self.cloud_account_id = None
        self.cloud_type = None


class FakeAdapter:
    MAX_PARALLEL_REQUESTS = 4

    def __init__(self, generators):
        self.generators = generators
        self.closed = False

    def get_discovery_calls(self, _resource_type):
        return [(lambda gen=gen: gen, ()) for gen in self.generators]

    def close(self):
        self.closed = True


def resources(prefix, count):
    for i in range(count):
        yield FakeResource(f'{prefix}-{i}')


def failing(prefix, count, error):
    yield from resources(prefix, count)
    raise error


@pytest.fixture(autouse=True)
def fast_saver_poll(monkeypatch):
    monkeypatch.setattr(ResourcesSaver, 'POLL_SECONDS', 0.01)


@pytest.fixture
def saved_chunks(mocker):
    """Replace the REST bulk write: record (cloud account, chunk size)"""
    saved = []
    lock = threading.Lock()

    def save(_saver, chunk):
        with lock:
            saved.append((next(iter(chunk)).cloud_account_id, len(chunk)))

    mocker.patch.object(ResourcesSaver, 'save_bulk_resources', save)
    return saved


@pytest.fixture
def rest_cl():
    rest = MagicMock()
    rest.discovery_info_list.return_value = (
        200, {'discovery_info': [{'id': 'di-1', 'enabled': True}]})
    rest.cloud_account_get.side_effect = lambda ca_id: (
        200, {'id': ca_id, 'type': 'aws_cnr', 'organization_id': 'org-1',
              'config': {}})
    rest.organization_get.return_value = (200, {'disabled': False})
    return rest


@pytest.fixture
def discovery(mocker, rest_cl):
    config_cl = MagicMock()
    config_cl.resource_discovery_params.return_value = (
        10000, None, WRITING_TIMEOUT, 7200, None)
    config_cl.product_tracking_id.return_value = 'tracking-id'
    mocker.patch.object(DiscoveryWorker, 'new_rest_cl', return_value=rest_cl)
    mocker.patch.object(DiscoveryWorker, 'new_insider_cl',
                        return_value=MagicMock())
    return DiscoveryWorker(config_cl)


def use_adapters(mocker, adapters_by_account):
    mocker.patch.object(
        worker_module.CloudAdapter, 'get_adapter',
        side_effect=lambda config: adapters_by_account[config['id']])


def discovery_info_updates(rest_cl):
    return [c.args[1] for c in rest_cl.discovery_info_update.call_args_list]


# ResourcesSaver

def make_saver(limit=10000, timeout=None):
    return ResourcesSaver(rest_cl=MagicMock(), insider_cl=MagicMock(),
                          limit=limit, timeout=timeout,
                          product_tracking_id='tracking-id')


def test_saver_saves_all_chunks_before_close_returns(saved_chunks):
    saver = make_saver()
    for i in range(3):
        chunk = set(resources(f'r{i}', 10))
        for res in chunk:
            res.cloud_account_id = f'ca-{i}'
        saver.send(chunk)
    assert saver.close(timeout=WAIT)
    assert saved_chunks == [('ca-0', 10), ('ca-1', 10), ('ca-2', 10)]


def test_saver_thread_is_a_daemon(saved_chunks):
    saver = make_saver()
    assert saver._thread.daemon  # pylint: disable=protected-access
    assert saver.close(timeout=WAIT)


def test_saver_close_times_out_when_saving_is_stuck(mocker):
    release = threading.Event()
    mocker.patch.object(ResourcesSaver, 'save_bulk_resources',
                        lambda _saver, _chunk: release.wait(WAIT))
    saver = make_saver()
    saver.send({FakeResource('r')})
    assert not saver.close(timeout=0.2)
    release.set()


def test_saver_send_gives_up_when_the_queue_stays_full(mocker, caplog):
    release = threading.Event()
    mocker.patch.object(ResourcesSaver, 'save_bulk_resources',
                        lambda _saver, _chunk: release.wait(WAIT))
    saver = make_saver(limit=CHUNK_SIZE, timeout=0.2)   # queue of 1 chunk
    saver.send({FakeResource('r1')})                    # being saved
    deadline = time.monotonic() + WAIT
    while saver.queue.qsize() and time.monotonic() < deadline:
        time.sleep(0.01)
    saver.send({FakeResource('r2')})                    # queued
    saver.send({FakeResource('r3')})                    # queue full
    assert 'Failed to add a chunk of 1 resources' in caplog.text
    release.set()
    assert saver.close(timeout=WAIT)


def test_saver_keeps_going_after_a_failed_chunk(mocker, caplog):
    calls = []

    def save(_saver, chunk):
        calls.append(len(chunk))
        if len(calls) == 1:
            raise RuntimeError('rest api down')

    mocker.patch.object(ResourcesSaver, 'save_bulk_resources', save)
    saver = make_saver()
    saver.send({FakeResource('r1')})
    saver.send({FakeResource('r2'), FakeResource('r3')})
    assert saver.close(timeout=WAIT)
    assert calls == [1, 2]
    assert 'rest api down' in caplog.text


# DiscoveryWorker

def test_discovery_saves_resources_in_chunks(mocker, discovery, rest_cl,
                                             saved_chunks):
    adapter = FakeAdapter([resources('a', 250), resources('b', 200)])
    use_adapters(mocker, {'ca-1': adapter})

    discovery.process_task({'cloud_account_id': 'ca-1',
                            'resource_type': 'instance'})

    assert sorted(size for _, size in saved_chunks) == [50, 200, 200]
    assert {ca for ca, _ in saved_chunks} == {'ca-1'}
    assert adapter.closed
    updates = discovery_info_updates(rest_cl)
    assert len(updates) == 1 and 'last_discovery_at' in updates[0]


def test_discovery_reports_progress_while_it_works(mocker, discovery,
                                                   saved_chunks):
    use_adapters(mocker, {'ca-1': FakeAdapter([resources('a', 250)])})
    discovery.progress = MagicMock()

    discovery.process_task({'cloud_account_id': 'ca-1',
                            'resource_type': 'instance'})

    # at least once per resource pulled and once per chunk sent
    assert discovery.progress.call_count >= 250 + 1


def test_discovery_errors_are_recorded_and_not_raised(mocker, discovery,
                                                      rest_cl, saved_chunks,
                                                      caplog):
    adapter = FakeAdapter([failing('a', 10, RuntimeError('throttled'))])
    use_adapters(mocker, {'ca-1': adapter})

    discovery.process_task({'cloud_account_id': 'ca-1',
                            'resource_type': 'instance'})

    # resources found before the error are still saved
    assert saved_chunks == [('ca-1', 10)]
    updates = discovery_info_updates(rest_cl)
    assert len(updates) == 1
    assert updates[0]['last_error'] == 'throttled'
    assert 'Resource discovery failed' in caplog.text


def test_disabled_discovery_is_skipped(mocker, discovery, rest_cl,
                                       saved_chunks):
    rest_cl.discovery_info_list.return_value = (
        200, {'discovery_info': [{'id': 'di-1', 'enabled': False}]})
    new_saver = mocker.spy(discovery, 'new_resources_saver')

    discovery.process_task({'cloud_account_id': 'ca-1',
                            'resource_type': 'instance'})

    new_saver.assert_not_called()
    rest_cl.cloud_account_get.assert_not_called()
    assert not saved_chunks


def test_invalid_task_is_logged(discovery, caplog):
    discovery.process_task({'resource_type': 'instance'})
    discovery.process_task('not a dict')
    failures = [r for r in caplog.records
                if r.getMessage().startswith('Resource discovery failed: '
                                             'Invalid task received')]
    assert len(failures) == 2


def test_concurrent_tasks_do_not_lose_each_other_chunks(mocker, discovery,
                                                        saved_chunks):
    """With the old shared saver, one task's pause() made the other task's
    send() drop its chunks"""
    accounts = [f'ca-{i}' for i in range(4)]
    use_adapters(mocker, {
        ca: FakeAdapter([resources(ca, 2 * CHUNK_SIZE + 10)])
        for ca in accounts})
    threads = [
        threading.Thread(target=discovery.process_task, args=(
            {'cloud_account_id': ca, 'resource_type': 'instance'},))
        for ca in accounts]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(WAIT * 2)

    for ca in accounts:
        assert sum(size for c, size in saved_chunks if c == ca) == \
            2 * CHUNK_SIZE + 10


def test_rest_client_is_per_thread(mocker):
    config_cl = MagicMock()
    config_cl.resource_discovery_params.return_value = (None,) * 5
    mocker.patch.object(DiscoveryWorker, 'new_rest_cl',
                        side_effect=lambda: MagicMock())
    discovery = DiscoveryWorker(config_cl)
    main_client = discovery.rest_cl
    assert discovery.rest_cl is main_client
    other = []
    thread = threading.Thread(target=lambda: other.append(discovery.rest_cl))
    thread.start()
    thread.join(WAIT)
    assert other[0] is not main_client


def test_default_settings_when_not_configured():
    config_cl = MagicMock()
    config_cl.resource_discovery_params.return_value = (None,) * 5
    discovery = DiscoveryWorker(config_cl)
    assert discovery.discover_size == worker_module.DEFAULT_DISCOVER_SIZE
    assert discovery.writing_timeout == worker_module.DEFAULT_WRITING_TIMEOUT


# process entry point

def test_touch_liveness_file(tmp_path, monkeypatch):
    path = tmp_path / 'alive'
    monkeypatch.setattr(worker_module, 'LIVENESS_FILE', str(path))
    touch_liveness_file()
    first = path.stat().st_mtime_ns
    time.sleep(0.01)
    touch_liveness_file()
    assert path.stat().st_mtime_ns > first
