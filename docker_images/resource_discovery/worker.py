#!/usr/bin/env python
import logging
import os
import resource
import threading
import time
import traceback
from etcd import EtcdKeyError

from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from threading import Event, Thread
import queue
from kombu.log import get_logger
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu import Exchange, Queue
import urllib3

from docker_images.resource_discovery.consumer import ConcurrentConsumer
from tools.cloud_adapter.cloud import Cloud as CloudAdapter
from tools.cloud_adapter.exceptions import InvalidResourceTypeException
from tools.cloud_adapter.model import (
    ResourceTypes, RES_MODEL_MAP, InstanceResource, RdsInstanceResource
)
from tools.cloud_adapter.clouds.gcp import GcpInstance
from tools.optscale_time import utcnow, utcnow_timestamp
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.insider_client.client import Client as InsiderClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient


BYTES_IN_MB = 1024 * 1024
BYTES_IN_GB = BYTES_IN_MB * 1024
CHUNK_SIZE = 200
EXCHANGE_NAME = 'resource-discovery'
QUEUE_NAME = 'discovery'
MAX_PARALLEL_REQUESTS = 50
task_exchange = Exchange(EXCHANGE_NAME, type='direct')
task_queue = Queue(QUEUE_NAME, task_exchange, routing_key=QUEUE_NAME)
LOG = get_logger(__name__)
DEFAULT_DISCOVER_SIZE = 10000
# used when resource_discovery_settings.timeout / writing_timeout are empty
DEFAULT_PUT_TIMEOUT = 600
DEFAULT_WRITING_TIMEOUT = 600
# AMQP heartbeat: safe because the I/O thread never runs task code
AMQP_HEARTBEAT = 30
# the k8s liveness probe fails when this file is older than 90 seconds
LIVENESS_FILE = '/tmp/worker-alive'


def get_current_rss_mb():
    """Current resident set size in MB, read from /proc"""
    try:
        with open('/proc/self/status') as f:
            for line in f:
                if line.startswith('VmRSS:'):
                    return int(line.split()[1]) / 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


class ResourcesNotSaved(Exception):
    """The saver stopped making progress; the task must not complete"""


