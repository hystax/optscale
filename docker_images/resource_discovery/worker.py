#!/usr/bin/env python
import os
import time
import traceback

from concurrent.futures.thread import ThreadPoolExecutor
from threading import Event, Thread
import queue
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu import Exchange, Queue
import urllib3

from tools.cloud_adapter.cloud import Cloud as CloudAdapter
from tools.cloud_adapter.exceptions import InvalidResourceTypeException
from tools.cloud_adapter.model import (
    ResourceTypes, RES_MODEL_MAP, InstanceResource, RdsInstanceResource,
    RedshiftClusterResource, EmrApplicationResource
)
from tools.optscale_time import utcnow, utcnow_timestamp
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.insider_client.client import Client as InsiderClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient


BYTES_IN_MB = 1024 * 1024
CHUNK_SIZE = 200
EXCHANGE_NAME = 'resource-discovery'
QUEUE_NAME = 'discovery'
MAX_PARALLEL_REQUESTS = 50
task_exchange = Exchange(EXCHANGE_NAME, type='direct')
task_queue = Queue(QUEUE_NAME, task_exchange, routing_key=QUEUE_NAME)
LOG = get_logger(__name__)
DEFAULT_DISCOVER_SIZE = 10000


class ResourcesSaver:

    MODEL_MAP_INVERTED = {v: k for k, v in RES_MODEL_MAP.items()}

    def __init__(self, rest_cl, insider_cl, limit, timeout, pause_timeout):
        queue_len = int(limit / CHUNK_SIZE) if CHUNK_SIZE else 0
        self.queue = queue.Queue(queue_len)
        self.insider_cl = insider_cl
        self.rest_cl = rest_cl
        self.timeout = timeout
        self.pause_timeout = pause_timeout
        self.recording_available = Event()
        self.empty = Event()
        self._proc = None
        self.start()

    def __del__(self):
        self.stop()

    def start(self):
        self.proc.start()
        self.resume()

    def stop(self):
        self.pause()
        if self._proc:
            self.proc.join()

    def shutdown(self):
        self.pause()
        if self.queue.qsize():
            LOG.warning('Shutdown a resource saver with a non-empty queue')
        self.queue.queue.clear()
        if self._proc:
            self.proc.join()

    def pause(self):
        self.recording_available.clear()

    def resume(self):
        self.recording_available.set()

    def send(self, chunk):
        try:
            recording_available = self.recording_available.wait(
                timeout=self.pause_timeout)
            if recording_available:
                self.queue.put(chunk, timeout=self.timeout)
            else:
                LOG.exception('Failed to add a chunk to the queue: '
                              'writing paused, timeout exceeded')
        except queue.Full as exc:
            LOG.exception('Failed to add a chunk to the queue: %s', str(exc))

    @property
    def proc(self):
        if self._proc is None:
            self._proc = Thread(target=self._save_chunks)
        return self._proc

    @property
    def is_finished(self):
        return self.empty.wait(
            self.pause_timeout) and not self.recording_available.is_set()

    def _save_chunks(self):
        while True:
            try:
                chunk = self.queue.get(timeout=1)
                self.empty.clear()
                self.save_bulk_resources(chunk)
            except queue.Empty:
                self.empty.set()
            except Exception as exc:
                LOG.warning('Failed to save a chunk: %s', str(exc))

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
            if type(resource) not in [InstanceResource, RdsInstanceResource]:
                break
            flavor_name = resource.flavor
            if resource.cloud_type == 'azure_cnr':
                flavor = flavors.get(flavor_name)
                if not flavor:
                    if not resource_type:
                        resource_type = getattr(
                            ResourceTypes, self.MODEL_MAP_INVERTED[
                                type(resource)]).name
                    _, flavor = self.insider_cl.find_flavor(
                        resource.cloud_type, resource_type, resource.region,
                        {'source_flavor_id': flavor_name}, 'current',
                        cloud_account_id=resource.cloud_account_id)
                if flavor:
                    flavors[flavor_name] = flavor
                    resource.cpu_count = flavor['cpu']
                    resource.ram = flavor['ram'] * BYTES_IN_MB
            if (not resource.architecture and
                    isinstance(resource, InstanceResource) and
                    resource.cloud_type in [
                        'aws_cnr', 'azure_cnr', 'alibaba_cnr'
                    ]):
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
        for resource in resources:
            try:
                resource.post_discover()
            except Exception as exc:
                LOG.error('Post discover actions failed: %s', str(exc))


