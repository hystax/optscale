import csv
import logging
import uuid

from calendar import monthrange
from datetime import datetime, timedelta, timezone

from cloud_adapter.clouds.aws import Aws
from cloud_adapter.clouds.fake_base import (
    FakeBase, ResourceKeys, encoded_tags, ResourceTypes, ETCD_FALSE)
from cloud_adapter.model import *


LOG = logging.getLogger(__name__)
REPORTS_GROUP_FORMAT = '%Y%m%d'
EXPENSE_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DEFAULT_FLAVOR = 't3.nano'
METER_MAP = {
    ResourceTypes.volume.value: {
        'ap-southeast-1': ('KVW47BDJMV6V4TYA', '0.1200000000'),
        'us-west-2': ('AUJG8J97AVK3PF8K', '0.1000000000'),
        'eu-west-2': ('58DS23R8RBGBGWEE', '0.1160000000'),
        'us-east-1': ('HY3BZPP2B6K8MSJF', '0.1000000000'),
        'eu-west-3': ('ESSUD2HPZGKYUGGX', '0.1160000000'),
        'me-south-1': ('X3MCMUQNTCHYP4KB', '0.1210000000'),
        'ap-northeast-2': ('HYU9KEWRBJTDDSCK', '0.1140000000'),
        'ap-southeast-2': ('5ES53GWNC5G54Q44', '0.1200000000'),
        'ap-northeast-1': ('2KRSTFABXH77P2FQ', '0.1200000000'),
        'eu-central-1': ('WHD78M63XVBREKT5', '0.1190000000'),
        'ca-central-1': ('SCGZGXF4WUZ74Q7A', '0.1100000000'),
        'us-east-2': ('SCM63QZA8NKUYACF', '0.1000000000'),
        'af-south-1': ('VUSQZR9XFXU85ZFS', '0.1309000000'),
        'us-west-1': ('UZ6TZ5NDAH7AGJPJ', '0.1200000000'),
        'eu-west-1': ('GDX844Q9TQAG2YZ2', '0.1100000000'),
        'ap-south-1': ('4MB6SVGV7JKWFBUJ', '0.1140000000'),
        'ap-northeast-3': ('6F534H7CJV6HN4S4', '0.1200000000'),
        'eu-south-1': ('TJAAZ93SWP3X4Y7Q', '0.1155000000'),
        'eu-north-1': ('7CTB69P5Y6AD2R84', '0.1045000000'),
        'sa-east-1': ('XEE5PD8PNDQJR7X3', '0.1900000000'),
        'ap-east-1': ('RBSZWUECC87G2DVW', '0.1320000000')
    },
    ResourceTypes.snapshot.value: {
        'us-east-2': ('EZ8T7N34G3H5Y4ER', '0.0500000000'),
        'eu-central-1': ('42HPMPRPNWRJYGZM', '0.0540000000'),
        'eu-west-2': ('KFGXHCVRRQ5UYRXJ', '0.0530000000'),
        'ap-northeast-1': ('4NHX4ZW7X52XZACJ', '0.0500000000'),
        'ap-northeast-3': ('J4276ZSNJVFGCXWW', '0.0500000000'),
        'us-west-2': ('CNYETXBBP73CTYPG', '0.0500000000'),
        'me-south-1': ('BP4GCXWXVXWFWFTU', '0.0550000000'),
        'ap-south-1': ('VDPTV7U529CYAXWY', '0.0500000000'),
        'ap-northeast-2': ('JC4HQPKR4ATMSY93', '0.0500000000'),
        'us-east-1': ('W339DBEHBVGTYPXR', '0.0500000000'),
        'af-south-1': ('P2C3ZE7ZCZXGMHVX', '0.0595000000'),
        'us-west-1': ('3F2BXQPS4TRZ6SR6', '0.0550000000'),
        'eu-west-3': ('DR59YGEVAG4VV4RA', '0.0530000000'),
        'eu-south-1': ('TRGEWAGEX8ETP2YW', '0.0525000000'),
        'ap-southeast-2': ('759N2ESGG4Z2C95V', '0.0550000000'),
        'eu-north-1': ('JAFNEA2DZUKPNWGT', '0.0475000000'),
        'sa-east-1': ('TCBN9ZYU44F47739', '0.0680000000'),
        'ap-east-1': ('8KEKS8ZT74G8BYQA', '0.0550000000'),
        'eu-west-1': ('UZ7N3QU3DRSU25FK', '0.0500000000'),
        'ap-southeast-1': ('5JKF9WXGUTYXYKXH', '0.0500000000'),
        'ca-central-1': ('5XUGBZ7CGY6QRFRD', '0.0550000000')
    },
    ResourceTypes.instance.value: {
        'ap-northeast-2': ('H7ZUWUQM6CR4EC83', '0.0065000000'),
        'eu-north-1': ('WGTNH42XRABN9CQH', '0.0054000000'),
        'eu-central-1': ('CVRPW534R69RUEMP', '0.0060000000'),
        'us-east-1': ('K7ERD2Q28HHU97DT', '0.0052000000'),
        'eu-west-1': ('KG2342MUYQD6T4BK', '0.0057000000'),
        'me-south-1': ('7WWTPXUP2GN7EANE', '0.0063000000'),
        'us-west-1': ('5EDHWY2G68899HDR', '0.0062000000'),
        'ap-northeast-3': ('GYSU5TZH84UBGJV4', '0.0068000000'),
        'ca-central-1': ('48PNHGCUGSKHKXWB', '0.0058000000'),
        'us-west-2': ('FFJFJF6E9ACSJXTV', '0.0052000000'),
        'ap-southeast-2': ('R38YK2SZTEYTTPWC', '0.0066000000'),
        'us-east-2': ('SEMV77DSB4WM675R', '0.0052000000'),
        'ap-northeast-1': ('TZG97WFA265PFBMW', '0.0068000000'),
        'eu-west-3': ('NUV5NNNMMYGGXPC2', '0.0059000000'),
        'ap-southeast-1': ('BJWSEGCHDKR6J3A8', '0.0066000000'),
        'eu-west-2': ('489GD5S7YM9EHXNV', '0.0059000000'),
        'af-south-1': ('456S8ADMKV2HEG86', '0.0068000000'),
        'ap-east-1': ('2Y2V5UBKTCGHE4AP', '0.0073000000'),
        'eu-south-1': ('T8KYYJPF95AD438P', '0.0060000000'),
        'ap-south-1': ('P6TB45QDGY6M3GGP', '0.0056000000'),
        'sa-east-1': ('ZP9UZFWN4HYJUA9P', '0.0084000000')
    },
    ResourceTypes.bucket.value: {
        'Global': ('F62Y6TKR8NC6Q2ZB', '0.0000000117')
    }
}
INSTANCE_REGION_LOCATION_MAP = {
    'ap-northeast-2': 'Asia Pacific (Seoul)',
    'eu-north-1': 'EU (Stockholm)',
    'eu-central-1': 'EU (Frankfurt)',
    'us-east-1': 'US East (N. Virginia)',
    'eu-west-1': 'EU (Ireland)',
    'me-south-1': 'Middle East (Bahrain)',
    'us-west-1': 'US West (N. California)',
    'ap-northeast-3': 'Asia Pacific (Osaka-Local)',
    'ca-central-1': 'Canada (Central)',
    'us-west-2': 'US West (Oregon)',
    'ap-southeast-2': 'Asia Pacific (Sydney)',
    'us-east-2': 'US East (Ohio)',
    'ap-northeast-1': 'Asia Pacific (Tokyo)',
    'eu-west-3': 'EU (Paris)',
    'ap-southeast-1': 'Asia Pacific (Singapore)',
    'eu-west-2': 'EU (London)',
    'af-south-1': 'Africa (Cape Town)',
    'ap-east-1': 'Asia Pacific (Hong Kong)',
    'eu-south-1': 'EU (Milan)',
    'ap-south-1': 'Asia Pacific (Mumbai)',
    'sa-east-1': 'South America (Sao Paulo)'
}


