import os
import uuid

from datetime import datetime, timedelta
from freezegun import freeze_time
from unittest.mock import patch, PropertyMock, Mock

from cloud_adapter.clouds.azure_fake import AzureFake
from cloud_adapter.clouds.fake_base import encoded_tags
from cloud_adapter.model import *
from cloud_adapter.tests.test_fake_cloud_base import TestFakeCloudBase


class TestAzureFake(TestFakeCloudBase):
    def setUp(self):
        super().setUp()
        azure_config = {
            "subscription_id": "subscription_id",
            "secret": "secret",
            "client_id": "client_id",
            "tenant": "tenant",
            "type": "azure_cnr",
        }
        self.cad = AzureFake(azure_config)

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

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_validate_credentials(self, p_config):
        p_config.return_value = {}
        data = self.cad.validate_credentials()
        self.assertIn('account_id', data)
        self.assertIn('warnings', data)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls(self, p_config):
        regions = {'1': 'germanywestcentral'}
        self.process_discovery_calls(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_dependencies(self, p_config):
        regions = {'1': 'germanywestcentral'}
        self.process_discovery_calls_dependencies(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_tags(self, p_config):
        regions = {'1': 'germanywestcentral'}
        self.process_discovery_calls_tags(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_several_resource_groups(self, p_config):
        regions = {'1': 'germanywestcentral'}
        self.process_discovery_calls_several_resource_groups(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_regions(self, p_config):
        tests = [
            ({'1': 'germanywestcentral', '2': 'canadaeast!11'}, 5),
            ({'1': 'germanywestcentral', '2': 'canadaeast'}, 10)
        ]
        self.process_discovery_calls_regions(tests, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_rediscover(self, p_config):
        regions = {'1': 'germanywestcentral'}
        self.process_discovery_calls_rediscover(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_renew(self, p_config):
        regions = {'1': 'germanywestcentral'}
        self.process_discovery_calls_renew(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_inactive(self, p_config):
        regions = {'1': 'germanywestcentral'}
        self.process_discovery_calls_inactive(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_instance_stopped_allocated(self, p_config):
        p_config.return_value = {
            'objects': {
                'instances': {
                    'common': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '10',
                        'stopped_allocated': 'True'
                    }
                }
            },
            'regions': {'1': 'germanywestcentral'}
        }
        stopped_allocated = False
        for val in range(100):
            for call, params in self.cad.instance_discovery_calls():
                for instance in call(*params):
                    if instance.stopped_allocated:
                        stopped_allocated = True
                        break
        self.assertTrue(stopped_allocated)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_instance_spot(self, p_config):
        p_config.return_value = {
            'objects': {
                'instances': {
                    'common': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '10',
                        'spot': 'True'
                    }
                }
            },
            'regions': {'1': 'germanywestcentral'}
        }
        for call, params in self.cad.instance_discovery_calls():
            for instance in call(*params):
                self.assertTrue(instance.spotted)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_get_usage_active(self, p_config):
        config = {
            'objects': {
                'buckets': {
                    'common': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '1',
                        'first_seen_offset': str(int(
                            timedelta(days=1).total_seconds()))
                    }
                }
            },
            'regions': {'1': 'germanywestcentral'}
        }

        p_config.return_value = config
        organization_id = str(uuid.uuid4())
        cloud_account_id = str(uuid.uuid4())
        now = datetime(day=25, month=2, year=2021, hour=7)
        with freeze_time(now):
            usage = None
            try:
                usage = next(self.cad.get_usage(now.replace(day=1)))
            except StopIteration:
                pass
            self.assertIsNone(usage)

            discovered_resources = []
            for func, params in self.cad.bucket_discovery_calls():
                discovered_resources.extend(func(*params))
            initials = []
            for resource in discovered_resources:
                initials.append(self._create_mongo_resource(
                    resource, cloud_account_id, organization_id, int(now.timestamp())))
            usage = next(self.cad.get_usage(now.replace(day=1)))
            # must be generator to specific model
            self.assertFalse(isinstance(usage, dict))