class ResourcesSaver:

    MODEL_MAP_INVERTED = {
        GcpInstance: ResourceTypes.instance.name,
        **{v: k for k, v in RES_MODEL_MAP.items()}
    }

    # how often the task thread and the saver thread check on each other
    POLL_SECONDS = 1

    def __init__(self, rest_cl, insider_cl, limit, timeout,
                 product_tracking_id, progress=None):
        """Saves discovered resources of ONE task in a background thread.

        Create one saver per task: savers share no state, so concurrent
        tasks cannot block or drop each other's chunks.

        The saver never outlives its task: send() and close() wait for the
        saver thread, and give up (abort the saver, raise/report) only when
        it has not completed a single chunk for `timeout` seconds. The
        bounded queue therefore gives backpressure as before: a slow
        rest_api slows discovery down, it never makes chunks pile up.

        :param timeout: seconds without a completed chunk after which the
            saver is considered stuck
        :param progress: callable(), invoked whenever a chunk is completed
            while the task thread is waiting on the saver
        """
        queue_len = int(limit / CHUNK_SIZE) if CHUNK_SIZE else 0
        self.queue = queue.Queue(queue_len)
        self.insider_cl = insider_cl
        self.rest_cl = rest_cl
        self.timeout = timeout or DEFAULT_PUT_TIMEOUT
        self.product_tracking_id = product_tracking_id
        self.progress = progress or (lambda: None)
        # counters: sent is written by the task thread, saved and failed
        # by the saver thread
        self.sent = 0
        self.saved = 0
        self.failed = 0
        self._closing = Event()
        self._aborted = Event()
        # daemon: a stuck saver must never keep a dead process alive
        self._thread = Thread(target=self._save_chunks, daemon=True,
                              name='resources-saver')
        self._thread.start()

    @property
    def unsaved(self):
        """Chunks handed to send() that were not written (yet)"""
        return self.sent - self.saved

    def _completed(self):
        return self.saved + self.failed

    def send(self, chunk):
        """Queue a chunk, waiting for a free slot while the saver is slow.

        :raises ResourcesNotSaved: the saver completed no chunk for
            `timeout` seconds; it is aborted and the task must fail
        """
        self.sent += 1
        if not self._wait(lambda: self._try_put(chunk)):
            raise ResourcesNotSaved(
                f'the saver did not complete a chunk in {self.timeout} '
                f'seconds, {self.unsaved} chunks were not saved')

    def _try_put(self, chunk):
        try:
            self.queue.put(chunk, timeout=self.POLL_SECONDS)
            return True
        except queue.Full:
            return False

    def close(self, timeout):
        """Wait until every queued chunk is written, then stop the saver.

        :param timeout: seconds without a completed chunk after which the
            saver is aborted and the remaining chunks are given up
        :return: the number of chunks that were not saved (0 on success)
        """
        self._closing.set()
        if self._aborted.is_set():      # send() already gave up
            return self.unsaved
        if not self._wait(self._joined, timeout):
            LOG.error('The saver did not complete a chunk in %s seconds, '
                      'giving up on %s chunks', timeout, self.unsaved)
        return self.unsaved

    def _joined(self):
        self._thread.join(self.POLL_SECONDS)
        return not self._thread.is_alive()

    def _wait(self, done, timeout=None):
        """Run `done()` until it returns True. Called from the task thread.

        Every completed chunk counts as progress and resets the timeout; the
        saver is aborted and False is returned when no chunk is completed
        for `timeout` seconds.
        """
        timeout = self.timeout if timeout is None else timeout
        completed = self._completed()
        deadline = time.monotonic() + timeout
        while not self._aborted.is_set():
            finished = done()
            if self._completed() != completed:
                completed = self._completed()
                self.progress()
                deadline = time.monotonic() + timeout
            if finished:
                return True
            if time.monotonic() >= deadline:
                self._aborted.set()
        return False

    def _save_chunks(self):
        while not self._aborted.is_set():
            try:
                chunk = self.queue.get(timeout=self.POLL_SECONDS)
            except queue.Empty:
                # only stop once everything that was queued has been saved
                if self._closing.is_set():
                    return
                continue
            try:
                self.save_bulk_resources(chunk)
                self.saved += 1
            except Exception as exc:
                LOG.warning('Failed to save a chunk: %s', str(exc))
                self.failed += 1

    @staticmethod
    def get_resource_type_model(resource_type):
        try:
            return RES_MODEL_MAP[resource_type]
        except KeyError:
            raise Exception(f'Invalid resource type {resource_type}')

    def build_payload(self, resource):
        obj = {}
        for field in resource.fields(meta_fields_incl=False):
            val = getattr(resource, field)
            if val is not None and (isinstance(val, bool) or val):
                obj[field] = val
        for param in ['resource_id', 'organization_id', 'cloud_type']:
            obj.pop(param, None)
        for cl, resource_type in self.MODEL_MAP_INVERTED.items():
            if issubclass(type(resource), cl):
                obj['resource_type'] = getattr(ResourceTypes,
                                               resource_type).value
        obj['last_seen'] = utcnow_timestamp()
        obj['active'] = True
        cloud_acc_id = obj.pop('cloud_account_id')
        return obj, cloud_acc_id

    def process_resource_obj(self, resources):
        flavors = {}
        flavor_archs = {}
        resource_type = None
        for resource in resources:
            if type(resource) not in [InstanceResource, RdsInstanceResource, GcpInstance]:
                break
            flavor_name = resource.flavor
            if resource.cloud_type in ['azure_cnr', 'aws_cnr', 'gcp_cnr']:
                if flavor_name in flavors:
                    flavor = flavors[flavor_name]
                else:
                    flavor = None
                    if not resource_type:
                        resource_type = getattr(
                            ResourceTypes, self.MODEL_MAP_INVERTED[
                                type(resource)]).name
                    try:
                        _, flavor = self.insider_cl.find_flavor(
                            resource.cloud_type, resource_type, resource.region,
                            {'source_flavor_id': flavor_name}, 'current',
                            cloud_account_id=resource.cloud_account_id)
                    except Exception as exc:
                        LOG.warning('Unable to find flavor %s for '
                                    'cloud account %s: %s', flavor_name,
                                    resource.cloud_account_id, str(exc))
                    # Not found flavors are cached too, to not call insider
                    # several times
                    flavors[flavor_name] = flavor
                if flavor:
                    resource.cpu_count = flavor['cpu']
                    multiplier = BYTES_IN_MB
                    if resource.cloud_type == 'gcp_cnr':
                        multiplier = BYTES_IN_GB
                    resource.ram = flavor['ram'] * multiplier
            if (hasattr(resource, 'architecture') and
                    not resource.architecture and resource.cloud_type in [
                        'aws_cnr', 'azure_cnr', 'alibaba_cnr']):
                flavor_arch = flavor_archs.get(flavor_name)
                if not flavor_arch:
                    _, arch_info = self.insider_cl.get_architecture(
                        cloud_type=resource.cloud_type,
                        flavor=resource.flavor,
                        region=resource.region,
                        cloud_account_id=resource.cloud_account_id
                    )
                    flavor_arch = arch_info['architecture']
                    flavor_archs[flavor_name] = flavor_arch
                resource.architecture = flavor_arch
        return resources

    def save_bulk_resources(self, resources):
        payload = []
        resources = self.process_resource_obj(resources)
        cloud_acc_id = None
        for rss in resources:
            obj, cloud_acc_id = self.build_payload(rss)
            payload.append(obj)
        if payload:
            LOG.info('Creating %s resources for cloud account %s', len(payload),
                     cloud_acc_id)
            LOG.debug('Payload build for cloud account %s resources: %s',
                      cloud_acc_id, [x['cloud_resource_id'] for x in payload])
            _, response = self.rest_cl.cloud_resource_create_bulk(
                cloud_acc_id, {'resources': payload},
                behavior='update_existing', return_resources=True)
        for res in resources:
            try:
                res.post_discover(tracking_id=self.product_tracking_id)
            except Exception as exc:
                LOG.error('Post discover actions failed: %s', str(exc))