class AwsFake(FakeBase, Aws):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cloud_type = 'aws_cnr'

    def _gen_id(self, resource_key, region, base=None):
        new_id = '%s-%s-%s-%s' % (
            self._cloud_type.split('_')[0],
            region,
            resource_key.value[:3],
            base if base else uuid.uuid4().hex)
        # otherwise several accs rss will point to the same base
        # (instance -> image for example)
        if self.config.get('id'):
            new_id = '%s-%s' % (new_id, self.config['id'])
        return new_id

    def _get_existing_resources_query(self, resource_type, region,
                                      config_hash):
        query = {
            'active': True,
            'resource_type': resource_type,
            'region': region,
            **{'tags.%s' % k: v for k, v in encoded_tags(
                {'group_config_hash': config_hash}).items()}
        }
        if self.config.get('id'):
            query['cloud_account_id'] = self.config['id']
        LOG.debug(query)
        return query

    def _get_expense_resources_query(self, encoded_config_hash,
                                     resource_types, regions, active=True,
                                     now=0, first_seen=0):
        query = {
            'resource_type': {'$in': resource_types},
            'region': {'$in': regions},
            **{'tags.%s' % k: {'$in': v}
               for k, v in encoded_config_hash.items()}
        }
        if self.config.get('id'):
            query['cloud_account_id'] = self.config['id']
        if active:
            query['active'] = True
        elif first_seen > 0:
            query['last_seen'] = {'$gte': first_seen, '$lte': now}
        LOG.debug(query)
        return query

    def _create_volume(self, region, resource_config, config_hash,
                       volume_id=None, attached=False, **kwargs):
        snapshot_id = ''
        if self._check_bool_key(resource_config, 'from_snapshot'):
            snapshot_id = self._gen_id(
                ResourceKeys.snapshots, region, config_hash)

        tags = resource_config.get('tags', {}).copy()
        tags['group_config_hash'] = config_hash

        obj = VolumeResource(
            cloud_resource_id=volume_id if volume_id else self._gen_id(
                ResourceKeys.volumes, region),
            cloud_account_id=self.cloud_account_id,
            region=region,
            name=tags.get('Name'),
            size=10,
            volume_type='gp2',
            organization_id=self.organization_id,
            tags=tags,
            attached=attached,
            snapshot_id=snapshot_id
        )
        self._set_cloud_link(obj, region)
        return obj

    def discover_region_volumes(self, region):
        return self._discover_resources(ResourceKeys.volumes, region)

    def _create_snapshot(self, region, resource_config, config_hash,
                         snapshot_id=None, **kwargs):
        volume_id = 'vol-ffffffff'
        if self._check_bool_key(resource_config, 'from_volume'):
            volume_id = self._gen_id(
                ResourceKeys.volumes, region, config_hash)

        tags = resource_config.get('tags', {}).copy()
        tags['group_config_hash'] = config_hash

        obj = SnapshotResource(
            cloud_resource_id=snapshot_id if snapshot_id else self._gen_id(
                ResourceKeys.snapshots, region),
            cloud_account_id=self.cloud_account_id,
            region=region,
            name=tags.get('Name'),
            size=10,
            state='completed',
            organization_id=self.organization_id,
            tags=tags,
            volume_id=volume_id
        )
        self._set_cloud_link(obj, region)
        return obj

    def discover_region_snapshots(self, region):
        return self._discover_resources(ResourceKeys.snapshots, region)

    def _create_bucket(self, region, resource_config, config_hash,
                       bucket_id=None, **kwargs):
        bucket_id = bucket_id if bucket_id else self._gen_id(
            ResourceKeys.buckets, region)

        tags = resource_config.get('tags', {}).copy()
        tags['group_config_hash'] = config_hash

        obj = BucketResource(
            cloud_resource_id=bucket_id,
            cloud_account_id=self.cloud_account_id,
            region=region,
            organization_id=self.organization_id,
            name=bucket_id,
            tags=tags
        )
        self._set_cloud_link(obj, region)
        return obj

    def bucket_discovery_calls(self):
        # saves memory on many buckets
        def dummy_func(x):
            return [x]

        result = []
        # not like original func but anyway returns func and params
        for region in self.config_regions:
            buckets = self._discover_resources(ResourceKeys.buckets, region)
            for bucket in buckets:
                result.append((dummy_func, (bucket,)))
        return result

    def _create_instance(self, region, resource_config, config_hash,
                         instance_id=None, **kwargs):
        image_id = ''
        if self._check_bool_key(resource_config, 'from_image'):
            image_id = self._gen_id(
                ResourceKeys.images, region, config_hash)

        tags = resource_config.get('tags', {}).copy()
        tags['group_config_hash'] = config_hash

        obj = InstanceResource(
            cloud_resource_id=instance_id if instance_id else self._gen_id(
                ResourceKeys.instances, region),
            cloud_account_id=self.cloud_account_id,
            region=region,
            name=tags.get('Name'),
            flavor=DEFAULT_FLAVOR,
            security_groups=[],
            organization_id=self.organization_id,
            tags=tags,
            spotted=resource_config.get('spot', False),
            image_id=image_id
        )
        self._set_cloud_link(obj, region)
        return obj

    def discover_region_instances(self, region):
        return self._discover_resources(ResourceKeys.instances, region)

    @staticmethod
    def _month_start(dt):
        return dt.replace(day=1, hour=0, minute=0, second=0)

    @staticmethod
    def _month_end(dt):
        return dt.replace(day=monthrange(dt.year, dt.month)[1],
                          hour=23, minute=59, second=59, microsecond=0)

    def get_report_files(self):
        res = {}
        now = datetime.utcnow()
        first_expense_ts = int(now.timestamp())
        expenses_exist = False
        for resource_key, resource_configs in self.config_resources.items():
            try:
                resource_key = ResourceKeys(resource_key)
            except ValueError:
                LOG.warning('Unsupported resource key %s', resource_key)
                continue
            if resource_key not in ResourceKeys.discovery_keys():
                continue
            resource_type, _ = self.resource_key_type_map.get(
                resource_key, (None, None))
            if not resource_type:
                LOG.warning('Failed to find resource type for %s',
                            resource_key)
                continue
            for config_name, resource_config in resource_configs.items():
                expenses_exist = True
                first_seen_offset = int(resource_config.get(
                    'first_seen_offset', 0))
                config_first_seen = int(now.timestamp()) - first_seen_offset
                LOG.debug('Detected %s/%s first expense date %s',
                          resource_key, config_name, config_first_seen)
                if config_first_seen < first_expense_ts:
                    first_expense_ts = config_first_seen

        if expenses_exist:
            first_expense_dt = self._month_start(
                datetime.fromtimestamp(first_expense_ts))
            last_expense_dt = self._month_start(now)
            while True:
                if first_expense_dt > last_expense_dt:
                    break
                date_range = '%s-%s' % (
                    first_expense_dt.strftime(REPORTS_GROUP_FORMAT),
                    (self._month_end(first_expense_dt) + timedelta(
                        seconds=1)).strftime(REPORTS_GROUP_FORMAT)
                )
                LOG.info('Detected %s period', date_range)
                if (first_expense_dt.year == now.year and
                        first_expense_dt.month == now.month):
                    last_modified = now
                else:
                    last_modified = self._month_end(first_expense_dt)
                last_modified = last_modified.replace(tzinfo=timezone.utc)
                res[date_range] = [{
                    'Key': 'reports/%s/report-00001.csv.zip' % date_range,
                    'LastModified': last_modified
                }]
                first_expense_dt += timedelta(days=monthrange(
                    first_expense_dt.year, first_expense_dt.month)[1])
        return res

    @staticmethod
    def _usage_type_prefix(region):
        prefix = ''
        for val in region.split('-'):
            prefix += val if len(val) < 3 else val[:1]
        return prefix.upper()

    def _get_volume_expense_record(self, resource, sku, tags,
                                   usage_start, usage_end, cost, quantity):
        account_id = self.config.get('account_id')
        usage_type = '%s-EBS:VolumeUsage.gp2' % self._usage_type_prefix(
            resource['region'])
        return {
            'lineItem/LineItemType': 'Credit"',
            'lineItem/UsageStartDate': usage_start.strftime(
                EXPENSE_DATE_FORMAT),
            'lineItem/UsageType': usage_type,
            'bill/BillingEntity': 'AWS',
            'bill/BillingPeriodEndDate': (self._month_end(
                usage_end) + timedelta(seconds=1)).strftime(
                EXPENSE_DATE_FORMAT),
            'bill/BillingPeriodStartDate': self._month_start(
                usage_start).strftime(EXPENSE_DATE_FORMAT),
            'bill/PayerAccountId': account_id,
            'lineItem/BlendedCost': cost,
            'lineItem/BlendedRate': cost,
            'lineItem/CurrencyCode': 'USD',
            'lineItem/ProductCode': 'AmazonEC2',
            'lineItem/UnblendedCost': cost,
            'lineItem/UnblendedRate': cost,
            'lineItem/UsageAccountId': account_id,
            'lineItem/UsageEndDate': (usage_end + timedelta(
                seconds=1)).strftime(EXPENSE_DATE_FORMAT),
            'product/ProductName': 'Amazon Elastic Compute Cloud',
            'product/productFamily': 'Storage',
            'product/region': resource['region'],
            'product/sku': sku,
            'lineItem/ResourceId': '/%s' % resource['cloud_resource_id'],
            **{'resourceTags/user:%s' % k: v for k, v in tags.items()},
            'snapshot_id': resource.get('snapshot_id')
        }

    def _get_snapshot_expense_record(self, resource, sku, tags,
                                     usage_start, usage_end, cost, quantity):
        account_id = self.config.get('account_id')
        usage_type = '%s-EBS:SnapshotUsage' % self._usage_type_prefix(
            resource['region'])
        return {
            'lineItem/LineItemType': 'Credit',
            'lineItem/UsageStartDate': usage_start.strftime(
                EXPENSE_DATE_FORMAT),
            'lineItem/UsageType': usage_type,
            'bill/BillingEntity': 'AWS',
            'bill/BillingPeriodEndDate': (self._month_end(
                usage_end) + timedelta(seconds=1)).strftime(
                EXPENSE_DATE_FORMAT),
            'bill/BillingPeriodStartDate': self._month_start(
                usage_start).strftime(EXPENSE_DATE_FORMAT),
            'bill/PayerAccountId': account_id,
            'lineItem/BlendedCost': cost,
            'lineItem/BlendedRate': cost,
            'lineItem/CurrencyCode': 'USD',
            'lineItem/ProductCode': 'AmazonEC2',
            'lineItem/UnblendedCost': cost,
            'lineItem/UnblendedRate': cost,
            'lineItem/UsageAccountId': account_id,
            'lineItem/UsageEndDate': (usage_end + timedelta(
                seconds=1)).strftime(EXPENSE_DATE_FORMAT),
            'product/ProductName': 'Amazon Elastic Compute Cloud',
            'product/productFamily': 'Storage Snapshot',
            'product/region': resource['region'],
            'product/sku': sku,
            'lineItem/ResourceId': '/%s' % resource['cloud_resource_id'],
            **{'resourceTags/user:%s' % k: v for k, v in tags.items()},
            'volume_id': resource.get('volume_id')
        }

    def _get_instance_expense_record(self, resource, sku, tags,
                                     usage_start, usage_end, cost, quantity):
        account_id = self.config.get('account_id')
        usage_type = '%s-BoxUsage:%s' % (self._usage_type_prefix(
            resource['region']),
                                         DEFAULT_FLAVOR)
        cost = str(float(cost) * quantity)

        return {
            'lineItem/LineItemType': 'SavingsPlanNegation',
            'lineItem/Operation': 'RunInstances',
            'lineItem/UsageStartDate': usage_start.strftime(
                EXPENSE_DATE_FORMAT),
            'lineItem/UsageType': usage_type,
            'bill/BillingEntity': 'AWS',
            'bill/BillingPeriodEndDate': (usage_end + timedelta(
                seconds=1)).strftime(EXPENSE_DATE_FORMAT),
            'bill/BillingPeriodStartDate': self._month_start(
                usage_start).strftime(
                EXPENSE_DATE_FORMAT),
            'bill/PayerAccountId': account_id,
            'lineItem/BlendedCost': cost,
            'lineItem/BlendedRate': cost,
            'lineItem/CurrencyCode': 'USD',
            'lineItem/ProductCode': 'AmazonEC2',
            'lineItem/UnblendedCost': cost,
            'lineItem/UnblendedRate': cost,
            'lineItem/UsageAccountId': account_id,
            'lineItem/UsageAmount': "24.0000000000",
            'lineItem/UsageEndDate': (usage_end + timedelta(
                seconds=1)).strftime(EXPENSE_DATE_FORMAT),
            'product/ProductName': 'Amazon Elastic Compute Cloud',
            'product/productFamily': 'Compute Instance',
            'product/region': resource['region'],
            'product/instanceType': DEFAULT_FLAVOR,
            'product/sku': sku,
            'product/servicecode': 'AmazonEC2',
            'product/tenancy': 'Shared',
            'product/operatingSystem': 'Linux',
            'product/preInstalledSw': 'NA',
            'lineItem/ResourceId': '/%s' % resource['cloud_resource_id'],
            **{'resourceTags/user:%s' % k: v for k, v in tags.items()},
            'image_id': resource.get('image_id')
        }

    def _get_bucket_expense_record(self, resource, sku, tags,
                                   usage_start, usage_end, cost, quantity):
        account_id = self.config.get('account_id')
        usage_type = '%s-DataTransfer-Out-Bytes' % self._usage_type_prefix(
            resource['region'])
        return {
            'lineItem/LineItemType': 'Credit',
            'lineItem/UsageStartDate': usage_start.strftime(
                EXPENSE_DATE_FORMAT),
            'lineItem/UsageType': usage_type,
            'bill/BillingEntity': 'AWS',
            'bill/BillingPeriodEndDate': (self._month_end(
                usage_end) + timedelta(seconds=1)).strftime(
                EXPENSE_DATE_FORMAT),
            'bill/BillingPeriodStartDate': self._month_start(
                usage_start).strftime(EXPENSE_DATE_FORMAT),
            'bill/PayerAccountId': account_id,
            'lineItem/BlendedCost': cost,
            'lineItem/BlendedRate': cost,
            'lineItem/CurrencyCode': 'USD',
            'lineItem/ProductCode': 'AWSDataTransfer',
            'lineItem/UnblendedCost': cost,
            'lineItem/UnblendedRate': cost,
            'lineItem/UsageAccountId': account_id,
            'lineItem/UsageEndDate': (usage_end + timedelta(
                seconds=1)).strftime(EXPENSE_DATE_FORMAT),
            'product/ProductName': 'AWS Data Transfer',
            'product/productFamily': 'Data Transfer',
            'product/region': resource['region'],
            'product/sku': sku,
            'lineItem/ResourceId': '/%s' % resource['cloud_resource_id'],
            **{'resourceTags/user:%s' % k: v for k, v in tags.items()}
        }

    def _get_expense_record(self, resource, usage_start, usage_end):
        resource_func_map = {
            ResourceTypes.volume.value: self._get_volume_expense_record,
            ResourceTypes.snapshot.value: self._get_snapshot_expense_record,
            ResourceTypes.instance.value: self._get_instance_expense_record,
            ResourceTypes.bucket.value: self._get_bucket_expense_record
        }

        resource_type = resource['resource_type']
        resource_meter_map = METER_MAP.get(resource_type, {})
        sku, cost = resource_meter_map.get(
            resource['region'], resource_meter_map.get('Global'))
        quantity = (usage_end - usage_start).total_seconds() / 3600

        func = resource_func_map.get(resource_type)
        if not func or not sku:
            return {}
        return func(resource, sku,
                    encoded_tags(resource['tags'], decode=True),
                    usage_start, usage_end, cost, quantity)

    def download_report_file(self, report_name, file_obj):
        dates_group = report_name.split('/')
        if len(dates_group) != 3:
            LOG.warning('Incorrect report path %s', report_name)
            return
        dates_group = dates_group[1].split('-')
        if len(dates_group) != 2:
            LOG.warning('Incorrect report name %s', report_name)
            return
        now = datetime.utcnow()
        date_start = datetime.strptime(dates_group[0], REPORTS_GROUP_FORMAT)
        if date_start > now:
            date_start = now
        date_end = datetime.strptime(
            dates_group[1], REPORTS_GROUP_FORMAT) - timedelta(seconds=1)
        if date_end > now or date_end < date_start:
            date_end = now

        res = []
        csv_keys = set()
        LOG.info('Collecting expenses for %s-%s', date_start, date_end)
        for expense in self._get_expenses(date_start, date_end):
            res.append(expense)
            csv_keys.update(expense.keys())
        if res:
            LOG.info('Dumping to file')
            w = csv.DictWriter(file_obj, csv_keys)
            w.writeheader()
            w.writerows(res)

    def list_users(self):
        res = []
        now = datetime.utcnow()
        for config_name, user_config in self.config_resources.get(
                ResourceKeys.users.value, {}).items():
            LOG.info('Discovering %s users', config_name)
            creation_offset = int(user_config.get('creation_offset', 0))
            password_use_offset = int(user_config.get('password_use_offset', 0))
            user_hash = self._get_config_hash(user_config)
            for num in range(int(user_config.get('count', 0))):
                user_id = '%s_%s' % (user_hash, num)
                res.append(
                    {
                        'UserName': user_id,
                        'UserId': user_id,
                        'CreateDate': (now - timedelta(
                            seconds=creation_offset)).replace(
                            tzinfo=timezone.utc),
                        'PasswordLastUsed': (now - timedelta(
                            seconds=password_use_offset)).replace(
                            tzinfo=timezone.utc),
                        'Tags': [
                            {
                                'Key': k, 'Value': v
                            } for k, v in user_config.get('tags', {})
                        ],

                    }
                )
        return res

    def list_access_keys(self, username):
        name_base = username.split('_')
        # hash and num
        if len(name_base) != 2:
            LOG.warning('Incorrect username %s', username)
            return []
        source_hash = name_base[0]
        res = []
        for config_name, user_config in self.config_resources.get(
                ResourceKeys.users.value, {}).items():
            if source_hash != self._get_config_hash(user_config):
                continue
            LOG.info('Found base config, discovering %s access keys', config_name)
            access_key_hash = self._get_config_hash(user_config)
            for num in range(int(user_config.get('access_keys_count', 0))):
                key_id = '%s_%s' % (access_key_hash, num)
                res.append({
                    'UserName': username,
                    'AccessKeyId': key_id,
                    'Status': 'Active' if self._check_bool_key(
                        user_config, 'access_key_active') else 'Inactive',
                })
            if res:
                break
        return res

    def get_access_key_usage_info(self, access_key_id):
        access_key_base = access_key_id.split('_')
        # hash and num
        if len(access_key_base) != 2:
            LOG.warning('Incorrect access key id %s', access_key_id)
            return
        source_hash = access_key_base[0]
        now = datetime.utcnow()
        for config_name, user_config in self.config_resources.get(
                ResourceKeys.users.value, {}).items():
            if source_hash != self._get_config_hash(user_config):
                continue
            LOG.info('Found base config, generating %s usage info', config_name)
            use_offset = int(user_config.get('access_key_use_offset', 0))
            return {
                'LastUsedDate': (now - timedelta(seconds=use_offset)).replace(
                    tzinfo=timezone.utc),
                'ServiceName': 'Fake AWS',
            }
        return {}

    def list_regions(self):
        return list(self.config_regions)

    def discover_region_images(self, region, by_owner=True, filter_by=None):
        def create_image(config_hash, resource_config, snapshots):
            resource_id = self._gen_id(
                ResourceKeys.images, region, config_hash)
            tags = resource_config.get('tags', {}).copy()
            tags['group_config_hash'] = config_hash

            created_at_ts = snapshots[0].get('created_at') - int(
                resource_config.get('image_last_seen_offset', 0))

            return {
                'ImageId': resource_id,
                'Name': tags.get('Name'),
                'CreationDate': datetime.fromtimestamp(
                    created_at_ts).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'BlockDeviceMappings': [
                    {
                        'Ebs': {
                            'SnapshotId': s.get('cloud_resource_id')
                        }
                    } for s in snapshots
                ],
                'Tags': [
                    {
                        'Key': k, 'Value': v
                    } for k, v in tags.items()]
            }

        res = []
        config_resources = self.config_resources
        for resource_key in [ResourceKeys.instances,
                             ResourceKeys.snapshots]:
            for config_name, resource_config in config_resources.get(
                    resource_key.value, {}).items():
                if resource_key == ResourceKeys.instances:
                    if not self._check_bool_key(resource_config, 'from_image'):
                        continue
                if resource_key == ResourceKeys.snapshots:
                    if not self._check_bool_key(
                            resource_config, 'is_image', ETCD_FALSE):
                        continue
                LOG.info('Discovering %s/%s images', resource_key, config_name)
                config_hash = self._get_config_hash(resource_config)
                resource_type, _ = self.resource_key_type_map.get(
                    resource_key)
                if not config_hash or not resource_type:
                    LOG.warning('Failed to find resource type for %s',
                                resource_key)
                    continue
                encoded_config_hash = encoded_tags(
                    {'group_config_hash': [config_hash]})
                query = self._get_expense_resources_query(
                    encoded_config_hash, [ResourceTypes.snapshot.value],
                    [region], True)
                resources = list(self.resources_collection.find(query))
                if not resources:
                    LOG.debug('Failed to find %s/%s resources',
                              resource_key, config_name)
                    continue
                res.append(create_image(config_hash, resource_config,
                                        resources))
        return res

    def get_similar_sku_prices(self, sku):
        res = []
        sku_found = False
        for region, price_details in METER_MAP.get(
                ResourceTypes.instance.value, {}).items():
            region_sku, region_cost = price_details
            if sku == region_sku:
                sku_found = True
            res.append({
                'location': INSTANCE_REGION_LOCATION_MAP.get(region),
                'price_unit': 'Hrs',
                'sku': region_sku,
                'price': {'USD': region_cost},
                'instanceType': DEFAULT_FLAVOR,
            })
        if not sku_found:
            LOG.warning('Failed to find sku %s details', sku)
        return res if sku_found else []

    def get_reserved_instances_offerings(self, *args, **kwargs):
        return {'ReservedInstancesOfferings': [
            {'Duration': 31536000, 'FixedPrice': 31.0, 'InstanceType': 't3.nano',
             'ProductDescription': 'Linux/UNIX',
             'ReservedInstancesOfferingId': 'd7fb576b-ab5a-497e-992d-85f8ade19ab1',
             'UsagePrice': 0.0, 'CurrencyCode': 'USD',
             'InstanceTenancy': 'default', 'Marketplace': False,
             'OfferingClass': 'standard', 'OfferingType': 'All Upfront',
             'PricingDetails': [], 'RecurringCharges': [
                {'Amount': 0.0, 'Frequency': 'Hourly'}], 'Scope': 'Region'},
            {'Duration': 31536000, 'FixedPrice': 0.0, 'InstanceType': 't3.nano',
             'ProductDescription': 'Linux/UNIX',
             'ReservedInstancesOfferingId': '3b0935b3-0961-4ef4-9314-ba1050dbd2a4',
             'UsagePrice': 0.0, 'CurrencyCode': 'USD',
             'InstanceTenancy': 'default', 'Marketplace': False,
             'OfferingClass': 'convertible', 'OfferingType': 'No Upfront',
             'PricingDetails': [], 'RecurringCharges': [
                {'Amount': 0.005, 'Frequency': 'Hourly'}], 'Scope': 'Region'}]}

    def validate_credentials(self, org_id=None):
        return {'account_id': self._get_config_hash(self.config),
                'warnings': []}

    def configure_report(self):
        pass

    def configure_last_import_modified_at(self):
        offsets = []
        for resource_key, resource_configs in self.config_resources.items():
            for _, resource_config in resource_configs.items():
                if resource_config.get('first_seen_offset'):
                        offsets.append(resource_config['first_seen_offset'])
        return int(datetime.utcnow().timestamp() - max(
                [int(x) for x in offsets], default=0))

    def set_currency(self, currency):
        pass
