import datetime
import enum
from concurrent.futures.thread import ThreadPoolExecutor
from functools import wraps
import json
import logging
import os
import random
import re

import boto3
from botocore.config import Config as CoreConfig
from botocore.exceptions import (ClientError,
                                 WaiterError,
                                 EndpointConnectionError,
                                 ParamValidationError,
                                 ConnectTimeoutError,
                                 ReadTimeoutError,
                                 SSLError)
from botocore.parsers import ResponseParserError
from retrying import retry

from tools.cloud_adapter.exceptions import *
from tools.cloud_adapter.clouds.base import S3CloudMixin
from tools.cloud_adapter.model import *
from tools.cloud_adapter.utils import CloudParameter, gbs_to_bytes

LOG = logging.getLogger(__name__)
DEFAULT_REPORT_NAME = 'optscale-report'
DEFAULT_BUCKET_PREFIX = 'reports'
DEFAULT_CLIENT_CONFIG = CoreConfig(
    connect_timeout=20, retries={'max_attempts': 3}
)
IAM_CLIENT_CONFIG = CoreConfig(
    connect_timeout=60, read_timeout=60, retries={'max_attempts': 3},
)
SECONDS_IN_DAY = 60 * 60 * 24
CLOUD_LINK_PATTERN = '%s/%s/v2/home?region=%s#%s=%s'
BUCKET_CLOUD_LINK_PATTERN = '%s/%s/buckets/%s?region=%s&tab=objects'
DEFAULT_BASE_URL = 'https://console.aws.amazon.com'
BUCKET_ACCEPTED_PERMISSIONS = ['FULL_CONTROL', 'READ', 'WRITE', 'READ_ACP',
                               'WRITE_ACP']
BUCKET_ACCEPTED_URIS = [
    'http://acs.amazonaws.com/groups/global/AllUsers',
    'http://acs.amazonaws.com/groups/global/AuthenticatedUsers'
]
# maximum value for MaxResults (AWS limitation)
MAX_RESULTS = 1000

REGEX_AWS_REPORT_FORMAT = 'data/BILLING_PERIOD=[0-9]{{4}}-[0-9]{{2}}'
REGEX_AWS_REPORT_GROUP = 'BILLING_PERIOD=[0-9]{4}-[0-9]{2}'
REGEX_AWS_REPORT_FORMAT_CSV_LEGACY = '[0-9]{{8}}-[0-9]{{8}}(/[0-9]{{8}}T[0-9]{{6}}Z)?'
REGEX_AWS_REPORT_GROUP_CSV_LEGACY = '[0-9]{8}-[0-9]{8}'
REGEX_AWS_REPORT_FORMAT_PARQUET_LEGACY = '{1}/year=[0-9]{{4}}/month=([1-9]|1[0-2])'
REGEX_AWS_REPORT_GROUP_PARQUET_LEGACY = 'year=[0-9]{4}/month=([1-9]|1[0-2])/'


def _retry_on_error(exc):
    if isinstance(exc, ResponseParserError):
        return True
    if isinstance(exc, EndpointConnectionError):
        return True
    if isinstance(exc, ClientError):
        err_code = exc.response['Error'].get('Code')
        if err_code and err_code == 'RequestLimitExceeded':
            return True
    if isinstance(exc, WaiterError):
        err_reason = exc.kwargs.get('reason')
        if err_reason and 'Request limit exceeded' in err_reason:
            return True
    if isinstance(exc, SSLError):
        return True
    return False


def _wrap_timeout_exception():
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ReadTimeoutError, ConnectTimeoutError) as ex:
                raise ConnectionTimeout('Connection timed out')
        return func_wrapper
    return decorator


class ConfigScheme(enum.Enum):
    find_report = 'find_report'
    create_report = 'create_report'
    bucket_only = 'bucket_only'


