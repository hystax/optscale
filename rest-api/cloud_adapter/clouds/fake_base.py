import base64
import enum
import hashlib
import json
import logging
import math
import os
import random

from datetime import timedelta, datetime

import config_client.client

from etcd import EtcdKeyNotFound
from pymongo import MongoClient

from cloud_adapter.model import *


LOG = logging.getLogger(__name__)
COUNT_KEY = 'count'
RENEW_PERCENT_KEY = 'renew_percent'
DEFAULT_CHECK_KEY = 'DEADBEEF'
ETCD_TRUE = 'True'
ETCD_FALSE = 'False'


class ResourceKeys(enum.Enum):
    instances = 'instances'
    volumes = 'volumes'
    snapshots = 'snapshots'
    buckets = 'buckets'
    images = 'images'
    users = 'users'

    @classmethod
    def discovery_keys(cls):
        return (cls._member_map_[name] for name
                in cls._member_names_ if name not in [
                    'images', 'users'])


class ResourceTypes(enum.Enum):
    instance = 'Instance'
    volume = 'Volume'
    snapshot = 'Snapshot'
    bucket = 'Bucket'


def encoded_tags(tags, decode=False):
    if not tags:
        return {}
    method = base64.b64decode if decode else base64.b64encode
    new_tags = {}
    for k, v in tags.items():
        new_key = method(k.encode('utf-8')).decode('utf-8')
        new_tags[new_key] = v
    return new_tags