class DiscoveryWorker:
    """Resource discovery business logic.

    Knows nothing about RabbitMQ: `process_task` is called by
    ConcurrentConsumer from its task threads, possibly concurrently. HTTP
    clients are therefore per thread, and every task gets its own
    ResourcesSaver.
    """

    def __init__(self, config_cl, progress=None):
        """
        :param progress: callable(), invoked whenever a task does real work
            (a page of resources received, a chunk handed to the saver). The
            consumer uses it to tell a slow task from a hung one.
        """
        self.config_cl = config_cl
        self.progress = progress or (lambda: None)
        self.set_discover_settings()
        self._local = threading.local()
        self._product_tracking_id = None

    @property
    def product_tracking_id(self):
        if not self._product_tracking_id:
            try:
                self._product_tracking_id = self.config_cl.product_tracking_id()
            except EtcdKeyError:
                self._product_tracking_id = None
            if not self._product_tracking_id:
                raise Exception('product_tracking_id is not set')
        return self._product_tracking_id

    def new_insider_cl(self):
        return InsiderClient(
            url=self.config_cl.insider_url(),
            secret=self.config_cl.cluster_secret())

    def new_rest_cl(self):
        return RestClient(
            url=self.config_cl.restapi_url(),
            secret=self.config_cl.cluster_secret(),
            verify=False)

    @property
    def rest_cl(self):
        # requests.Session is not guaranteed to be thread safe
        if getattr(self._local, 'rest_cl', None) is None:
            self._local.rest_cl = self.new_rest_cl()
        return self._local.rest_cl

    def new_resources_saver(self):
        # own clients: the saver runs in its own thread
        return ResourcesSaver(
            insider_cl=self.new_insider_cl(),
            rest_cl=self.new_rest_cl(),
            limit=self.discover_size,
            timeout=self.timeout,
            product_tracking_id=self.product_tracking_id,
            progress=self.progress,
        )

    def set_discover_settings(self):
        (discover_size, timeout, writing_timeout,
         _, _) = self.config_cl.resource_discovery_params()
        self.discover_size = discover_size if (
            discover_size) else DEFAULT_DISCOVER_SIZE
        self.timeout = timeout
        self.writing_timeout = writing_timeout or DEFAULT_WRITING_TIMEOUT

    def get_config(self, cloud_account_id):
        _, cloud_account = self.rest_cl.cloud_account_get(cloud_account_id)
        cloud_account.update(cloud_account.get('config', {}))
        if cloud_account['type'] == 'kubernetes_cnr':
            cloud_account['url'] = self.config_cl.thanos_query_url()
        return cloud_account

    def check_discover_enabled(self, cloud_account_id, resource_type):
        _, di_info_list = self.rest_cl.discovery_info_list(
            cloud_account_id, resource_type=resource_type)
        enabled = True
        for di_info in di_info_list.get('discovery_info', []):
            enabled = di_info['enabled']
            break
        return enabled

    def is_org_disabled(self, organization_id):
        _, org = self.rest_cl.organization_get(organization_id)
        return org.get('disabled')

    @staticmethod
    def max_parallel_requests(config):
        # check if MAX_PARALLEL_REQUESTS is set for cloud adapter
        # otherwise use default parallelism
        adapter = CloudAdapter.get_adapter(config)
        return getattr(adapter, 'MAX_PARALLEL_REQUESTS', MAX_PARALLEL_REQUESTS)

    def discover(self, config, resource_type):
        res = []
        if not config:
            return res, None
        adapter = CloudAdapter.get_adapter(config)
        max_parallel_requests = self.max_parallel_requests(config)
        try:
            with ThreadPoolExecutor(
                    max_workers=max_parallel_requests) as executor:
                try:
                    discover_calls = adapter.get_discovery_calls(
                        resource_type)
                except InvalidResourceTypeException:
                    LOG.exception('Discovery calls for resource type %s are '
                                  'not found', resource_type)
                    return res, adapter
                futures = []
                for call in discover_calls:
                    futures.append(executor.submit(call[0], *call[1]))
                for f in futures:
                    res.append(f.result())
                    self.progress()
        except Exception:
            adapter.close()
            raise
        return res, adapter

    @staticmethod
    def extract_from_generator(generator):
        try:
            return next(generator), generator
        except StopIteration:
            return None, generator
        except Exception as exc:
            return exc, generator

    @staticmethod
    def is_404(exception):
        try:
            not_found = exception.response.status_code == 404
        except Exception:
            not_found = False
        return not_found

    def _discover_and_save(self, cloud_acc_id, resource_type, config, saver):
        discovered_resources = set()
        resources_count = 0
        errors = set()
        adapter = None
        try:
            max_parallel_requests = self.max_parallel_requests(config)
            gen_list, adapter = self.discover(config, resource_type)
            with ThreadPoolExecutor(
                    max_workers=max_parallel_requests) as executor:
                for i in range(0, len(gen_list), max_parallel_requests):
                    gen_list_chunk = gen_list[i:i + max_parallel_requests]
                    while gen_list_chunk:
                        futures = [
                            executor.submit(self.extract_from_generator, gen)
                            for gen in gen_list_chunk]
                        for f in futures:
                            res, gen = f.result()
                            self.progress()
                            if isinstance(res, Exception):
                                if self.is_404(res):
                                    LOG.debug("Got 404 exception: %s, skipping it",
                                              str(res))
                                    continue
                                LOG.error("Exception: %s %s", str(res),
                                          traceback.print_tb(res.__traceback__))
                                gen_list_chunk.remove(gen)
                                errors.add(str(res))
                            elif res:
                                res.cloud_account_id = cloud_acc_id
                                res.cloud_type = config['type']
                                discovered_resources.add(res)
                            else:
                                gen_list_chunk.remove(gen)
                            if len(discovered_resources) >= CHUNK_SIZE:
                                resources_count += len(discovered_resources)
                                saver.send(discovered_resources)
                                self.progress()
                                discovered_resources = set()
        finally:
            if adapter is not None:
                adapter.close()
        if len(discovered_resources):
            resources_count += len(discovered_resources)
            saver.send(discovered_resources)
        return resources_count, errors

    def _discover_resources(self, cloud_acc_id, resource_type):
        LOG.info('Starting %s discovery for cloud_account %s',
                 resource_type, cloud_acc_id)
        start_time = utcnow()
        if not self.check_discover_enabled(cloud_acc_id, resource_type):
            LOG.info('Discover of cloud account id %s for resource type %s is '
                     'not enabled. Discover will be skipped.', cloud_acc_id,
                     resource_type)
            return
        config = self.get_config(cloud_acc_id)
        if self.is_org_disabled(config['organization_id']):
            LOG.info('Discover of cloud account id %s for resource type %s is '
                     'skipped due to disabled organization.', cloud_acc_id,
                     resource_type)
            return
        saver = self.new_resources_saver()
        try:
            resources_count, errors = self._discover_and_save(
                cloud_acc_id, resource_type, config, saver)
        finally:
            unsaved = saver.close(timeout=self.writing_timeout)
        LOG.info("%s %s resources have been discovered for cloud %s",
                 resources_count, resource_type, cloud_acc_id)
        if errors:
            LOG.error('%s discovery call failed for cloud %s with errors %s',
                      resource_type, cloud_acc_id, errors)
            raise Exception(next(iter(errors)))
        if unsaved:
            # last_discovery_at must not move: resource_observer marks every
            # resource with last_seen < last_discovery_at as inactive, which
            # would hit the resources of the chunks that were not written
            raise ResourcesNotSaved(
                f'{unsaved} chunks of {resource_type} resources were not '
                f'saved for cloud account {cloud_acc_id}')
        self._update_discovery_info(
            cloud_acc_id, resource_type,
            last_discovery_at=int(start_time.timestamp()))
        LOG.info('%s discovery for cloud_account %s completed in %s',
                 resource_type, cloud_acc_id,
                 (utcnow() - start_time).total_seconds())

    def discover_resources(self, task):
        cloud_acc_id = task.get('cloud_account_id')
        resource_type = task.get('resource_type')
        if not resource_type or not cloud_acc_id:
            raise Exception('Invalid task received: {}'.format(task))
        try:
            self._discover_resources(cloud_acc_id, resource_type)
        except Exception as ex:
            self._update_discovery_info(
                cloud_acc_id, resource_type,
                last_error_at=utcnow_timestamp(),
                last_error=str(ex)[:1024])
            raise

    def _update_discovery_info(self, cloud_acc_id, resource_type, **kwargs):
        _, di_info_list = self.rest_cl.discovery_info_list(
            cloud_acc_id, resource_type=resource_type)
        for di_info in di_info_list.get('discovery_info', []):
            self.rest_cl.discovery_info_update(
                di_info['id'], kwargs)

    def process_task(self, body):
        body = body if isinstance(body, dict) else {}
        try:
            self.discover_resources(body)
        except Exception as exc:
            LOG.exception('Resource discovery failed: %s', str(exc))
        finally:
            # ru_maxrss is the process' peak resident set size so far (KB on
            # Linux) - monotonically non-decreasing, so logging it after
            # every task lets us correlate RSS growth with a specific
            # cloud_account_id/resource_type task and with thread count.
            # current_rss_mb (from /proc) is the actual usage right now,
            # for comparison - unlike ru_maxrss it can go down.
            max_rss_mb = resource.getrusage(
                resource.RUSAGE_SELF).ru_maxrss / 1024
            current_rss_mb = get_current_rss_mb()
            LOG.info(
                'RSS after task cloud_account_id=%s resource_type=%s: '
                'peak=%.1f MB, current=%s MB, active threads=%s',
                body.get('cloud_account_id'), body.get('resource_type'),
                max_rss_mb,
                f'{current_rss_mb:.1f}' if current_rss_mb is not None else 'n/a',
                threading.active_count())