class Aws(S3CloudMixin):
    BILLING_CREDS = [
        CloudParameter(name='access_key_id', type=str, required=True),
        CloudParameter(name='secret_access_key', type=str, required=True,
                       protected=True),
        CloudParameter(name='config_scheme', type=str, required=False),
        CloudParameter(name='bucket_name', type=str, required=False),
        CloudParameter(name='bucket_prefix', type=str, required=False),
        CloudParameter(name='report_name', type=str, required=False),
        CloudParameter(name='linked', type=bool, required=False),
    ]
    DEFAULT_S3_REGION_NAME = 'eu-central-1'
    SUPPORTS_REPORT_UPLOAD = True

    def discovery_calls_map(self):
        return {
            VolumeResource: self.volume_discovery_calls,
            InstanceResource: self.instance_discovery_calls,
            SnapshotResource: self.snapshot_discovery_calls,
            IpAddressResource: self.ip_address_discovery_calls,
            BucketResource: self.bucket_discovery_calls
        }

    @property
    def sts(self):
        return self.session.client('sts')

    @property
    def ec2(self):
        return self.session.client('ec2')

    @property
    def ec2_resource(self):
        return self.session.resource('ec2')

    @property
    def s3_resource(self):
        return self.session.resource('s3')

    @property
    def cf(self):
        return self.session.client("cloudformation")

    @property
    def cur(self):
        # hardcoded, because service is only available in us-east-1
        return self.session.client('cur', 'us-east-1')

    @property
    def iam(self):
        return self.session.client('iam', config=IAM_CLIENT_CONFIG)

    @property
    def pricing(self):
        return self.session.client('pricing', 'us-east-1')

    @property
    def cloud_account_id(self):
        return self.config.get('cloud_account_id')

    @property
    def organization_id(self):
        return self.config.get('organization_id')

    @property
    def cloud_account_name(self):
        return self.config.get('cloud_account_name')

    @property
    def cloudwatch(self):
        return self.session.client('cloudwatch')

    @retry(retry_on_exception=_retry_on_error, wait_fixed=2000,
           stop_max_attempt_number=10)
    def _retry(self, method, *args, **kwargs):
        return method(*args, **kwargs)

    def describe_security_groups(self, region, group_ids=None):
        session = self.get_session()
        ec2 = session.client('ec2', region)
        all_groups = {sec_group['GroupId']: sec_group
                      for sec_group in self._retry(ec2.describe_security_groups)['SecurityGroups']}
        if group_ids:
            # if one group_id was passed then convert it to list
            if isinstance(group_ids, str):
                group_ids = [group_ids]
            groups_by_id = [all_groups[group_id] for group_id in group_ids if all_groups.get(group_id)]
        else:
            groups_by_id = list(all_groups.values())
        return groups_by_id

    def validate_credentials(self, org_id=None):
        try:
            result = self._retry(self.sts.get_caller_identity)
        except ClientError as ex:
            raise InvalidParameterException(str(ex))
        except (ReadTimeoutError, ConnectTimeoutError) as ex:
            raise CloudConnectionError(str(ex))
        return {'account_id': result['Account'],
                'warnings': []}

    @_wrap_timeout_exception()
    def list_regions(self):
        """
        Lists regions
        :return: list(string)
        """
        return [region['RegionName'] for region in
                self.ec2.describe_regions()['Regions']]

    @staticmethod
    def _extract_tag(obj_, tag_name, dict_name='Tags'):
        return next((map(lambda x: x['Value'], filter(
            lambda y: y['Key'] == tag_name, obj_.get(
                dict_name, [])))), None)

    @staticmethod
    def _extract_tags(obj, dict_name='Tags'):
        tags = {}
        for tag in obj.get(dict_name, []):
            if tag['Key'] == 'Name':
                continue
            tags[tag['Key']] = tag['Value']
        return tags

    @staticmethod
    def _generate_cloud_link(resource_type, region, resource_value):
        cloud_link_map = {
            InstanceResource: CLOUD_LINK_PATTERN % (
                DEFAULT_BASE_URL, 'ec2', region,
                'InstanceDetails:instanceId', resource_value),
            VolumeResource: CLOUD_LINK_PATTERN % (
                DEFAULT_BASE_URL, 'ec2', region,
                'Volumes:volumeId', resource_value),
            SnapshotResource: CLOUD_LINK_PATTERN % (
                DEFAULT_BASE_URL, 'ec2', region,
                'Snapshots:snapshotId', resource_value),
            BucketResource: BUCKET_CLOUD_LINK_PATTERN % (
                DEFAULT_BASE_URL, 's3', resource_value, region),
            IpAddressResource: CLOUD_LINK_PATTERN % (
                DEFAULT_BASE_URL, 'ec2', region,
                'ElasticIpDetails:AllocationId', resource_value),
        }
        return cloud_link_map.get(resource_type)

    def _set_cloud_link(self, resource_obj, region):
        resource_type = type(resource_obj)
        resource_obj.cloud_console_link = self._generate_cloud_link(
            resource_type, region, resource_obj.cloud_resource_id)

    def _discover_region_vpcs(self, region):
        ec2 = self.session.client('ec2', region)
        vpcs = ec2.describe_vpcs().get('Vpcs', [])
        # if there is no VpcId in vpc then it means that something is wrong
        # with that vpc so we can ignore it
        return {
            vpc['VpcId']: self._extract_tag(vpc, 'Name')
            for vpc in vpcs if vpc.get('VpcId')
        }

    def discover_region_instances(self, region):
        """
        Discovers instance cloud resources
        :return: list(model.InstanceResource)
        """
        vpc_id_to_name = self._discover_region_vpcs(region)
        ec2 = self.session.client('ec2', region)
        next_token = None
        first_iteration = True
        while next_token or first_iteration:
            params = {'MaxResults': MAX_RESULTS}
            if next_token:
                params['NextToken'] = next_token
            first_iteration = False
            described = ec2.describe_instances(**params)
            next_token = described.get('NextToken')
            for reservation in described['Reservations']:
                for instance in reservation['Instances']:
                    dates = [x['Ebs']['AttachTime'] for x in instance[
                        'BlockDeviceMappings'] if 'Ebs' in x]
                    dates.extend(list(map(
                        lambda x: x['Attachment']['AttachTime'],
                        instance.get('NetworkInterfaces', []))))
                    cloud_created = min(
                        dates, default=None) or instance['LaunchTime']
                    spotted = instance.get('InstanceLifecycle') == 'spot'
                    vpc_id = instance.get('VpcId')
                    instance_resource = InstanceResource(
                        cloud_resource_id=instance['InstanceId'],
                        cloud_account_id=self.cloud_account_id,
                        region=region,
                        name=self._extract_tag(instance, 'Name'),
                        flavor=instance['InstanceType'],
                        security_groups=instance.get('SecurityGroups', []),
                        organization_id=self.organization_id,
                        tags=self._extract_tags(instance),
                        spotted=spotted,
                        image_id=instance.get('ImageId'),
                        cloud_created_at=int(cloud_created.timestamp()),
                        vpc_id=vpc_id,
                        vpc_name=vpc_id_to_name.get(vpc_id)
                    )
                    self._set_cloud_link(instance_resource, region)
                    yield instance_resource

    def instance_discovery_calls(self):
        """
        Returns list of discovery calls to discover instances presented
        as tuples (adapter_method, arguments_tuple)
        """
        return [(self.discover_region_instances, (r,))
                for r in self.list_regions()]

    def discover_region_volumes(self, region):
        ec2 = self.session.client('ec2', region)
        next_token = None
        first_iteration = True
        while next_token or first_iteration:
            params = {'MaxResults': MAX_RESULTS}
            if next_token:
                params['NextToken'] = next_token
            first_iteration = False
            described = ec2.describe_volumes(**params)
            next_token = described.get('NextToken')
            for volume in described['Volumes']:
                volume_resource = VolumeResource(
                    cloud_resource_id=volume['VolumeId'],
                    cloud_account_id=self.cloud_account_id,
                    region=region,
                    name=self._extract_tag(volume, 'Name'),
                    size=gbs_to_bytes(volume['Size']),
                    volume_type=volume['VolumeType'],
                    organization_id=self.organization_id,
                    tags=self._extract_tags(volume),
                    attached=(volume['State'] == 'in-use'),
                    snapshot_id=volume['SnapshotId']
                )
                self._set_cloud_link(volume_resource, region)
                yield volume_resource

    def volume_discovery_calls(self):
        """
        Returns list of discovery calls to discover volumes presented
        as tuples (adapter_method, arguments_tuple)
        """
        return [(self.discover_region_volumes, (r,))
                for r in self.list_regions()]

    def discover_region_snapshots(self, region):
        account_id = self.validate_credentials()['account_id']
        ec2 = self.session.client('ec2', region)
        next_token = None
        first_iteration = True
        while next_token or first_iteration:
            params = {'Filters': [{'Name': 'owner-id', 'Values': [account_id]}],
                      'MaxResults': MAX_RESULTS}
            if next_token:
                params['NextToken'] = next_token
            first_iteration = False
            described = ec2.describe_snapshots(**params)
            next_token = described.get('NextToken')
            for snap in described['Snapshots']:
                snapshot_resource = SnapshotResource(
                    cloud_resource_id=snap['SnapshotId'],
                    cloud_account_id=self.cloud_account_id,
                    region=region,
                    organization_id=self.organization_id,
                    name=self._extract_tag(snap, 'Name'),
                    size=gbs_to_bytes(snap['VolumeSize']),
                    description=snap['Description'],
                    state=snap['State'],
                    tags=self._extract_tags(snap),
                    volume_id=snap['VolumeId']
                )
                self._set_cloud_link(snapshot_resource, region)
                yield snapshot_resource

    def snapshot_discovery_calls(self):
        """
        Returns list of discovery calls to discover snapshots presented
        as tuples (adapter_method, arguments_tuple)
        """
        return [(self.discover_region_snapshots, (r,))
                for r in self.list_regions()]

    def _handle_specific_error(self, exc, error_code):
        exc_error_code = exc.response['Error'].get('Code')
        if exc_error_code == error_code:
            return
        else:
            raise exc

    def _get_bucket_public_settings(self, bucket_s3, bucket_name):
        is_public_policy, is_public_acls = (False, False)
        public_access_block = {}
        try:
            public_access_block = bucket_s3.get_public_access_block(
                Bucket=bucket_name)
        except ClientError as exc:
            # We get this type of exception if we don't change any public
            # access settings. So it's normal situation if config is
            # not found
            self._handle_specific_error(
                exc, 'NoSuchPublicAccessBlockConfiguration')
        access_block_config = public_access_block.get(
            'PublicAccessBlockConfiguration', {})
        block_public_policy = access_block_config.get(
            'BlockPublicPolicy', False)
        block_public_acls = access_block_config.get('BlockPublicAcls', False)
        if block_public_policy and block_public_acls:
            return is_public_policy, is_public_acls
        if block_public_policy is False:
            try:
                is_public_blocked_map = bucket_s3.get_bucket_policy_status(
                    Bucket=bucket_name)
                is_public_policy = is_public_blocked_map.get(
                    'PolicyStatus', {}).get('IsPublic')
            except ClientError as exc:
                # Bucket could be created without any bucket policy
                self._handle_specific_error(exc, 'NoSuchBucketPolicy')

        if block_public_acls is False:
            try:
                alc_map = bucket_s3.get_bucket_acl(Bucket=bucket_name)
            except ClientError as exc:
                LOG.error(str(exc))
                raise
            grants = alc_map.get('Grants', [])
            for grant in grants:
                grantee = grant.get('Grantee', {})
                permission = grant.get('Permission')
                has_permission = (permission and
                                  permission in BUCKET_ACCEPTED_PERMISSIONS)
                uri = grantee.get('URI')
                has_accepted_uris = bool(uri and uri in BUCKET_ACCEPTED_URIS)
                is_public_acls = has_permission and has_accepted_uris
                if is_public_acls:
                    break
        return is_public_policy, is_public_acls

    def discover_bucket_info(self, bucket_name):
        region_info = self.s3.get_bucket_location(Bucket=bucket_name)
        # LocationConstraint will be None if bucket is located in us-east-1
        region = region_info['LocationConstraint'] or 'us-east-1'

        # get_bucket_tagging fails for eu-south-1 if region is not set
        # explicitly, so we find region first and initialize client for
        # specific region
        s3 = self.session.client('s3', region_name=region)
        is_public_policy, is_public_acls = self._get_bucket_public_settings(
            s3, bucket_name)

        try:
            tags = s3.get_bucket_tagging(Bucket=bucket_name)
        except ClientError as exc:
            err_code = exc.response['Error'].get('Code')
            if err_code and err_code == 'NoSuchTagSet':
                tags = {}
            else:
                raise
        bucket_resource = BucketResource(
            cloud_resource_id=bucket_name,
            cloud_account_id=self.cloud_account_id,
            region=region,
            organization_id=self.organization_id,
            name=bucket_name,
            tags=self._extract_tags(tags, dict_name='TagSet'),
            is_public_policy=is_public_policy,
            is_public_acls=is_public_acls
        )
        self._set_cloud_link(bucket_resource, region)
        yield bucket_resource

    def bucket_discovery_calls(self):
        """
        Returns list of discovery calls to discover buckets presented
        as tuples (adapter_method, arguments_tuple)
        """
        result = list()
        bucket_list = self.s3.list_buckets()
        for bucket in bucket_list['Buckets']:
            result.append((self.discover_bucket_info, (bucket['Name'],)))
        return result

    def pod_discovery_calls(self):
        return []

    def snapshot_chain_discovery_calls(self):
        return []

    def rds_instance_discovery_calls(self):
        return []

    def discover_region_ip_addresses(self, region):
        instance_map = {}
        ec2 = self.session.client('ec2', region)
        described_ip_addresses = ec2.describe_addresses()
        instance_ids = []
        for address in described_ip_addresses['Addresses']:
            instance_id = address.get('InstanceId')
            if instance_id:
                instance_ids.append(instance_id)
        if instance_ids:
            described_instances = ec2.describe_instances(InstanceIds=instance_ids)
            for reservation in described_instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_map.update({instance['InstanceId']: instance.get('State', {}).get('Name')})
        for address in described_ip_addresses['Addresses']:
            available = True
            instance_id = address.get('InstanceId')
            if instance_id:
                available = instance_map.get(instance_id) in ['stopped', 'terminated']
            ip_resource = IpAddressResource(
                cloud_account_id=self.cloud_account_id,
                organization_id=self.organization_id,
                cloud_resource_id=address['AllocationId'],
                region=region,
                instance_id=instance_id,
                available=available
            )
            self._set_cloud_link(ip_resource, region)
            yield ip_resource

    def ip_address_discovery_calls(self):
        return [(self.discover_region_ip_addresses, (r,))
                for r in self.list_regions()]

    def check_prefix_report_name(self, prefix, report_name):
        if prefix and not self.is_valid_s3_object_key(prefix):
            raise BucketPrefixValidationError(
                'Bucket prefix "{}" has incorrect format'.format(prefix))
        if not self.is_valid_s3_object_key(report_name):
            raise ReportNameValidationError(
                'Report name "{}" has incorrect format'.format(report_name))

    def _collect_s3_objects(self, bucket_name, prefix, report_name):
        resp = self.s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix='{0}/{1}/'.format(prefix, report_name),
            Delimiter='/'
        )
        result = {'Contents': []}
        for common_prefix in resp.get('CommonPrefixes', []):
            common_prefix = common_prefix['Prefix']
            last_objects_map = {}
            resp = self.s3.list_objects_v2(
                Bucket=bucket_name,
                Prefix=common_prefix,
            )
            for r in resp.get('Contents', []):
                path = r['Key']
                day = path.split(common_prefix)[1].split(report_name)[0]
                key = common_prefix + path.split(
                    common_prefix + day)[1] if day else path
                last_obj = last_objects_map.get(key)
                if not last_obj or last_obj['LastModified'] < r['LastModified']:
                    last_objects_map[key] = r
            result['Contents'].extend(last_objects_map.values())
        return result

    def get_report_files(self):
        bucket_name = self.config['bucket_name']
        prefix = self.config.get('bucket_prefix', DEFAULT_BUCKET_PREFIX)
        if prefix.endswith('/'):
            prefix = prefix[:-1]
        report_name = self.config.get('report_name', DEFAULT_REPORT_NAME)
        region = self.get_bucket_region(bucket_name)
        self.config['region_name'] = region
        resp = self._collect_s3_objects(bucket_name, prefix, report_name)

        reports = self.find_csv_reports(resp, prefix, report_name)
        if not reports:
            reports = self.find_parquet_reports(resp, prefix, report_name)

        if not reports:
            raise ReportFilesNotFoundException(
                'Report files for report {} not found in bucket {}'.format(
                    report_name, bucket_name))
        return reports

    def find_parquet_reports(self, s3_objects, prefix, report_name):
        reports = {}
        parquet_regex_parts = [
            (REGEX_AWS_REPORT_FORMAT,
             REGEX_AWS_REPORT_GROUP),  # parquet reports
            (REGEX_AWS_REPORT_FORMAT_PARQUET_LEGACY,
             REGEX_AWS_REPORT_GROUP_PARQUET_LEGACY)  # legacy parquet reports
        ]
        try:
            for format_part, group_part in parquet_regex_parts:
                report_regex_fmt = r'^{0}/{1}/%s/{1}-[0-9]{{5}}.snappy.parquet$' \
                                   % format_part
                report_regex = re.compile(
                    report_regex_fmt.format(re.escape(prefix),
                                            re.escape(report_name)))
                for report in [f for f in s3_objects['Contents']
                               if re.match(report_regex, f['Key'])]:
                    group = re.search(group_part, report['Key']).group(0)
                    common_group = self._group_to_daterange(group)
                    if common_group not in reports:
                        reports[common_group] = []
                    reports[common_group].append(report)
        except KeyError:
            reports = {}
        return reports

    @staticmethod
    def _group_to_daterange(group):
        if 'BILLING_PERIOD' in group:
            year = int(group[-7:-3])
            month = int(group[-2:])
        else:
            year = int(group[5:].split('/')[0])
            month = int(group.split('month=')[1].split('/')[0])
        if month == 12:
            next_year = year + 1
            next_month = 1
        else:
            next_year = year
            next_month = month + 1
        return '{0}{1}01-{2}{3}01'.format(year, f'{month:02d}',
                                          next_year, f'{next_month:02d}')

    def find_csv_reports(self, s3_objects, prefix, report_name):
        reports = {}
        try:
            csv_regex_parts = [
                (REGEX_AWS_REPORT_FORMAT,
                 REGEX_AWS_REPORT_GROUP),  # csv reports
                (REGEX_AWS_REPORT_FORMAT_CSV_LEGACY,
                 REGEX_AWS_REPORT_GROUP_CSV_LEGACY)  # legacy csv reports
            ]
            for format_part, group_part in csv_regex_parts:
                report_regex_fmt = '^{0}/{1}/%s/{1}-[0-9]{{5}}.csv.(gz|zip)$' \
                                   % format_part
                report_regex = re.compile(
                    report_regex_fmt.format(re.escape(prefix),
                                            re.escape(report_name)))
                for report in [f for f in s3_objects['Contents']
                               if re.match(report_regex, f['Key'])]:
                    group = re.search(group_part, report['Key']).group(0)
                    if group not in reports:
                        reports[group] = []
                    reports[group].append(report)
        except KeyError:
            reports = {}
        return reports

    def download_report_file(self, report_name, file_obj):
        self.s3.download_fileobj(
            self.config['bucket_name'], report_name, file_obj)

    def configure_bucket_policy(self, bucket_name):
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "billingreports.amazonaws.com"
                    },
                    "Action": [
                        "s3:GetBucketAcl",
                        "s3:GetBucketPolicy"
                    ],
                    "Resource": "arn:aws:s3:::{}".format(bucket_name)
                },
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "billingreports.amazonaws.com"
                    },
                    "Action": "s3:PutObject",
                    "Resource": "arn:aws:s3:::{}/*".format(bucket_name)
                }
            ]
        }
        return self.s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy),
        )

    def get_bucket_region(self, bucket_name):
        try:
            bucket_location = self.s3.get_bucket_location(Bucket=bucket_name)
            location_constraint = bucket_location.get('LocationConstraint')
            return 'us-east-1' if location_constraint is None else location_constraint
        except self.s3.exceptions.NoSuchBucket:
            raise BucketNotFoundException(
                'Bucket {} not found'.format(bucket_name))
        except ParamValidationError:
            raise BucketNameValidationError('Bucket name "{}" has incorrect format'.format(bucket_name))

    @staticmethod
    def get_report_definition(report_name, bucket_name, prefix,
                              region):
        return {
            'ReportName': report_name,
            'TimeUnit': 'DAILY',
            'Format': 'textORcsv',
            'Compression': 'ZIP',
            'AdditionalSchemaElements': ['RESOURCES'],
            'S3Bucket': bucket_name,
            'S3Prefix': prefix,
            'S3Region': region,
            'RefreshClosedReports': True,
            'ReportVersioning': 'OVERWRITE_REPORT'
        }

    def check_report_definition(self, report, exclude_s3_settings=False,
                                exclude_name=False):
        if not report or not isinstance(report, dict):
            return

        exclude_keys = ['TimeUnit', 'Format', 'Compression']
        if exclude_name:
            exclude_keys.append('ReportName')
        if exclude_s3_settings:
            exclude_keys.extend(['S3Bucket', 'S3Prefix', 'S3Region'])

        report_definition = self.get_report_definition(
            report_name=self.config.get('report_name', DEFAULT_REPORT_NAME),
            bucket_name=self.config.get('bucket_name'),
            prefix=self.config.get('bucket_prefix', DEFAULT_BUCKET_PREFIX),
            region=self.config.get('region_name', self.DEFAULT_S3_REGION_NAME)
        )

        incorrect_params = []
        for k, v in report_definition.items():
            if k in exclude_keys:
                continue
            report_val = report.get(k)
            if report_val != v:
                incorrect_params.append('%s must be %s' % (k, v))
        supported_compression = ['ZIP', 'GZIP', 'Parquet']
        if report.get('Compression') not in supported_compression:
            incorrect_params.append(
                'Compression must be in %s' % supported_compression)
        supported_time_units = ['DAILY', 'HOURLY']
        if report.get('TimeUnit') not in supported_time_units:
            incorrect_params.append(
                'TimeUnit must be in %s' % supported_compression)
        supported_formats = ['textORcsv', 'Parquet']
        if report.get('Format') not in supported_formats:
            incorrect_params.append(
                'Format must be in %s' % supported_compression)

        if incorrect_params:
            raise ReportConfigurationException(
                'Invalid report configuration: {}'.format(
                    ', '.join(incorrect_params)))

    def _wrap(self, action, method, *args, **kwargs):
        try:
            return self._retry(method, *args, **kwargs)
        except ClientError as exc:
            err_code = exc.response['Error'].get('Code')
            if err_code and err_code in ['AccessDenied',
                                         'AccessDeniedException',
                                         '403', 'Forbidden']:
                raise ReportConfigurationException(
                    'Not enough permissions to {}: {}'.format(
                        action, str(exc)))
            else:
                raise ReportConfigurationException(
                    'Unable to {}: {}'.format(action, str(exc)))

    def create_bucket_for_report(self, bucket_name):
        def create_bucket_for_report_inner(func):
            try:
                func(bucket_name)
            except (self.s3.exceptions.BucketAlreadyExists,
                    self.s3.exceptions.BucketAlreadyOwnedByYou):
                raise ReportConfigurationException(
                    'Bucket {} already exists'.format(bucket_name))

        def create_bucket(bucket_name):
            return self.s3.create_bucket(
                Bucket=bucket_name,
                ACL='private',
                CreateBucketConfiguration={
                    'LocationConstraint': self.config.get('region_name',
                                                          self.DEFAULT_S3_REGION_NAME)
                })

        actions = [
            ('create bucket {}'.format(bucket_name),
             create_bucket),
            ('configure bucket {} policy'.format(bucket_name),
             self.configure_bucket_policy)
        ]
        for step, func in actions:
            self._wrap(step, create_bucket_for_report_inner, func)

    def find_reports(self, name=None, raise_on_bad_config=False,
                     search_criteria=None, **kwargs):
        res = []
        for r in self.cur.describe_report_definitions()['ReportDefinitions']:
            if name is None or (name and r['ReportName'] == name):
                if search_criteria:
                    try:
                        search_criteria(r, **kwargs)
                    except ReportConfigurationException:
                        if raise_on_bad_config:
                            raise
                        else:
                            continue
                res.append(r)
        return res

    def _configure_create_report(self):
        bucket_name = self.config.get('bucket_name')
        if bucket_name is None:
            raise ReportConfigurationException(
                'bucket_name is required')

        is_bucket_missing = False
        try:
            region = self._wrap(
                'check bucket {} existence'.format(bucket_name),
                self.get_bucket_region,
                bucket_name)
            self.config['region_name'] = region
        except BucketNotFoundException:
            is_bucket_missing = True

        if is_bucket_missing:
            self.create_bucket_for_report(bucket_name)

        prefix = self.config.get('bucket_prefix', DEFAULT_BUCKET_PREFIX)
        report_name = self.config.get('report_name', DEFAULT_REPORT_NAME)
        self.check_prefix_report_name(prefix, report_name)
        reports = self._wrap(
            'find report {}'.format(report_name),
            self.find_reports,
            report_name, search_criteria=self.check_report_definition,
            raise_on_bad_config=True,
        )
        if not reports:
            def create_report(definition):
                try:
                    self.cur.put_report_definition(
                        ReportDefinition=definition)
                except self.cur.exceptions.ReportLimitReachedException:
                    raise ReportConfigurationException(
                        'Unable to create report: report limit reached')
                except self.cur.exceptions.DuplicateReportNameException:
                    raise ReportConfigurationException(
                        'Unable to create report: {} already exists'.format(
                            report_name))
                except ParamValidationError:
                    raise ReportConfigurationException(
                        'Unable to create report: invalid parameters')

            report_definition = self.get_report_definition(
                report_name=report_name, bucket_name=bucket_name,
                prefix=prefix,
                region=self.config.get('region_name', self.DEFAULT_S3_REGION_NAME))
            self._wrap(
                'create report {}'.format(report_name),
                create_report, report_definition)
        resp = self._wrap(
            'check access to {}/{}'.format(bucket_name, prefix),
            self.s3.list_objects_v2,
            Bucket=bucket_name, Prefix=prefix, MaxKeys=15)
        objs = sorted(resp.get('Contents', []),
                      key=lambda x: x.get('Size', 0))
        if objs:
            with open(os.devnull, 'wb') as f:
                self._wrap('perform test {} download'.format(objs[0]['Key']),
                           self.download_report_file,
                           objs[0]['Key'], f)

    def _configure_find_report(self):
        reports = self._wrap(
            'list reports', self.find_reports,
            search_criteria=self.check_report_definition,
            exclude_s3_settings=True, exclude_name=True
        )
        if not reports:
            raise ReportConfigurationException(
                'Unable to find report with required configuration')
        reports = {r['ReportName']: r for r in reports}
        for name, report in reports.items():
            bucket_name = report['S3Bucket']
            prefix = report['S3Prefix']
            try:
                resp = self._retry(self.s3.list_objects_v2,
                                   Bucket=bucket_name, Prefix=prefix,
                                   MaxKeys=15)
                objs = sorted(resp.get('Contents', []),
                              key=lambda x: x.get('Size', 0))
                if objs:
                    self.config['bucket_name'] = bucket_name
                    with open(os.devnull, 'wb') as f:
                        self._retry(self.download_report_file,
                                    objs[0]['Key'], f)
                return {
                    'bucket_name': bucket_name,
                    'report_name': name,
                    'bucket_prefix': prefix
                }
            except ClientError as exc:
                LOG.warning(str(exc))
        raise ReportConfigurationException(
            'Unable to read report data. Checked reports: {}'.format(
                ', '.join(reports.keys())))

    def _check_report_download(self, bucket_name, prefix):
        reports = self._wrap(
            'check {}/{} access'.format(bucket_name, prefix),
            self.get_report_files)
        if reports:
            report = reports.popitem()[1][0]
            with open(os.devnull, 'wb') as f:
                self._wrap('perform test {} download'.format(report),
                           self.download_report_file, report['Key'], f)

    def _configure_bucket_only(self):
        for param in ['bucket_name', 'report_name', 'bucket_prefix']:
            if self.config.get(param) is None:
                raise ReportConfigurationException(
                    '{} is required'.format(param))
        bucket_name = self.config.get('bucket_name')
        report_name = self.config.get('report_name')
        prefix = self.config.get('bucket_prefix')
        try:
            region = self._wrap(
                'check bucket {} existence'.format(bucket_name),
                self.get_bucket_region,
                bucket_name)
            self.config['region_name'] = region
        except BucketNotFoundException:
            raise ReportConfigurationException(
                'Bucket {} not found'.format(bucket_name))

        self.check_prefix_report_name(prefix, report_name)
        try:
            self._check_report_download(bucket_name, prefix)
        except ReportFilesNotFoundException:
            try:
                # AWS shows prefix in console as '<prefix>/<report_name>', let's
                # try to connect cloud removing report_name from prefix
                pattern = '^(.*)(\\/.*)$'
                match = re.match(pattern, prefix)
                if match:
                    prefix = match.group(1)
                    LOG.warning('Changing bucket prefix from {0} to {1}'.format(
                        self.config['bucket_prefix'], prefix))
                    self.config['bucket_prefix'] = prefix
                    self._check_report_download(bucket_name, prefix)
            except ReportFilesNotFoundException:
                raise ReportConfigurationException(
                    'Unable to find report {} files'.format(report_name))

    def configure_report(self):
        if self.config.get('linked'):
            return
        scheme = self.config.get(
            'config_scheme', ConfigScheme.find_report.value)
        try:
            ConfigScheme(scheme)
        except ValueError:
            raise ReportConfigurationException(
                'Incorrect config_scheme')

        configurations = {
            ConfigScheme.find_report.value: self._configure_find_report,
            ConfigScheme.create_report.value: self._configure_create_report,
            ConfigScheme.bucket_only.value: self._configure_bucket_only
        }
        configure_func = configurations.get(scheme)
        return {
            'config_updates': configure_func() or {},
            'warnings': []
        }

    def configure_last_import_modified_at(self):
        pass

    def try_to_find_existing_reports(self):
        try:
            LOG.info('Trying to find existing report files')
            reports = self.get_report_files()
        except Exception as ex:
            LOG.info('Unable to find existing report files. Err: %s' % str(ex))
            reports = []
        LOG.info('Found reports: %s' % reports)
        return reports

    def _get_coordinates_map(self):
        return {
            'eu-central-1': {'longitude': 8.65399, 'latitude': 50.12581},
            'eu-west-1': {'longitude': -6.266155, 'latitude': 53.350140},
            'eu-west-2': {'longitude': -0.11362, 'latitude': 51.51768},
            'eu-west-3': {'longitude': 2.34293, 'latitude': 48.85717},
            'eu-south-1': {'latitude': 45.4668, 'longitude': 9.1905},
            'eu-north-1': {'longitude': 18.04856, 'latitude': 59.33097},
            'us-east-1': {'longitude': -78.45, 'latitude': 38.13},
            'us-east-2': {'longitude': -83, 'latitude': 39.96},
            'us-west-1': {'longitude': -121.96, 'latitude': 37.35},
            'us-west-2': {'longitude': -123.88, 'latitude': 46.15},
            'af-south-1': {'latitude': -33.928992, 'longitude': 18.417396},
            'ap-east-1': {'longitude': 114.13624, 'latitude': 22.25424},
            'ap-south-1': {'longitude': 72.86730, 'latitude': 19.07257},
            'ap-northeast-1': {'longitude': 139.42, 'latitude': 35.41},
            'ap-northeast-2': {'longitude': 126.99272, 'latitude': 37.57444},
            'ap-northeast-3': {'longitude': 135.50674, 'latitude': 34.69857},
            'ap-southeast-1': {'longitude': 103.851959, 'latitude': 1.290270},
            'ap-southeast-2': {'longitude': 151.2, 'latitude': -33.8},
            'ap-southeast-3': {'longitude': 106.8455, 'latitude': -6.2087},
            'ca-central-1': {'longitude': -73.6, 'latitude': 45.5},
            'me-south-1': {'longitude': 50.6377716, 'latitude': 25.9304142},
            'sa-east-1': {'longitude': -46.8754, 'latitude': -23.6815},
            'cn-north-1': {'longitude': 116.38570, 'latitude': 39.90388},
            'cn-northwest-1': {'longitude': 103.7300, 'latitude': 37.2931},
            'us-gov-east-1': {'longitude': -83.0235, 'latitude': 39.9653},
            'us-gov-west-1': {'longitude': -97.09434, 'latitude': 31.78395},
            'global': {'longitude': -98.48424, 'latitude': 39.01190}
        }

    def get_regions_coordinates(self):
        zero_coordinates = {
            'longitude': None,
            'latitude': None
        }
        coordinates_map = self._get_coordinates_map()
        try:
            for available_region in self.list_regions():
                if not coordinates_map.get(available_region):
                    coordinates_map[available_region] = zero_coordinates
        except Exception:
            LOG.info('Cannot retrieve the list of regions for %s cloud account'
                     % self.cloud_account_id)
            pass
        return coordinates_map

    def list_users(self):
        response = self._retry(self.iam.list_users)
        return response.get('Users', [])

    def get_login_profile(self, user_name):
        try:
            response = self._retry(self.iam.get_login_profile,
                                   UserName=user_name)
            return response.get('LoginProfile', None)
        except self.iam.exceptions.NoSuchEntityException:
            return None
        except ClientError as exc:
            # previous error NoSuchEntityException is expected from cloud if
            # the user does not have console access but rarely we get
            # unexpected cloud error with NoSuchEntity text which is not
            # caught by the error, will use this way and log such error
            if 'NoSuchEntity' in str(exc):
                LOG.info('Unexpected NoSuchEntity %s error from cloud while '
                         'get_login_profile for user %s', str(exc), user_name)
                return None
            raise

    def list_access_keys(self, username):
        response = self._retry(self.iam.list_access_keys, UserName=username)
        return response.get('AccessKeyMetadata', [])

    def get_access_key_usage_info(self, access_key_id):
        response = self._retry(self.iam.get_access_key_last_used,
                               AccessKeyId=access_key_id)
        return response['AccessKeyLastUsed']

    def get_pricing(self, filters):
        session = self.get_session()
        pricing = session.client('pricing', 'us-east-1')
        api_filters = []
        for field, value in filters.items():
            api_filters.append({
                'Type': 'TERM_MATCH',
                'Field': field,
                'Value': value,
            })
        body = {'ServiceCode': 'AmazonEC2', 'Filters': api_filters}
        result = []
        resp = pricing.get_products(**body)
        result.extend([json.loads(r) for r in resp['PriceList']])
        while resp.get('NextToken'):
            resp = pricing.get_products(**body, NextToken=resp['NextToken'])
            result.extend([json.loads(r) for r in resp['PriceList']])
        return result

    @staticmethod
    def _format_prices(prices):
        result = []
        for sku_info in prices:
            sku = sku_info['product']['attributes']
            price_info = list(list(
                sku_info['terms']['OnDemand'].values()
            )[0]['priceDimensions'].values())[0]
            sku['price_unit'] = price_info['unit']
            sku['price'] = price_info['pricePerUnit']
            sku['sku'] = sku_info['product']['sku']
            result.append(sku)
        return result

    def get_similar_sku_prices(self, sku):
        location_related_fields = [
            'location',
            'locationType',
            'usagetype',
            'regionCode'
        ]
        sku_resp = self.get_pricing({'sku': sku})
        sku_attrs = sku_resp[0]['product']['attributes']
        similar_infos = self.get_pricing({k: v for k, v in sku_attrs.items()
                                         if k not in location_related_fields})
        return self._format_prices(similar_infos)

    def get_prices(self, filters):
        if not filters:
            return []
        prices_infos = self.get_pricing(filters)
        return self._format_prices(prices_infos)

    @property
    def ssm(self):
        return self.session.client('ssm', 'us-east-1')

    def get_region_name_code_map(self):
        url_tmp = '/aws/service/global-infrastructure/regions/%s/longName'
        code_name_map = {}
        for region in self.list_regions():
            ssm_response = self.ssm.get_parameter(Name=url_tmp % region)
            region_name = ssm_response['Parameter']['Value'].replace(
                'Europe', 'EU')
            code_name_map[region_name] = region
        return code_name_map

    @_wrap_timeout_exception()
    def get_spot_history(self, region, flavors):
        return self.session.client('ec2', region).describe_spot_price_history(
            InstanceTypes=flavors, StartTime=datetime.datetime.utcnow(),
        )

    @staticmethod
    def _build_filter(filter_by):
        filters = []
        if isinstance(filter_by, dict):
            for k, v in filter_by.items():
                values = []
                if isinstance(v, list):
                    values.extend(v)
                else:
                    values.append(v)
                filters.append({'Name': k, 'Values': values})
        return filters

    def image_discovery_calls(self):
        """
        Returns list of discovery calls to discover regions presented
        as tuples (adapter_method, arguments_tuple)
        """
        return [(self.discover_region_images, (r,))
                for r in self.list_regions()]

    def discover_region_images(self, region, by_owner=True, filter_by=None):
        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        owners = []
        if by_owner:
            owners.append(self.validate_credentials()['account_id'])
        ec2 = self.session.client('ec2', region)
        all_images = ec2.describe_images(Owners=owners).get('Images', [])
        if filter_by and isinstance(filter_by, dict):
            all_images = self._filter_response(all_images, filter_by)
        for image in all_images:
            image_resource = ImageResource(
                cloud_resource_id=image['ImageId'],
                cloud_account_id=self.cloud_account_id,
                region=region,
                name=image.get('Name'),
                block_device_mappings=[
                    {
                        'device_name': bdm.get('DeviceName'),
                        'snapshot_id': bdm.get('Ebs', {}).get('SnapshotId'),
                        'volume_size': bdm.get('Ebs', {}).get('VolumeSize'),
                    }
                    for bdm in image.get('BlockDeviceMappings', [])
                ],
                cloud_created_at=int(datetime.datetime.strptime(
                    image['CreationDate'], date_format).timestamp()),
                tags=self._extract_tags(image),
            )
            yield image_resource

    @staticmethod
    def _filter_response(all_elements, filter_by):
        def is_param_in_filter(param, filter_key, filter_value):
            if isinstance(filter_value, list):
                is_matched = param.get(filter_key) in filter_value
            else:
                is_matched = param.get(filter_key) == filter_value
            return is_matched

        for filter_key, filter_value in filter_by.items():
            all_elements = list(
                filter(
                    lambda param: is_param_in_filter(
                        param, filter_key, filter_value
                    ), all_elements)
            )
        return all_elements

    @_wrap_timeout_exception()
    def get_region_availability_zones(self, region):
        resp = self.session.client(
            'ec2', region_name=region).describe_availability_zones(
            Filters=[{
                'Name': 'opt-in-status',
                'Values': ['opt-in-not-required']
            }])
        return [az['ZoneName'] for az in resp['AvailabilityZones']]

    @_wrap_timeout_exception()
    def get_all_instance_types(self, region):
        # this method will run in threads and new session is necessary to avoid
        # issues caused by creation of client in threads
        session = self.get_session()

        instance_types = []
        region_ec2 = session.client('ec2', region_name=region)
        resp = region_ec2.describe_instance_types()
        instance_types.extend(resp['InstanceTypes'])
        while resp.get('NextToken'):
            resp = region_ec2.describe_instance_types(
                NextToken=resp['NextToken'])
            instance_types.extend(resp['InstanceTypes'])
        return instance_types

    @_wrap_timeout_exception()
    def get_pricing_score_base(self, regions, skus):
        region_name_code_map = self.get_region_name_code_map()
        region_scores = {r: 0 for r in regions}
        for sku in skus:
            similar_skus = self.get_similar_sku_prices(sku)
            region_sku_price = {}
            for similar in similar_skus:
                region = region_name_code_map.get(similar['location'])
                if region not in regions:
                    continue
                region_sku_price[region] = float(similar['price']['USD'])
            sku_not_preset_regions = set(regions) - set(region_sku_price.keys())
            if sku_not_preset_regions:
                raise Exception('sku {} not present in regions {}'.format(
                    sku, sku_not_preset_regions))
            for region, price in region_sku_price.items():
                region_scores[region] += price
        return region_scores

    def get_instance_types_present_in_all_regions(self, regions):
        type_regions_map = {}
        for region in regions:
            types_in_region = self.session.client(
                'ec2', region_name=region).describe_instance_types()
            for i_type in types_in_region['InstanceTypes']:
                type_name = i_type['InstanceType']
                if type_name not in type_regions_map:
                    type_regions_map[type_name] = []
                type_regions_map[type_name].append(region)
        result = []
        for type_name, type_regions in type_regions_map.items():
            regions_diff = set(regions) - set(type_regions)
            if not regions_diff:
                result.append(type_name)
        return result

    @_wrap_timeout_exception()
    def get_oregon_sku_for_types(self, instance_types):
        result = []
        for instance_type in instance_types:
            skus = self.get_pricing({
                'instanceType': instance_type,
                'preInstalledSw': 'NA',
                'operatingSystem': 'Linux',
                'tenancy': 'Shared',
                'locationType': 'AWS Region',
                'capacitystatus': 'Used',
            })
            for sku_info in skus:
                if sku_info['product']['attributes']['location'] == 'US West (Oregon)':
                    result.append(sku_info['product']['sku'])
                    break
            else:
                raise Exception('instance type {} not present in oregon'.format(
                    instance_type))
        return result

    def get_price_checking_skus(self):
        skus = self.get_oregon_sku_for_types(
            self.get_instance_types_present_in_all_regions(self.list_regions())
        )
        return random.sample(skus, 10)

    def get_metric(self, namespace, metric_name, instance_ids, region,
                   interval, start_date, end_date):
        """
        Get metric for instances
        :param metric_name: metric name
        :param instance_ids: instance ids
        :param region: instance's region name
        :param interval: time interval in seconds
        :param start_date: metric start datetime date
        :param end_date: metric end datetime date
        :return: dict
        """
        result = {}
        # TODO: replace parallel calls with proper bulks
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures_map = {}
            for instance_id in instance_ids:
                session = self.get_session()
                cloudwatch = session.client('cloudwatch', region_name=region)
                params = {
                    'Dimensions': [{
                        'Name': 'InstanceId',
                        'Value': instance_id
                    }],
                    'MetricName': metric_name,
                    'Namespace': namespace,
                    'StartTime': start_date,
                    'EndTime': end_date,
                    'Period': interval,
                    'Statistics': ['Average'],
                }
                futures_map[instance_id] = executor.submit(
                    self._retry, cloudwatch.get_metric_statistics, **params)
            for instance_id, f in futures_map.items():
                stats = f.result()['Datapoints']
                result[instance_id] = stats
        return result

    def get_reserved_instances_offerings(self, pd, tenancy, flavor,
                                         min_duration, max_duration,
                                         include_marketplace):
        try:
            return self.ec2.describe_reserved_instances_offerings(
                ProductDescription=pd, InstanceTenancy=tenancy,
                InstanceType=flavor, MinDuration=min_duration,
                MaxDuration=max_duration,
                IncludeMarketplace=include_marketplace)
        except ClientError as ex:
            error_message = str(ex)
            if 'InvalidParameter' in error_message:
                raise InvalidParameterException(error_message)
            raise

    def set_currency(self, currency):
        pass

    def start_instance(self, instance_ids: list, region):
        ec2 = self.session.client('ec2', region)
        try:
            return ec2.start_instances(InstanceIds=instance_ids)
        except ClientError as exc:
            if 'InvalidInstanceID' in exc.response['Error']['Code']:
                raise ResourceNotFound(str(exc))
            elif 'IncorrectInstanceState' in str(exc):
                raise InvalidResourceStateException(str(exc))
            else:
                raise

    def stop_instance(self, instance_ids: list, region):
        ec2 = self.session.client('ec2', region)
        try:
            return ec2.stop_instances(InstanceIds=instance_ids)
        except ClientError as exc:
            if 'InvalidInstanceID' in str(exc):
                raise ResourceNotFound(str(exc))
            elif 'IncorrectInstanceState' in str(exc):
                raise InvalidResourceStateException(str(exc))
            else:
                raise