def get_etcd_client():
    return config_client.client.Client(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')))


class FakeBase:
    def __init__(self, *args, **kwargs):
        self.config_cl = get_etcd_client()
        self._mongo_client = None
        self.resource_key_type_map = {
            ResourceKeys.instances: (ResourceTypes.instance.value,
                                     InstanceResource),
            ResourceKeys.volumes: (ResourceTypes.volume.value,
                                   VolumeResource),
            ResourceKeys.snapshots: (ResourceTypes.snapshot.value,
                                     SnapshotResource),
            ResourceKeys.buckets: (ResourceTypes.bucket.value,
                                   BucketResource)
        }
        self._cloud_type = None
        self.config = {}
        super().__init__(*args, **kwargs)

    @property
    def _config(self):
        config = {}
        try:
            config.update(self.config_cl.read_branch('/fake_cad/config'))
        except EtcdKeyNotFound:
            pass
        finally:
            return config.get(self._cloud_type, {})

    @property
    def config_regions(self):
        return list(self._config.get('regions', {}).values())

    @property
    def config_resources(self):
        return self._config.get('objects', {})

    @property
    def mongo_client(self):
        if not self._mongo_client:
            mongo_params = self.config_cl.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_client = MongoClient(mongo_conn_string)
        return self._mongo_client

    @property
    def resources_collection(self):
        return self.mongo_client.restapi.resources

    @property
    def _resource_types(self):
        return [
            ResourceTypes.instance.value,
            ResourceTypes.volume.value,
            ResourceTypes.snapshot.value,
            ResourceTypes.bucket.value
        ]

    def _gen_id(self, resource_key, region, base=None):
        raise NotImplementedError()

    def _get_existing_resources_query(self, resource_type, region,
                                      config_hash):
        raise NotImplementedError()

    def _get_expense_resources_query(self, encoded_config_hash,
                                     resource_types, regions, active=True,
                                     now=0, first_seen=0):
        raise NotImplementedError()

    def _create_volume(self, region, resource_config, config_hash,
                       volume_id=None, attached=False, **kwargs):
        raise NotImplementedError()

    def _create_snapshot(self, region, resource_config, config_hash,
                         snapshot_id=None, **kwargs):
        raise NotImplementedError()

    def _create_bucket(self, region, resource_config, config_hash,
                       bucket_id=None, **kwargs):
        raise NotImplementedError()

    def _create_instance(self, region, resource_config, config_hash,
                         instance_id=None, **kwargs):
        raise NotImplementedError()

    @staticmethod
    def _check_bool_key(config, key, default=ETCD_TRUE):
        return config.get(key, default) == ETCD_TRUE

    @staticmethod
    def _get_config_hash(config):
        return hashlib.md5(
            json.dumps(config, sort_keys=True).encode("utf-8")).hexdigest()

    def _load_existing_resources(self, resource_key, region, config,
                                 config_hash):
        count = int(config.get(COUNT_KEY, 0))
        renew_percent = int(config.get(RENEW_PERCENT_KEY, 0))

        resource_type, model = self.resource_key_type_map.get(
            resource_key, (None, None))
        existing_resources = list(self.resources_collection.find(
            self._get_existing_resources_query(
                resource_type, region, config_hash)
        ).limit(count))

        old_resources_count = count - math.ceil(count * renew_percent / 100)
        if len(existing_resources) > old_resources_count:
            existing_resources = random.sample(
                existing_resources, old_resources_count)
            LOG.debug('Keeping %s %s resources according renew_percent %s',
                      old_resources_count, resource_key, renew_percent)

        result = []
        first_seen_offset = int(config.get('first_seen_offset', 0))
        ttl = int(config.get('ttl', 0))
        now = int(datetime.utcnow().timestamp())
        for existing_resource in existing_resources:
            first_seen = existing_resource['first_seen']
            created_at = existing_resource['created_at']
            if first_seen == created_at:
                first_seen -= first_seen_offset
            if ttl and now - first_seen >= ttl:
                break
            resource = model()
            for f in resource.fields():
                if f in ['meta', 'last_seen', 'active',
                         'last_seen_not_stopped', 'last_attached']:
                    continue
                val = existing_resource.get(f)
                if val is None:
                    val = existing_resource.get('meta', {}).get(f)
                if f == 'tags':
                    val = encoded_tags(val, decode=True)
                if val:
                    setattr(resource, f, val)
            result.append(resource)
        return result

    def _create_resource(self, resource_key, as_dict=False, *args, **kwargs):
        func_map = {
            ResourceKeys.instances: self._create_instance,
            ResourceKeys.volumes: self._create_volume,
            ResourceKeys.snapshots: self._create_snapshot,
            ResourceKeys.buckets: self._create_bucket
        }
        res = func_map.get(resource_key)(*args, **kwargs)
        if res and as_dict:
            res = res.to_dict()
            resource_type, _ = self.resource_key_type_map.get(resource_key)
            res['resource_type'] = resource_type
            res['tags'] = encoded_tags(res.get('tags', {}))
        return res

    def _create_resources(self, resource_key, resource_config, config_hash,
                          as_dict=False):
        result = []
        for region in self.config_regions:
            for _ in range(int(resource_config.get(COUNT_KEY, 0))):
                resource = self._create_resource(
                    resource_key, as_dict, region, resource_config,
                    config_hash)
                result.append(resource)
            result.extend(self._resource_dependencies(
                resource_key, region, resource_config, config_hash, as_dict))
        return result

    def _resource_dependencies(self, resource_key, region, resource_config,
                               config_hash, as_dict=False):
        resource_children_map = {
            ResourceKeys.volumes: [
                (ResourceKeys.snapshots, 'from_snapshot')
            ],
            ResourceKeys.snapshots: [
                (ResourceKeys.volumes, 'from_volume')
            ],
            ResourceKeys.instances: [
                (ResourceKeys.volumes, DEFAULT_CHECK_KEY),
                (ResourceKeys.snapshots, DEFAULT_CHECK_KEY)
            ]
        }
        result = []
        for dest_resource_key, check_key in resource_children_map.get(
                resource_key, []):
            resource_id = self._gen_id(
                dest_resource_key, region, config_hash)
            extra_kwargs = {}
            if (self._is_config_active(resource_config) and
                    dest_resource_key == ResourceKeys.volumes and
                    resource_key == ResourceKeys.instances):
                extra_kwargs['attached'] = True
            result.append(self._create_resource(
                dest_resource_key, as_dict, region, resource_config,
                config_hash, resource_id))
        return result

    @staticmethod
    def _is_config_active(resource_config):
        first_seen_offset = int(resource_config.get('first_seen_offset', 0))
        ttl = int(resource_config.get('ttl', 0))
        return (ttl - first_seen_offset) > 0 or ttl == 0

    def _discover_resources(self, resource_key, region):
        if region not in self._get_coordinates_map().keys():
            LOG.warning('Invalid region %s', region)
            return []

        result = list()
        for config_name, resource_config in self.config_resources.get(
                resource_key.value, {}).items():
            count = int(resource_config.get(COUNT_KEY, 0))
            # inactive resources are out of discovery scope
            if not count or not self._is_config_active(resource_config):
                LOG.debug('Skipping %s/%s', resource_key, config_name)
                continue
            LOG.info('Discovering %s/%s resources', resource_key, config_name)
            config_hash = self._get_config_hash(resource_config)
            existing_resources = self._load_existing_resources(
                resource_key, region, resource_config, config_hash)
            result.extend(existing_resources)

            for _ in range(count - len(existing_resources)):
                resource = self._create_resource(
                    resource_key, False, region, resource_config,
                    config_hash)
                result.append(resource)

        result.extend(self._discover_dependencies(resource_key, region))
        return result

    def _discover_dependencies(self, dest_resource_key, region):
        resource_parents_map = {
            ResourceKeys.snapshots: [
                (ResourceKeys.volumes, 'from_snapshot'),
                (ResourceKeys.instances, DEFAULT_CHECK_KEY)
            ],
            ResourceKeys.volumes: [
                (ResourceKeys.snapshots, 'from_volume'),
                (ResourceKeys.instances, DEFAULT_CHECK_KEY)
            ]
        }
        result = []
        config = self.config_resources
        for resource_key, check_key in resource_parents_map.get(
                dest_resource_key, []):
            for config_name, resource_config in config.get(
                    resource_key.value, {}).items():
                # no need to discover volumes for inactive instances
                if (not self._is_config_active(resource_config) and
                        resource_key == ResourceKeys.instances and
                        dest_resource_key == ResourceKeys.volumes):
                    continue
                if not self._check_bool_key(resource_config, check_key):
                    continue
                config_hash = self._get_config_hash(resource_config)
                resource_id = self._gen_id(
                    dest_resource_key, region, config_hash)
                extra_kwargs = {}
                if (dest_resource_key == ResourceKeys.volumes and
                        resource_key == ResourceKeys.instances):
                    extra_kwargs['attached'] = True
                LOG.debug('Discovered dependent resource %s for %s/%s',
                          dest_resource_key, resource_key, config_name)
                resource = self._create_resource(
                    dest_resource_key, False, region, resource_config,
                    config_hash, resource_id, **extra_kwargs)
                result.append(resource)
        return result

    @staticmethod
    def _date_range(start_date, end_date):
        for n in range(int((FakeBase._day_end(
                end_date) + timedelta(days=1) - FakeBase._day_end(start_date)
                           ).days)):
            yield start_date + timedelta(n)

    @staticmethod
    def _day_start(dt):
        return dt.replace(hour=0, minute=0, second=0)

    @staticmethod
    def _day_end(dt):
        return dt.replace(hour=23, minute=59, second=59, microsecond=0)

    def _get_expense_record(self, resource, usage_start, usage_end):
        raise NotImplementedError()

    def _get_expenses(self, date_start, date_end):
        now = int(datetime.utcnow().timestamp())
        for resource_key, resource_configs in self.config_resources.items():
            try:
                resource_key = ResourceKeys(resource_key)
            except ValueError:
                LOG.warning('Unsupported resource key %s', resource_key)
                continue
            if resource_key not in ResourceKeys.discovery_keys():
                continue
            for config_name, resource_config in resource_configs.items():
                first_seen_offset = int(resource_config.get(
                    'first_seen_offset', 0))
                ttl = int(resource_config.get('ttl', 0))
                config_hash = self._get_config_hash(resource_config)
                active = self._is_config_active(resource_config)
                encoded_config_hash = encoded_tags(
                    {'group_config_hash': [config_hash]})
                query = self._get_expense_resources_query(
                    encoded_config_hash, self._resource_types,
                    self.config_regions, active, now, now - first_seen_offset)
                resources = list(self.resources_collection.find(query))
                resource_type, _ = self.resource_key_type_map.get(resource_key)
                is_config_resources = any(filter(
                    lambda x: x['resource_type'] == resource_type, resources))
                if not active and not is_config_resources:
                    LOG.info(
                        'Generating resources for inactive config %s/%s',
                        resource_key, config_name)
                    resources = self._create_resources(
                        resource_key, resource_config, config_hash,
                        as_dict=True)
                LOG.info('Generating %s/%s expenses',
                         resource_key, config_name)
                for resource in resources:
                    created_at = resource.get('created_at', now)
                    first_seen = resource.get('first_seen', now)
                    if (first_seen_offset and
                            created_at - first_seen < first_seen_offset):
                        first_seen -= first_seen_offset
                    first_seen = datetime.fromtimestamp(first_seen)
                    if first_seen > date_end:
                        continue
                    range_start = date_start
                    if first_seen > range_start:
                        range_start = first_seen
                    range_end = date_end
                    # dependent resources are not limited by ttl
                    if resource['resource_type'] == resource_type and ttl:
                        last_seen = first_seen + timedelta(seconds=ttl)
                        if last_seen < range_end:
                            range_end = last_seen
                    LOG.debug('Generating %s expenses for %s - %s',
                              resource['cloud_resource_id'], range_start,
                              range_end)
                    for day in self._date_range(range_start, range_end):
                        usage_start = self._day_start(day)
                        if usage_start < range_start:
                            usage_start = range_start
                        usage_end = self._day_end(day)
                        if usage_end > range_end:
                            usage_end = range_end
                        res = self._get_expense_record(
                            resource, usage_start, usage_end)
                        if res:
                            yield res

    def validate_credentials(self, org_id=None):
        raise NotImplementedError()

    def set_currency(self, currency):
        pass