class DiscoveryWorker(ConsumerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl
        self.set_discover_settings()
        self._insider_cl = None
        self._rest_cl = None
        self._res_saving = None
        self.running = True
        self.thread = Thread(target=self.heartbeat)
        self.thread.start()

    def __del__(self):
        if self._res_saving:
            self.res_saving.shutdown()

    @property
    def insider_cl(self):
        if not self._insider_cl:
            self._insider_cl = InsiderClient(
                url=self.config_cl.insider_url(),
                secret=self.config_cl.cluster_secret())
        return self._insider_cl

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._rest_cl

    @property
    def res_saving(self):
        if self._res_saving is None:
            self._res_saving = ResourcesSaver(
                insider_cl=self.insider_cl,
                rest_cl=self.rest_cl,
                limit=self.discover_size,
                timeout=self.timeout,
                pause_timeout=self.writing_timeout
            )
        return self._res_saving

    def set_discover_settings(self):
        (discover_size, timeout, writing_timeout,
         _, _) = self.config_cl.resource_discovery_params()
        self.discover_size = discover_size if (
            discover_size) else DEFAULT_DISCOVER_SIZE
        self.timeout = timeout
        self.writing_timeout = writing_timeout

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[task_queue], accept=['json'],
                         callbacks=[self.process_task], prefetch_count=1)]

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
            return res
        adapter = CloudAdapter.get_adapter(config)
        max_parallel_requests = self.max_parallel_requests(config)
        with ThreadPoolExecutor(
                max_workers=max_parallel_requests) as executor:
            try:
                discover_calls = adapter.get_discovery_calls(resource_type)
            except InvalidResourceTypeException:
                LOG.exception('Discovery calls for resource type %s are '
                              'not found', resource_type)
                return res
            futures = []
            for call in discover_calls:
                futures.append(executor.submit(call[0], *call[1]))
            for f in futures:
                res.append(f.result())
        return res

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
        gen_list = self.discover(config, resource_type)
        discovered_resources = set()
        resources_count = 0
        max_parallel_requests = self.max_parallel_requests(config)
        errors = set()
        for i in range(0, len(gen_list), max_parallel_requests):
            gen_list_chunk = gen_list[i:i + max_parallel_requests]
            while gen_list_chunk:
                futures = []
                with ThreadPoolExecutor(
                        max_workers=max_parallel_requests) as executor:
                    for gen in gen_list_chunk:
                        futures.append(
                            executor.submit(self.extract_from_generator, gen))
                for f in futures:
                    res, gen = f.result()
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
                        self.res_saving.send(discovered_resources)
                        discovered_resources.clear()
        if len(discovered_resources):
            resources_count += len(discovered_resources)
            self.res_saving.send(discovered_resources)
        LOG.info("%s %s resources have been discovered for cloud %s",
                 resources_count, resource_type, cloud_acc_id)
        self.res_saving.pause()
        if not self.res_saving.is_finished:
            LOG.warning('The timeout for writing %s resources for the'
                        ' cloud account %s has been exceeded',
                        resource_type, cloud_acc_id)
        self.res_saving.resume()
        if errors:
            LOG.error('%s discovery call failed for cloud %s with errors %s',
                      resource_type, cloud_acc_id, errors)
            raise Exception(next(iter(errors)))
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

    def process_task(self, body, message):
        try:
            self.discover_resources(body)
        except Exception as exc:
            LOG.exception('Resource discovery failed: %s', str(exc))
        message.ack()

    def heartbeat(self):
        while self.running:
            self.connection.heartbeat_check()
            time.sleep(1)


if __name__ == '__main__':
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
    with Connection(conn_str) as conn:
        try:
            worker = DiscoveryWorker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.thread.join()
            LOG.info('Shutdown received')
