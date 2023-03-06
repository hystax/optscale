import os
import uuid

from calendar import monthrange
from datetime import datetime, timezone, timedelta
from freezegun import freeze_time
from unittest.mock import patch, PropertyMock, Mock

from cloud_adapter.clouds.aws_fake import AwsFake
from cloud_adapter.model import BucketResource
from cloud_adapter.tests.test_fake_cloud_base import TestFakeCloudBase


class TestAwsFake(TestFakeCloudBase):
    def setUp(self):
        super().setUp()
        aws_config = {
            "type": "aws_cnr",
            "report_name": "report_name",
            "access_key_id": "access_key_id",
            "bucket_name": "bucket_name",
            "bucket_prefix": "bucket_prefix",
            "secret_access_key": "secret_access_key",
            "linked": False,
            'config_scheme': 'bucket_only'
        }
        self.cad = AwsFake(aws_config)

    @staticmethod
    def _dates_from_group(date_group):
        dates = date_group.split('-')
        return datetime.strptime(dates[0], '%Y%m%d'), datetime.strptime(
            dates[-1], '%Y%m%d')

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_validate_credentials(self, p_config):
        p_config.return_value = {}
        data = self.cad.validate_credentials()
        self.assertIn('account_id', data)
        self.assertIn('warnings', data)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_list_users(self, p_config):
        config = {
            'objects': {
                'users': {
                    'access_key_active': {
                        'count': '0',
                        'creation_offset': '7862400',
                        'password_use_offset': '7862400',
                    }
                }
            }
        }
        p_config.return_value = config
        self.assertEqual(len(self.cad.list_users()), 0)

        config['objects']['users']['access_key_active']['count'] = '5'
        p_config.return_value = config
        users = self.cad.list_users()
        self.assertEqual(len(users), 5)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_list_access_keys(self, p_config):
        config = {
            'objects': {
                'users': {
                    'access_key_active': {
                        'access_key_active': 'True',
                        'count': '2',
                        'creation_offset': '7862400',
                    }
                }
            }
        }
        p_config.return_value = config
        for user in self.cad.list_users():
            akeys = self.cad.list_access_keys(user['UserName'])
            self.assertEqual(len(akeys), 0)

        # config changes leads to hash -> user id change
        config['objects']['users']['access_key_active']['access_keys_count'] = '5'
        p_config.return_value = config
        for user in self.cad.list_users():
            akeys = self.cad.list_access_keys(user['UserName'])
            self.assertTrue(all(map(
                lambda x: x.get('Status', 'Inactive') == 'Active', akeys)))
            self.assertEqual(len(akeys), 5)

        config['objects']['users']['access_key_active']['access_key_active'] = 'False'
        p_config.return_value = config
        for user in self.cad.list_users():
            akeys = self.cad.list_access_keys(user['UserName'])
            self.assertTrue(all(map(
                lambda x: x.get('Status', 'Inactive') != 'Active', akeys)))

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_access_key_usage_info(self, p_config):
        now = datetime.now(tz=timezone.utc)
        p_config.return_value = {
            'objects': {
                'users': {
                    'access_key_active': {
                        'access_key_active': 'True',
                        'access_key_use_offset': '7862400',
                        'count': '2',
                        'creation_offset': '7862400',
                        'password_use_offset': '7862400',
                        'access_keys_count': '1'
                    }
                }
            }
        }
        for user in self.cad.list_users():
            akeys = self.cad.list_access_keys(user['UserName'])
            for akey in akeys:
                akey_info = self.cad.get_access_key_usage_info(
                    akey['AccessKeyId'])
                self.assertTrue(akey_info.get('LastUsedDate', now) < now)

    def test_similar_sku_prices(self):
        skus = self.cad.get_similar_sku_prices(str(uuid.uuid4()))
        self.assertTrue(len(skus) == 0)

        skus = self.cad.get_similar_sku_prices('KG2342MUYQD6T4BK')
        self.assertTrue(len(skus) > 0)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls(self, p_config):
        regions = {'1': 'eu-central-1'}
        self.process_discovery_calls(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_dependencies(self, p_config):
        regions = {'1': 'eu-central-1'}
        self.process_discovery_calls_dependencies(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_tags(self, p_config):
        regions = {'1': 'eu-central-1'}
        self.process_discovery_calls_tags(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_several_resource_groups(self, p_config):
        regions = {'1': 'eu-central-1'}
        self.process_discovery_calls_several_resource_groups(
            regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_regions(self, p_config):
        tests = [
            ({'1': 'eu-central-1', '2': 'us-east-12'}, 5),
            ({'1': 'eu-central-1', '2': 'us-east-1'}, 10)
        ]
        self.process_discovery_calls_regions(tests, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_rediscover(self, p_config):
        regions = {'1': 'eu-central-1'}
        self.process_discovery_calls_rediscover(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_renew(self, p_config):
        regions = {'1': 'eu-central-1'}
        self.process_discovery_calls_renew(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_inactive(self, p_config):
        regions = {'1': 'eu-central-1'}
        self.process_discovery_calls_inactive(regions, p_config)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_discovery_calls_inactive_dependencies(self, p_config):
        p_config.return_value = {
            'objects': {
                'snapshots': {
                    'common': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '10',
                        'first_seen_offset': '10',
                        'ttl': '5'
                    },
                    'uncommon': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '10',
                        'first_seen_offset': '10',
                        'ttl': '5'
                    }
                }
            },
            'regions': {'1': 'eu-central-1'}
        }
        res = []
        for call, params in self.cad.volume_discovery_calls():
            res.extend(call(*params))
            self.assertEqual(len(res), 2)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_images_discovery_active_sources(self, p_config):
        organization_id = str(uuid.uuid4())
        cloud_account_id = str(uuid.uuid4())
        now = int(datetime.utcnow().timestamp())

        for group, func in [
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
                            'is_image': 'True',
                            'from_image': 'True',
                            'count': '1'
                        }
                    }
                },
                'regions': {'1': 'eu-central-1'}
            }
            res = []
            for call, params in func():
                res.extend(call(*params))
            self.assertEqual(len(res), 1)
            self._create_mongo_resource(
                res[0], cloud_account_id, organization_id, now)

            res.clear()
            for call, params in func():
                res.extend(call(*params))
            self.assertEqual(len(res), 1)
        for func, params in self.cad.image_discovery_calls():
            self.assertTrue(len(func(*params)) == 1)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_get_report_files_nondiscoverable(self, p_config):
        config = {
            'objects': {
                'users': {
                     'access_key_active': {
                        'count': '0',
                        'creation_offset': '7862400',
                        'password_use_offset': '7862400',
                    }
                }
            },
            'regions': {'1': 'eu-central-1'}
        }
        p_config.return_value = config
        report_files = self.cad.get_report_files()
        self.assertEqual(len(report_files), 0)

    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_get_report_files(self, p_config):
        config = {
            'objects': {
                'buckets': {
                    'common': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '1'
                    }
                }
            },
            'regions': {'1': 'eu-central-1'}
        }
        now = datetime.utcnow()
        p_config.return_value = config
        report_files = self.cad.get_report_files()
        self.assertEqual(len(report_files), 1)
        for report_group in report_files.keys():
            date_start, date_end = self._dates_from_group(report_group)
            if date_start.month != 12:
                self.assertTrue(date_end.year == date_start.year and
                                date_end.month - date_start.month == 1)
                self.assertTrue(now.year == date_start.year and
                                now.month == date_start.month)
            else:
                self.assertTrue(date_end.year == date_start.year + 1 and
                                date_end.month == 1)
                self.assertTrue(now.year == date_start.year and
                                now.month == date_start.month)

        prev_month_end = (now.replace(day=1) - timedelta(days=1))
        month_ago = prev_month_end.replace(
            day=min(now.day, monthrange(prev_month_end.year, prev_month_end.month)[1]))

        fs_offset = now - month_ago

        config['objects']['buckets']['common']['first_seen_offset'] = str(
            int(fs_offset.total_seconds()))
        p_config.return_value = config
        report_files = self.cad.get_report_files()
        self.assertEqual(len(report_files), 2)
        first_seen_dates = [now, now - fs_offset]
        for report_group in report_files.keys():
            date_start, date_end = self._dates_from_group(report_group)
            if date_start.month != 12:
                self.assertTrue(date_end.year == date_start.year and
                                date_end.month - date_start.month == 1)
            else:
                self.assertTrue(date_end.year == date_start.year + 1 and
                                date_end.month == 1)
            self.assertTrue(any(filter(
                    lambda x: x.year == date_start.year and x.month == date_start.month,
                    first_seen_dates)))

    @patch('cloud_adapter.clouds.aws_fake.csv')
    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_download_report_file_nonexistent(self, p_config, p_csv):
        config = {
            'objects': {
                'buckets': {
                    'common': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '1'
                    }
                }
            },
            'regions': {'1': 'eu-central-1'}
        }

        p_config.return_value = config
        p_csv.DictWriter = Mock(writerows=Mock())
        with open(os.devnull, 'w') as f:
            self.cad.download_report_file('some_weird_report_file', f)
        self.assertEqual(p_csv.DictWriter.call_count, 0)


    @patch('cloud_adapter.clouds.aws_fake.csv')
    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_download_report_file_active(self, p_config, p_csv):
        config = {
            'objects': {
                'buckets': {
                    'common': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '1'
                    }
                }
            },
            'regions': {'1': 'eu-central-1'}
        }

        p_config.return_value = config
        p_csv.DictWriter = Mock(writerows=Mock())
        report_files_data = self.cad.get_report_files()
        for k, v in report_files_data.items():
            for rep in v:
                with open(os.devnull, 'w') as f:
                    self.cad.download_report_file(rep['Key'], f)
        self.assertEqual(p_csv.DictWriter.call_count, 0)

        discovered_resources = []
        organization_id = str(uuid.uuid4())
        cloud_account_id = str(uuid.uuid4())
        now = datetime(day=25, month=2, year=2021, hour=7)
        with freeze_time(now + timedelta(hours=1)):
            for func, params in self.cad.bucket_discovery_calls():
                discovered_resources.extend(func(*params))
            initials = []
            for resource in discovered_resources:
                initials.append(self._create_mongo_resource(
                    resource, cloud_account_id, organization_id, int(now.timestamp())))
            report_files_data = self.cad.get_report_files()
            for k, v in report_files_data.items():
                for rep in v:
                    with open(os.devnull, 'w') as f:
                        self.cad.download_report_file(rep['Key'], f)
            self.assertEqual(p_csv.DictWriter.call_count, 1)
            expense_call = {
                    'lineItem/LineItemType': 'Credit',
                    'lineItem/UsageStartDate': '2021-02-25T07:00:00Z',
                    'lineItem/UsageType': 'EUC1-DataTransfer-Out-Bytes',
                    'bill/BillingEntity': 'AWS',
                    'bill/BillingPeriodEndDate': '2021-03-01T00:00:00Z',
                    'bill/BillingPeriodStartDate': '2021-02-01T00:00:00Z',
                    'bill/PayerAccountId': None,
                    'lineItem/BlendedCost': '0.0000000117',
                    'lineItem/BlendedRate': '0.0000000117',
                    'lineItem/CurrencyCode': 'USD',
                    'lineItem/ProductCode': 'AWSDataTransfer',
                    'lineItem/UnblendedCost': '0.0000000117',
                    'lineItem/UnblendedRate': '0.0000000117',
                    'lineItem/UsageAccountId': None,
                    'lineItem/UsageEndDate': '2021-02-25T08:00:01Z',
                    'product/ProductName': 'AWS Data Transfer',
                    'product/productFamily': 'Data Transfer',
                    'product/region': 'eu-central-1',
                    'product/sku': 'F62Y6TKR8NC6Q2ZB',
                    'lineItem/ResourceId': '/%s' % discovered_resources[0].cloud_resource_id,
                    'resourceTags/user:group_config_hash': '9d6394bc912f90fcc0d43d912bbc322c'
            }
            for csv_call in p_csv.DictWriter.mock_calls:
                if not csv_call[0].endswith('writerows'):
                    continue
                for k, v in expense_call.items():
                    self.assertEqual(csv_call[1][0][0].get(k), v, '%s is not equal' % k)

    @patch('cloud_adapter.clouds.aws_fake.csv')
    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_download_report_file_active_offset(self, p_config, p_csv):
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
            'regions': {'1': 'eu-central-1'}
        }

        p_config.return_value = config
        p_csv.DictWriter = Mock(writerows=Mock())
        report_files_data = self.cad.get_report_files()

        discovered_resources = []
        organization_id = str(uuid.uuid4())
        cloud_account_id = str(uuid.uuid4())
        now = datetime(day=25, month=2, year=2021, hour=7)
        with freeze_time(now + timedelta(hours=1)):
            for func, params in self.cad.bucket_discovery_calls():
                discovered_resources.extend(func(*params))
            initials = []
            for resource in discovered_resources:
                initials.append(self._create_mongo_resource(
                    resource, cloud_account_id, organization_id, int(now.timestamp())))
            report_files_data = self.cad.get_report_files()
            for k, v in report_files_data.items():
                for rep in v:
                    with open(os.devnull, 'w') as f:
                        self.cad.download_report_file(rep['Key'], f)
            self.assertEqual(p_csv.DictWriter.call_count, 1)
            for csv_call in p_csv.DictWriter.mock_calls:
                if not csv_call[0].endswith('writerows'):
                    continue
                self.assertEqual(len(csv_call[1][0]), 2)

    @patch('cloud_adapter.clouds.aws_fake.csv')
    @patch('cloud_adapter.clouds.fake_base.FakeBase._config',
           new_callable=PropertyMock)
    def test_download_report_file_inactive(self, p_config, p_csv):
        config = {
            'objects': {
                'buckets': {
                    'common': {
                        'renew_percent': '0',
                        'tags': {},
                        'count': '1',
                        'first_seen_offset': str(int(
                            timedelta(days=2).total_seconds())),
                        'ttl': str(int(
                            timedelta(days=1).total_seconds()))
                    }
                }
            },
            'regions': {'1': 'eu-central-1'}
        }

        p_config.return_value = config
        p_csv.DictWriter = Mock(writerows=Mock())
        now = datetime(day=25, month=2, year=2021, hour=7)
        with freeze_time(now):
            report_files_data = self.cad.get_report_files()
            for k, v in report_files_data.items():
                for rep in v:
                    with open(os.devnull, 'w') as f:
                        self.cad.download_report_file(rep['Key'], f)
            self.assertEqual(p_csv.DictWriter.call_count, 1)

            resource = BucketResource(
                organization_id=str(uuid.uuid4()),
                cloud_account_id=str(uuid.uuid4())
            )
            for csv_call in p_csv.DictWriter.mock_calls:
                if not csv_call[0].endswith('writerows'):
                    continue
                self.assertEqual(len(csv_call[1][0]), 2)
                resource.cloud_resource_id = csv_call[1][0][0]['lineItem/ResourceId']
                resource.name = resource.cloud_resource_id
                resource.region = csv_call[1][0][0]['product/region']
                resource.tags = {
                    'group_config_hash': 'ae683d0a01d7986f50c88da9620c451e'
                }

            first_seen = int((now - timedelta(days=2)).timestamp())
            last_seen = first_seen + int(timedelta(days=1).total_seconds())
            self._create_mongo_resource(
                resource, str(uuid.uuid4()), str(uuid.uuid4()),
                int(now.timestamp()), first_seen, last_seen, False)
            for k, v in report_files_data.items():
                for rep in v:
                    with open(os.devnull, 'w') as f:
                        self.cad.download_report_file(rep['Key'], f)
            self.assertEqual(p_csv.DictWriter.call_count, 2)