def touch_liveness_file():
    """Refresh the file checked by the k8s liveness probe"""
    Path(LIVENESS_FILE).touch()


def main():
    urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()
    params = config_cl.resource_discovery_params()
    log_level = 'INFO' if not params[-1] else 'DEBUG'
    setup_logging(loglevel=log_level, loggers=[''])
    conn_str = 'amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit'))
    # /resource_discovery_settings in etcd; read once, at startup
    concurrency, max_stall_seconds = config_cl.resource_discovery_worker_params()
    worker = DiscoveryWorker(config_cl)
    consumer = ConcurrentConsumer(
        Connection(conn_str, heartbeat=AMQP_HEARTBEAT), task_queue,
        worker.process_task, concurrency=concurrency,
        max_stall_seconds=max_stall_seconds, on_healthy=touch_liveness_file)
    # tasks report progress to the consumer so that a slow task is not
    # mistaken for a hung one
    worker.progress = consumer.progress
    LOG.info('Starting discovery worker: concurrency=%s, max_stall_seconds=%s',
             concurrency, max_stall_seconds)
    try:
        consumer.run()
    except BaseException:  # pylint: disable=broad-exception-caught
        LOG.exception('Consumer loop died, exiting')
    # run() only returns by raising. Exit hard: a normal exit joins every
    # pool thread, so a task stuck in a blocking call would keep the dead
    # process alive forever (a "zombie" pod). os._exit skips that, and also
    # skips flushing, hence logging.shutdown() first.
    logging.shutdown()
    os._exit(1)


if __name__ == '__main__':
    main()
