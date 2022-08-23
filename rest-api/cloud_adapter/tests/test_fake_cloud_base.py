import mongomock
import unittest
import uuid

from datetime import datetime
from unittest.mock import patch, PropertyMock

from cloud_adapter.model import *
from cloud_adapter.clouds.fake_base import encoded_tags


class TestFakeCloudBase(unittest.TestCase):
    def setUp(self):
        self.etcd_mock = patch('cloud_adapter.clouds.fake_base.get_etcd_client')
        self.etcd_mock.start()
        self.cad = None
        self.mongo_client = mongomock.MongoClient()
        self.resources_collection = self.mongo_client.restapi.resources
        patch('cloud_adapter.clouds.fake_base.FakeBase.mongo_client',
              new_callable=PropertyMock, return_value=self.mongo_client
              ).start()

    def tearDown(self):
        self.etcd_mock.stop()

    def _create_mongo_resource(self, obj, cloud_account_id, organization_id,
                               created_at, first_seen=None, last_seen=None,
                               active=True):
        model_type_map = {
            BucketResource: 'Bucket',
            VolumeResource: 'Volume',
            SnapshotResource: 'Snapshot',
            InstanceResource: 'Instance'
        }
        rss_type = model_type_map.get(type(obj))
        obj = obj.to_dict()
        obj['resource_type'] = rss_type
        obj['organization_id'] = organization_id
        obj['cloud_account_id'] = cloud_account_id
        obj['created_at'] = created_at
        obj['last_seen'] = last_seen if last_seen else created_at
        obj['first_seen'] = first_seen if first_seen else created_at
        obj['active'] = active
        obj['tags'] = encoded_tags(obj['tags'])

        self.mongo_client.restapi.resources.insert_one(obj)
        return obj

    def process_discovery_calls(self, regions, p_config):
        p_config.return_value = {}
        res = []
        for call, params in self.cad.snapshot_discovery_calls():
            res.extend(call(*params))
        self.assertEqual(len(res), 0)

        config = {
            'regions': regions
        }
        for group, func in [
            ('buckets', self.cad.bucket_discovery_calls),
            ('instances', self.cad.instance_discovery_calls),
            ('volumes', self.cad.volume_discovery_calls),
            ('snapshots', self.cad.snapshot_discovery_calls)
        ]:
            config['objects'] = {}
            config['objects'][group] = {
                'common': {
                    'renew_percent': '0',
                    'tags': {},
                    'count': '0'
                }
            }
            p_config.return_value = config
            res = []
            for call, params in func():
                res.extend(call(*params))
            self.assertEqual(len(res), 0)

            config['objects'][group]['common']['count'] = '1'
            p_config.return_value = config
            for call, params in func():
                res.extend(call(*params))
            self.assertEqual(len(res), 1)

    def process_discovery_calls_dependencies(self, regions, p_config):
        config = {
            'regions': regions,
            'objects': {
                'volumes': {
                    'common': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '5'
                    }
                }
            }
        }
        p_config.return_value = config
        res = []
        for call, params in self.cad.snapshot_discovery_calls():
            res.extend(call(*params))
        self.assertEqual(len(res), 1)

    def process_discovery_calls_tags(self, regions, p_config):
        tags = {
            'another': 'tag'
        }
        config = {
            'objects': {
                'buckets': {
                    'common': {
                        'renew_percent': '0',
                        'tags': tags,
                        'count': '5'
                    }
                }
            },
            'regions': regions
        }
        p_config.return_value = config
        res = []
        for call, params in self.cad.bucket_discovery_calls():
            res.extend(call(*params))
        self.assertEqual(len(res), 5)
        for obj in res:
            self.assertIsNotNone(getattr(obj, 'cloud_resource_id'))

    def process_discovery_calls_several_resource_groups(self, regions, p_config):
        config = {
            'objects': {
                'buckets': {
                    'common': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '5'
                    },
                    'uncommon': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '5'
                    }
                }
            },
            'regions': regions
        }
        p_config.return_value = config
        res = []
        for f, obj in self.cad.bucket_discovery_calls():
            res.extend(f(*obj))
        self.assertEqual(len(res), 10)

    def process_discovery_calls_regions(self, tests, p_config):
        config = {
            'objects': {
                'buckets': {
                    'common': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '5'
                    }
                }
            },
        }
        for regions, expected_count in tests:
            config['regions'] = regions
            p_config.return_value = config
            buckets = []
            for f, obj in self.cad.bucket_discovery_calls():
                buckets.extend(f(*obj))
            self.assertEqual(len(buckets), expected_count)

    def process_discovery_calls_rediscover(self, regions, p_config):
        organization_id = str(uuid.uuid4())
        cloud_account_id = str(uuid.uuid4())
        now = int(datetime.utcnow().timestamp())

        for group, func in [
            ('buckets', self.cad.bucket_discovery_calls),
            ('instances', self.cad.instance_discovery_calls),
            ('volumes', self.cad.volume_discovery_calls),
            ('snapshots', self.cad.snapshot_discovery_calls)
        ]:
            p_config.return_value = {
                'objects': {
                    group: {
                        'common': {
                            'renew_percent': '0',
                            'tags': {},
                            'count': '1'
                        }
                    }
                },
                'regions': regions
            }
            res = []
            for call, params in func():
                res.extend(call(*params))
            self.assertEqual(len(res), 1)
            initial = self._create_mongo_resource(
                res[0], cloud_account_id, organization_id, now)

            res.clear()
            for call, params in func():
                res.extend(call(*params))
            self.assertEqual(len(res), 1)
            self.assertEqual(initial['cloud_resource_id'],
                             res[0].cloud_resource_id)

    def process_discovery_calls_renew(self, regions, p_config):
        organization_id = str(uuid.uuid4())
        cloud_account_id = str(uuid.uuid4())
        now = int(datetime.utcnow().timestamp())

        for group, func in [
            ('buckets', self.cad.bucket_discovery_calls),
            ('instances', self.cad.instance_discovery_calls),
            ('volumes', self.cad.volume_discovery_calls),
            ('snapshots', self.cad.snapshot_discovery_calls)
        ]:
            p_config.return_value = {
                'objects': {
                    group: {
                        'common': {
                            'renew_percent': '1',
                            'tags': {},
                            'count': '1'
                        }
                    }
                },
                'regions': regions
            }
            res = []
            for call, params in func():
                res.extend(call(*params))
            self.assertEqual(len(res), 1)
            initial = self._create_mongo_resource(
                res[0], cloud_account_id, organization_id, now)

            res.clear()
            for call, params in func():
                res.extend(call(*params))
            self.assertEqual(len(res), 1)
            self.assertNotEqual(initial['cloud_resource_id'],
                                res[0].cloud_resource_id)

    def process_discovery_calls_inactive(self, regions, p_config):
        for group, func in [
            ('buckets', self.cad.bucket_discovery_calls),
            ('instances', self.cad.instance_discovery_calls),
            ('volumes', self.cad.volume_discovery_calls),
            ('snapshots', self.cad.snapshot_discovery_calls)
        ]:
            p_config.return_value = {
                'objects': {
                    group: {
                        'common': {
                            'renew_percent': '0',
                            'tags': {},
                            'count': '10',
                            'first_seen_offset': '10',
                            'ttl': '5'
                        }
                    }
                },
                'regions': regions
            }
            for call, params in func():
                self.assertEqual(len(call(*params)), 0)
