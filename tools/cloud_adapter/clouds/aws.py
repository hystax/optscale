from datetime import datetime, timezone
from datetime import timedelta
import time
from concurrent.futures import as_completed
from datetime import timedelta
import enum
import urllib.parse
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor
from functools import wraps
from importlib import metadata
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
                                 InvalidRegionError,
                                 ParamValidationError,
                                 ConnectTimeoutError,
                                 ReadTimeoutError,
                                 SSLError)
from botocore.session import Session as CoreSession
from botocore.parsers import ResponseParserError
from retrying import retry

from tools.cloud_adapter.exceptions import *
from tools.cloud_adapter.clouds.base import S3CloudMixin
from tools.cloud_adapter.model import *
from tools.cloud_adapter.utils import CloudParameter, gbs_to_bytes
from tools.cloud_adapter.templates import AwsTemplates

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
LB_CLOUD_LINK_PATTERN = '%s/ec2/home?region=%s#%s=%s'
# https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#LoadBalancer:loadBalancerArn=nklb-classic
DEFAULT_BASE_URL = 'https://console.aws.amazon.com'
BUCKET_ACCEPTED_PERMISSIONS = ['FULL_CONTROL', 'READ', 'WRITE', 'READ_ACP',
                               'WRITE_ACP']
BUCKET_ACCEPTED_URIS = [
    'http://acs.amazonaws.com/groups/global/AllUsers',
    'http://acs.amazonaws.com/groups/global/AuthenticatedUsers'
]
# maximum value for MaxResults (AWS limitation)
MAX_RESULTS = 1000
CSV_FORMAT_PATTERN = r'\.csv.(gz|zip)$'
PARQUET_FORMAT_PATTERN = r'\.snappy.parquet$'
GROUP_DATES_PATTERNS = {
    2: ['BILLING_PERIOD=[0-9]{4}-[0-9]{2}/'],
    1: ['[0-9]{8}-[0-9]{8}/',
        'year=[0-9]{4}/month=([1-9]|1[0-2])/']
}


AUTH_ERROR_CODES = {
    'AuthFailure', 'AccessDenied', 'AccessDeniedException',
    'UnauthorizedOperation', 'UnrecognizedClientException',
    'InvalidClientTokenId', 'ExpiredToken', 'InvalidToken',
    'SignatureDoesNotMatch', 'InvalidSignatureException',
}

THROTTLE_ERROR_CODES = {
    'RequestLimitExceeded', 'Throttling', 'ThrottlingException',
    'TooManyRequestsException', 'ProvisionedThroughputExceededException',
}

def _is_auth_error(exc) -> bool:

    if isinstance(exc, ClientError):
        meta = exc.response.get('ResponseMetadata', {})
        if meta.get('HTTPStatusCode') in (401, 403):
            return True
        code = (exc.response.get('Error') or {}).get('Code')
        if code in AUTH_ERROR_CODES:
            return True
    msg = str(exc) or ""
    needles = [
        "was not able to validate the provided access credentials",
        "is not authorized to perform",
        "AccessDenied", "AuthFailure", "UnauthorizedOperation",
        "HTTP 401", "HTTP 403",
    ]
    return any(n.lower() in msg.lower() for n in needles)


def _retry_on_error(exc):
    if _is_auth_error(exc):
        return False

    if isinstance(exc, (ResponseParserError, EndpointConnectionError, SSLError)):
        return True

    if isinstance(exc, ClientError):
        code = (exc.response.get('Error') or {}).get('Code')
        if code in THROTTLE_ERROR_CODES:
            return True

    if isinstance(exc, WaiterError):
        reason = exc.kwargs.get('reason', '') or ''
        if 'Request limit exceeded' in reason or 'Throttl' in reason:
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
        CloudParameter(name='region_name', type=str, required=False),

        CloudParameter(name='assume_role_account_id', type=str,
                       required=False),
        CloudParameter(name='assume_role_name', type=str, required=False),
        CloudParameter(name='assume_role_session_name', type=str,
                       required=False),

        # Service parameters
        CloudParameter(name='cur_version', type=int, required=False),
        CloudParameter(name='use_edp_discount', type=bool, required=False)
    ]
    DEFAULT_S3_REGION_NAME = 'eu-central-1'
    SUPPORTS_REPORT_UPLOAD = True

    def get_session(self, access_key=None, secret_key=None, region_name=None):
        role_account_id = self.config.get('assume_role_account_id')
        role_name = self.config.get('assume_role_name')
        role_session_name = self.config.get('assume_role_session_name',
                                            'opt-session')

        def refresh_session():
            nonlocal access_key, secret_key, region_name

            if not access_key:
                access_key = self.config.get('access_key_id')
            if not secret_key:
                secret_key = self.config.get('secret_access_key')
            if not region_name:
                region_name = self.config.get('region_name',
                                              self.DEFAULT_S3_REGION_NAME)

            base_session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region_name,
            )

            sts_client = base_session.client('sts', config=IAM_CLIENT_CONFIG)
            response = sts_client.assume_role(
                RoleArn=f'arn:aws:iam::{role_account_id}:role/{role_name}',
                RoleSessionName=role_session_name,
            )
            creds = response['Credentials']
            self._session = boto3.Session(
                aws_access_key_id=creds['AccessKeyId'],
                aws_secret_access_key=creds['SecretAccessKey'],
                aws_session_token=creds['SessionToken'],
                region_name=region_name,
            )

        if not (role_account_id and role_name):
            return super().get_session(access_key, secret_key, region_name)

        if not hasattr(self, '_session') or self._session is None:
            refresh_session()

        try:
            self._session.client('sts').get_caller_identity()
        except ClientError as exc:
            err_code = exc.response['Error'].get('Code')
            if err_code in ['ExpiredToken', 'InvalidToken']:
                refresh_session()
            else:
                raise

        return self._session

    def discovery_calls_map(self):
        return {
            VolumeResource: self.volume_discovery_calls,
            InstanceResource: self.instance_discovery_calls,
            SnapshotResource: self.snapshot_discovery_calls,
            IpAddressResource: self.ip_address_discovery_calls,
            BucketResource: self.bucket_discovery_calls,
            LoadBalancerResource: self.load_balancer_discovery_calls,
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
    def logs(self):
        return self.session.client('logs')

    @property
    def cf(self):
        return self.session.client("cloudformation")

    @property
    def cur(self):
        # hardcoded, because service is only available in us-east-1
        return self.session.client('cur', 'us-east-1')

    @property
    def cur_2(self):
        return self.session.client('bcm-data-exports')

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
        region_name = self.config.get("region_name")
        if region_name and region_name not in self._get_coordinates_map():
            raise InvalidParameterException(f"Invalid region: {region_name}")
        try:
            result = self._retry(self.sts.get_caller_identity)
        except (ClientError, InvalidRegionError,
                EndpointConnectionError) as ex:
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
            LoadBalancerResource: CLOUD_LINK_PATTERN % (
                DEFAULT_BASE_URL, 'ec2', region,
                'LoadBalancer:loadBalancerArn', resource_value),
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
                    sg_ids = [x['GroupId'] for x in instance.get(
                        'SecurityGroups', [])]
                    dates = [x['Ebs']['AttachTime'] for x in instance[
                        'BlockDeviceMappings'] if 'Ebs' in x]
                    dates.extend(list(map(
                        lambda x: x['Attachment']['AttachTime'],
                        instance.get('NetworkInterfaces', []))))
                    cloud_created = min(
                        dates, default=None) or instance['LaunchTime']
                    spotted = instance.get('InstanceLifecycle') == 'spot'
                    vpc_id = instance.get('VpcId')
                    architecture = instance.get('Architecture')
                    instance_resource = InstanceResource(
                        cloud_resource_id=instance['InstanceId'],
                        cloud_account_id=self.cloud_account_id,
                        region=region,
                        name=self._extract_tag(instance, 'Name'),
                        flavor=instance['InstanceType'],
                        architecture=architecture,
                        security_groups=sg_ids,
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

    def _get_bucket_public_settings(self, bucket_s3, s3_client, bucket_name):
        """
        Inspect S3 bucket public settings.

        This helper inspects a bucket's public configuration in three places:
        - PublicAccessBlock (BlockPublicPolicy / BlockPublicAcls)
        - Bucket policy public status (get_bucket_policy_status)
        - Bucket ACLs (get_bucket_acl)

        It returns a dict with:
        - is_public_policy: True if bucket policy makes the bucket public
        - is_public_acls: True if any ACL grant makes the bucket public
        - public_access_block: raw result from get_public_access_block (may be empty)

        Note: method tolerates missing configurations and maps known ClientError
        codes (e.g. NoSuchPublicAccessBlockConfiguration, NoSuchBucketPolicy)
        to non-fatal behavior.
        """
        
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
            return {
                'is_public_policy': False,
                'is_public_acls': False,
                'public_access_block': public_access_block
            }

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
        
        result = {
            'is_public_policy': is_public_policy,
            'is_public_acls': is_public_acls,
            'public_access_block': public_access_block,
        }

        return result
    
    def _get_bucket_intelligent_tiering_metadata(self, s3_client, bucket_name):
        """
        Gather Intelligent-Tiering and related storage metadata for a bucket.

        The returned metadata is a dictionary with the following keys:
        - intelligent_tiering_enabled (bool): whether any Intelligent-Tiering
          configuration exists for the bucket.
        - intelligent_tiering_configs (list): raw IntelligentTieringConfigurationList.
        - lifecycle_rules (list): bucket lifecycle configuration rules (if any).
        - has_lifecycle (bool): True when lifecycle configuration exists.
        - storage_class_analysis (list): analytics configuration list (if any).
        - metrics_configurations (list): metrics configuration list (if any).
        - total_size_bytes (int|None): aggregated bucket size in bytes (CloudWatch),
          if available.
        - object_count (int|None): estimated or exact number of objects in bucket.
        - access_pattern (deprecated|placeholder): reserved for future use.
        - it_status_bucket (str): 'enabled' when intelligent-tiering applies to
          the full bucket, otherwise 'disabled'.
        - tiers (list): list of [display_name, size_gb] pairs for detected storage tiers.
        - last_checked (list): ISO dates (YYYY-MM-DD) where GET object activity was detected.

        Behavior summary:
        - Attempts to read Intelligent-Tiering configurations (list_bucket_intelligent_tiering_configurations)
          and determines whether IT applies to the entire bucket (no filter or empty prefix).
        - Reads lifecycle, analytics and metrics configs where available, ignoring
          known "no such configuration" errors.
        - Tries to obtain object count by sampling list_objects_v2 (MaxKeys=1000).
          If sample returns 1000 items (potentially large bucket), falls back to CloudWatch
          NumberOfObjects metric (7-day window). For smaller buckets it paginates to compute
          an accurate object count.
        - Uses CloudWatch BucketSizeBytes metric (7-day window) per storage type to
          compute total_size_bytes and per-tier sizes.
        - Collects last access dates using CloudWatch GetRequests (sum per day)
          for the last 30 days and returns dates where Sum > 0 in last_checked.
        - All network/cloud errors are caught and logged; missing data remains None
          or empty lists as appropriate.

        Parameters:
        - s3_client: boto3 S3 client already configured for the bucket's region.
        - bucket_name: name of the bucket to inspect.

        Returns:
        - dict described above containing metadata about intelligent-tiering and storage metrics.
        """
        metadata = {
        'intelligent_tiering_enabled': False,
        'intelligent_tiering_configs': [],
        'lifecycle_rules': [],
        'has_lifecycle': False,
        'storage_class_analysis': [],
        'metrics_configurations': [],
        'total_size_bytes': None,
        'object_count': None,
        'access_pattern': None,
        'it_status_bucket': None,
        'tiers': [],
        'last_checked': []
    }
        try:
            it_configs = s3_client.list_bucket_intelligent_tiering_configurations(
                Bucket=bucket_name
            )
            configs_list = it_configs.get('IntelligentTieringConfigurationList', [])
            metadata['intelligent_tiering_enabled'] = bool(configs_list)
            metadata['intelligent_tiering_configs'] = configs_list
            # Check if IT applies to entire bucket (no filter or empty prefix)
            full_bucket = False
            for cfg in configs_list:
                flt = cfg.get('Filter')
                if not flt:
                    full_bucket = True
                    break
                # Check for empty prefix or no tags
                prefix = flt.get('Prefix')
                and_map = flt.get('And', {}) if isinstance(flt, dict) else {}
                and_prefix = and_map.get('Prefix')
                and_tags = and_map.get('Tags')
                if (prefix == '' or prefix is None) and (not and_tags) and (and_prefix in (None, '')):
                    full_bucket = True
                    break
            metadata['it_status_bucket'] = 'enabled' if (metadata['intelligent_tiering_enabled'] and full_bucket) else 'disabled'
        except ClientError as exc:
            if exc.response['Error'].get('Code') != 'NoSuchConfiguration':
                LOG.warning(f"[IT] Failed to get Intelligent-Tiering config for bucket {bucket_name}: {str(exc)}")

        try:
            lifecycle = s3_client.get_bucket_lifecycle_configuration(
                Bucket=bucket_name
            )
            metadata['lifecycle_rules'] = lifecycle.get('Rules', [])
            metadata['has_lifecycle'] = True
        except ClientError as exc:
            if exc.response['Error'].get('Code') != 'NoSuchLifecycleConfiguration':
                LOG.warning(f"[IT] Failed to get lifecycle config for bucket {bucket_name}: {str(exc)}")

        try:
            analytics = s3_client.list_bucket_analytics_configurations(
                Bucket=bucket_name
            )
            metadata['storage_class_analysis'] = analytics.get(
                'AnalyticsConfigurationList', []
            )
        except ClientError as exc:
            if exc.response['Error'].get('Code') not in ['NoSuchConfiguration', 'NoSuchAnalyticsConfiguration']:
                LOG.warning(f"[IT] Failed to get analytics config for bucket {bucket_name}: {str(exc)}")

        try:
            metrics = s3_client.list_bucket_metrics_configurations(
                Bucket=bucket_name
            )
            metadata['metrics_configurations'] = metrics.get(
                'MetricsConfigurationList', []
            )
        except ClientError as exc:
            if exc.response['Error'].get('Code') not in ['NoSuchConfiguration', 'NoSuchMetricsConfiguration']:
                LOG.warning(f"[IT] Failed to get metrics config for bucket {bucket_name}: {str(exc)}") 

        # Get bucket size and object count via CloudWatch
        try:
            region_name = s3_client.meta.region_name
            cloudwatch = self.session.client('cloudwatch', region_name=region_name)

            def _latest_value(datapoints):
                if not datapoints:
                    return None
                # Get most recent value from CloudWatch
                last = sorted(datapoints, key=lambda x: x['Timestamp'])[-1]
                return last.get('Average') or last.get('Sum') or last.get('Maximum') or last.get('Minimum')

            object_count_val = None
            try:
                # Sample bucket to estimate object count
                sample_response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    MaxKeys=1000
                )
                
                if not sample_response.get('Contents'):
                    object_count_val = 0
                    LOG.info(f"[IT] Bucket {bucket_name} is empty: 0 objects")
                else:
                    # Filter out directories - only count actual objects
                    def is_actual_object(obj):
                        key = obj.get('Key', '')
                        size = obj.get('Size', 0)
                        return size > 0 or not key.endswith('/')
                    
                    actual_objects = [obj for obj in sample_response['Contents'] if is_actual_object(obj)]
                    sample_count = len(actual_objects)
                    
                    # For large buckets, use CloudWatch
                    if len(sample_response['Contents']) == 1000:
                        objects_stats = cloudwatch.get_metric_statistics(
                            Namespace='AWS/S3',
                            MetricName='NumberOfObjects',
                            Dimensions=[
                                {'Name': 'BucketName', 'Value': bucket_name},
                                {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
                            ],
                            StartTime=datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=7),
                            EndTime=datetime.utcnow().replace(tzinfo=timezone.utc),
                            Period=24 * 60 * 60,
                            Statistics=['Average']
                        )
                        cloudwatch_count = _latest_value(objects_stats.get('Datapoints', []))
                        if cloudwatch_count is not None:
                            object_count_val = int(cloudwatch_count)
                            LOG.info(f"[IT] Using CloudWatch object count for large bucket {bucket_name}: {object_count_val}")
                        else:
                            LOG.warning(f"[IT] CloudWatch returned no data for bucket {bucket_name}, using sample estimate")
                            object_count_val = sample_count
                    else:
                        # For smaller buckets, paginate to get accurate count
                        total_objects = sample_count
                        continuation_token = sample_response.get('NextContinuationToken')
                        
                        while continuation_token:
                            try:
                                response = s3_client.list_objects_v2(
                                    Bucket=bucket_name,
                                    ContinuationToken=continuation_token
                                )
                                
                                if response.get('Contents'):
                                    actual_objects = [obj for obj in response['Contents'] if is_actual_object(obj)]
                                    total_objects += len(actual_objects)
                                
                                continuation_token = response.get('NextContinuationToken')
                                
                            except Exception as page_exc:
                                LOG.warning(f"[IT] Failed to get page for bucket {bucket_name}: {str(page_exc)}")
                                break
                        
                        object_count_val = total_objects
                        LOG.info(f"[IT] Accurate object count for bucket {bucket_name}: {object_count_val}")
                        
            except Exception as exc:
                LOG.warning(f"[IT] Failed to get accurate object count for bucket {bucket_name}: {str(exc)}")
                # Fallback to CloudWatch if sampling fails
                try:
                    objects_stats = cloudwatch.get_metric_statistics(
                        Namespace='AWS/S3',
                        MetricName='NumberOfObjects',
                        Dimensions=[
                            {'Name': 'BucketName', 'Value': bucket_name},
                            {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
                        ],
                        StartTime=datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=7),
                        EndTime=datetime.utcnow().replace(tzinfo=timezone.utc),
                        Period=24 * 60 * 60,
                        Statistics=['Average']
                    )
                    cloudwatch_count = _latest_value(objects_stats.get('Datapoints', []))
                    if cloudwatch_count is not None:
                        object_count_val = int(cloudwatch_count)
                        LOG.warning(f"[IT] Using CloudWatch fallback for bucket {bucket_name} (may include prefixes): {object_count_val}")
                    else:
                        LOG.warning(f"[IT] CloudWatch fallback also failed for bucket {bucket_name}")
                except Exception as fallback_exc:
                    LOG.warning(f"[IT] Failed to get CloudWatch fallback for bucket {bucket_name}: {str(fallback_exc)}")

            # BucketSizeBytes by StorageType
            storage_types = [
                'StandardStorage',
                'StandardIAStorage',
                'OneZoneIAStorage',
                'ReducedRedundancyStorage',
                'GlacierStorage',
                'GlacierInstantRetrievalStorage',
                'GlacierStagingStorage',
                'GlacierS3ObjectOverhead',
                'IntelligentTieringFAStorage',
                'IntelligentTieringIAStorage',
                'IntelligentTieringAAStorage',
                'IntelligentTieringDAAStorage',
                'DeepArchiveStorage',
                'DeepArchiveS3ObjectOverhead',
            ]
            total_size = 0
            any_size_dp = False
            tiers_bytes = {}
            for st in storage_types:
                size_stats = cloudwatch.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName='BucketSizeBytes',
                    Dimensions=[
                        {'Name': 'BucketName', 'Value': bucket_name},
                        {'Name': 'StorageType', 'Value': st}
                    ],
                    StartTime=datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=7),
                    EndTime=datetime.utcnow().replace(tzinfo=timezone.utc),
                    Period=24 * 60 * 60,
                    Statistics=['Average']
                )
                val = _latest_value(size_stats.get('Datapoints', []))
                if val is not None:
                    any_size_dp = True
                    total_size += int(val)
                    tiers_bytes[st] = int(val)

            if any_size_dp:
                metadata['total_size_bytes'] = int(total_size)
            if object_count_val is not None:
                metadata['object_count'] = int(object_count_val)

            # Build tiers list with sizes in GB
            def _display_name(storage_type):
                mapping = {
                    'StandardStorage': 'Standard',
                    'StandardIAStorage': 'Standard-IA',
                    'OneZoneIAStorage': 'One Zone-IA',
                    'ReducedRedundancyStorage': 'RRS',
                    'GlacierStorage': 'Glacier',
                    'GlacierInstantRetrievalStorage': 'Glacier IR',
                    'GlacierStagingStorage': 'Glacier Staging',
                    'GlacierS3ObjectOverhead': 'Glacier Overhead',
                    'IntelligentTieringFAStorage': 'Intelligent Tiering - Frequent',
                    'IntelligentTieringIAStorage': 'Intelligent Tiering - Infrequent',
                    'IntelligentTieringAAStorage': 'Intelligent Tiering - Archive Access',
                    'IntelligentTieringDAAStorage': 'Intelligent Tiering - Deep Archive Access',
                    'DeepArchiveStorage': 'Deep Archive',
                    'DeepArchiveS3ObjectOverhead': 'Deep Archive Overhead',
                }
                return mapping.get(storage_type, storage_type)

            tiers_list = []
            BYTES_IN_GB = 1024 ** 3
            for st, b in tiers_bytes.items():
                size_gb = round(b / BYTES_IN_GB, 3)
                tiers_list.append([_display_name(st), size_gb])
            metadata['tiers'] = tiers_list
        except Exception as exc:
            LOG.warning(f"[IT] Failed to fetch CloudWatch metrics for bucket {bucket_name}: {str(exc)}")

        # Get last_checked dates from GET requests
        try:
            region_name = s3_client.meta.region_name
            cloudwatch = self.session.client('cloudwatch', region_name=region_name)
            
            get_requests_metric = 'GetRequests'
            dates_with_object_access = []
            
            try:
                get_stats = cloudwatch.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName=get_requests_metric,
                    Dimensions=[
                        {'Name': 'BucketName', 'Value': bucket_name},
                        {'Name': 'FilterId', 'Value': 'EntireBucket'}
                    ],
                    StartTime=datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=30),
                    EndTime=datetime.utcnow().replace(tzinfo=timezone.utc),
                    Period=24 * 60 * 60,
                    Statistics=['Sum']
                )
                get_dps = get_stats.get('Datapoints', [])
                
                # Collect dates with GET requests
                for dp in get_dps:
                    if dp.get('Sum', 0) > 0:
                        ts = dp.get('Timestamp')
                        if isinstance(ts, datetime):
                            dates_with_object_access.append(ts.date().isoformat())
                
                # Store unique sorted dates
                if dates_with_object_access:
                    metadata['last_checked'] = sorted(list(set(dates_with_object_access)))
                    LOG.info(f"[IT] Bucket {bucket_name} had object GETs on dates: {metadata['last_checked']}")
                else:
                    metadata['last_checked'] = []
                    LOG.info(f"[IT] Bucket {bucket_name} had no object GETs in the last 30 days")
                    
            except Exception as exc:
                LOG.warning(f"[IT] Failed to get {get_requests_metric} metrics for bucket {bucket_name}: {str(exc)}")
                metadata['last_checked'] = []
            
        except Exception as exc:
            LOG.warning(f"[IT] Failed to get access metrics for bucket {bucket_name}: {str(exc)}")
            metadata['last_checked'] = []

        return metadata

    @staticmethod
    def get_region_from_location(region_info):
        if not region_info['LocationConstraint']:
            # LocationConstraint will be None if bucket is located in us-east-1
            region = 'us-east-1'
        elif region_info['LocationConstraint'].lower() == 'eu':
            # LocationConstraint will be EU if bucket is located in eu-west-1
            region = 'eu-west-1'
        else:
            region = region_info['LocationConstraint']
        return region

    def discover_bucket_info(self, bucket_name):
        region_info = self.s3.get_bucket_location(Bucket=bucket_name)
        region = self.get_region_from_location(region_info)

        # get_bucket_tagging fails for eu-south-1 if region is not set
        # explicitly, so we find region first and initialize client for
        # specific region
        s3 = self.session.client('s3', region_name=region)

        public_and_tiering = self._get_bucket_public_settings(s3, s3, bucket_name)
        is_public_policy = public_and_tiering.get('is_public_policy', False)
        is_public_acls = public_and_tiering.get('is_public_acls', False)

        try:
            tags = s3.get_bucket_tagging(Bucket=bucket_name)
        except ClientError as exc:
            err_code = exc.response['Error'].get('Code')
            if err_code and err_code == 'NoSuchTagSet':
                tags = {}
            else:
                raise

        it_metadata = self._get_bucket_intelligent_tiering_metadata(
            s3_client=s3,
            bucket_name=bucket_name
        )

        bucket_resource = BucketResource(
            cloud_resource_id=bucket_name,
            cloud_account_id=self.cloud_account_id,
            region=region,
            organization_id=self.organization_id,
            name=bucket_name,
            tags=self._extract_tags(tags, dict_name='TagSet'),
            is_public_policy=is_public_policy,
            is_public_acls=is_public_acls,
            intelligent_tiering_enabled=it_metadata.get('intelligent_tiering_enabled', False),
            intelligent_tiering_configs=it_metadata.get('intelligent_tiering_configs', []),
            lifecycle_rules=it_metadata.get('lifecycle_rules', []),
            storage_class_analysis=it_metadata.get('storage_class_analysis', []),
            metrics_configurations=it_metadata.get('metrics_configurations', []),
            total_size_bytes=it_metadata.get('total_size_bytes'),
            object_count=it_metadata.get('object_count'),
            it_status_bucket=it_metadata.get('it_status_bucket'),
            tiers=it_metadata.get('tiers', []),
            last_checked=it_metadata.get('last_checked', []),
        )

        self._set_cloud_link(bucket_resource, region)
        yield bucket_resource

    def bucket_discovery_calls(self):
        """
        Returns list of discovery calls to discover buckets presented
        as tuples (adapter_method, arguments_tuple)
        """
        result = list()
        paginator = self.s3.get_paginator('list_buckets')
        page_iterator  = paginator.paginate()
        for page in page_iterator:
            for bucket in page['Buckets']:
                result.append((self.discover_bucket_info, (bucket['Name'],)))
        LOG.debug("Detected buckets: %s", [x[1][0] for x in result])
        return result

    @staticmethod
    def _parse_lb_tags(response):
        tags = {}
        if response:
            tags = {x['Key']: x['Value'] for x in response[0].get('Tags', [])}
        return tags

    def discover_region_lbs_v2(self, region):
        session = self.get_session()
        elb = session.client('elbv2', region)
        lbs = elb.describe_load_balancers().get('LoadBalancers', [])
        for lb in lbs:
            lb_arn = lb['LoadBalancerArn']
            tags = elb.describe_tags(ResourceArns=[lb_arn]).get(
                'TagDescriptions', [])
            tags = self._parse_lb_tags(tags)
            lb_resource = LoadBalancerResource(
                name=lb['LoadBalancerName'],
                cloud_resource_id=lb_arn,
                cloud_account_id=self.cloud_account_id,
                organization_id=self.organization_id,
                region=region,
                vpc_id=lb['VpcId'],
                security_groups=lb.get('SecurityGroups'),
                category=lb.get('Type'),
                tags=tags,
                cloud_console_link=self._generate_cloud_link(
                    LoadBalancerResource, region, lb_arn),
            )
            yield lb_resource

    def discover_region_lbs(self, region):
        """Discover "classic" load balancer resources"""
        session = self.get_session()
        elb = session.client('elb', region)
        lbs = elb.describe_load_balancers().get(
            'LoadBalancerDescriptions', [])
        for lb in lbs:
            name = lb['LoadBalancerName']
            tags = elb.describe_tags(LoadBalancerNames=[name]).get(
                'TagDescriptions', [])
            tags = self._parse_lb_tags(tags)
            # ARN is not returned for classic LBs, generate it
            cloud_resource_id = (f'arn:aws:elasticloadbalancing:{region}:'
                                 f'{self.config["account_id"]}:'
                                 f'loadbalancer/{name}')
            lb_resource = LoadBalancerResource(
                name=name,
                cloud_resource_id=cloud_resource_id,
                cloud_account_id=self.cloud_account_id,
                organization_id=self.organization_id,
                region=region,
                vpc_id=lb['VPCId'],
                security_groups=lb.get('SecurityGroups'),
                tags=tags,
                category='classic',
                cloud_console_link=self._generate_cloud_link(
                    LoadBalancerResource, region, name),
            )
            yield lb_resource

    def load_balancer_discovery_calls(self):
        """
        Returns list of discovery calls to discover load balancers presented
        as tuples (adapter_method, arguments_tuple)
        """
        result = []
        for r in self.list_regions():
            result.append((self.discover_region_lbs_v2, (r,)))
            result.append((self.discover_region_lbs, (r,)))
        return result

    def pod_discovery_calls(self):
        return []

    def snapshot_chain_discovery_calls(self):
        return []

    def rds_instance_discovery_calls(self):
        return []

    @staticmethod
    def _get_network_interfaces_attachments(client, eni_ids):
        result = {}
        enis = client.describe_network_interfaces(
            NetworkInterfaceIds=eni_ids)
        for eni in enis['NetworkInterfaces']:
            available = eni.get('Status') == 'available'
            if not available:
                instance_id = eni.get('Attachment', {}).get(
                    'InstanceId') or eni.get('Description')
                result[eni['NetworkInterfaceId']] = instance_id
        return result

    def discover_region_ip_addresses(self, region):
        instance_map = {}
        ec2 = self.session.client('ec2', region)
        described_ip_addresses = ec2.describe_addresses()
        eni_ids = []
        instance_ids = []
        for address in described_ip_addresses['Addresses']:
            eni_id = address.get('NetworkInterfaceId')
            instance_id = address.get('InstanceId')
            if instance_id:
                instance_ids.append(instance_id)
            elif eni_id:
                eni_ids.append(eni_id)
        if instance_ids:
            described_instances = ec2.describe_instances(
                InstanceIds=instance_ids)
            for reservation in described_instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_map.update({instance['InstanceId']: instance.get(
                        'State', {}).get('Name')})
        eni_instance_map = self._get_network_interfaces_attachments(
            ec2, eni_ids)
        for address in described_ip_addresses['Addresses']:
            available = True
            instance_id = address.get('InstanceId')
            eni_id = address.get('NetworkInterfaceId')
            if instance_id:
                available = instance_map.get(instance_id) == 'terminated'
            elif eni_id:
                instance_id = eni_instance_map.get(eni_id)
                if instance_id:
                    available = False
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
                # replace daily reports with the latest
                # for "create_new" report versioning
                path = r['Key']
                day = path.split(common_prefix)[1].split(report_name)[0]
                if day:
                    for rgx in [el for el_l in GROUP_DATES_PATTERNS.values()
                                for el in el_l]:
                        if re.search(rgx, day):
                            day = re.sub(rgx, '', day)
                            break
                key = path.replace(day, '')
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

        reports = self.find_reports_by_format(resp, CSV_FORMAT_PATTERN)
        if not reports:
            reports = self.find_reports_by_format(resp, PARQUET_FORMAT_PATTERN)

        if not reports:
            raise ReportFilesNotFoundException(
                'Report files for report {} not found in bucket {}. Please '
                'check your CUR version and existence of report files in the '
                'bucket'.format(report_name, bucket_name))
        return reports

    def find_reports_by_format(self, s3_objects, format_pattern):
        reports = defaultdict(list)
        group_dates_patterns = None
        cur_version = self.config.get('cur_version')
        if cur_version:
            group_dates_patterns = GROUP_DATES_PATTERNS.get(cur_version)
        if not group_dates_patterns:
            group_dates_patterns = GROUP_DATES_PATTERNS[2] + GROUP_DATES_PATTERNS[1]

        group_part = None
        try:
            report_candidates = [f for f in s3_objects['Contents']
                                 if re.search(format_pattern, f['Key'])]
            for group_pattern in group_dates_patterns:
                if any(re.search(group_pattern, report['Key'])
                       for report in report_candidates):
                    group_part = group_pattern
                    if not cur_version:
                        version = [k for k, v in GROUP_DATES_PATTERNS.items()
                                   if group_part in v][0]
                        LOG.info('Detected CUR version: %s', version)
                        self.config['cur_version'] = version
                    break
            if group_part:
                for report in report_candidates:
                    group = re.search(group_part, report['Key'])
                    if group:
                        common_group = self._group_to_daterange(group.group(0))
                        reports[common_group].append(report)
        except KeyError:
            pass
        return reports

    @staticmethod
    def _group_to_daterange(group):
        if 'BILLING_PERIOD' in group:
            year = int(group[-8:-4])
            month = int(group[-3:-1])
        elif 'year=' in group:
            year = int(group[5:].split('/')[0])
            month = int(group.split('month=')[1].split('/')[0])
        else:
            return group.replace('/', '')
        if month == 12:
            next_year = year + 1
            next_month = 1
        else:
            next_year = year
            next_month = month + 1
        return '{0}{1}01-{2}{3}01'.format(year, f'{month:02d}',
                                          next_year, f'{next_month:02d}')

    def download_report_file(self, report_name, file_obj):
        self.s3.download_fileobj(
            self.config['bucket_name'], report_name, file_obj)

    def configure_bucket_policy(self, bucket_name):
        account_id = self.validate_credentials()['account_id']
        bucket_policy = AwsTemplates.get_bucket_policy(bucket_name, account_id)
        return self.s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy),
        )

    def get_bucket_region(self, bucket_name):
        try:
            bucket_location = self.s3.get_bucket_location(Bucket=bucket_name)
            return self.get_region_from_location(bucket_location)
        except self.s3.exceptions.NoSuchBucket:
            raise BucketNotFoundException(
                'Bucket {} not found'.format(bucket_name))
        except ParamValidationError:
            raise BucketNameValidationError(
                'Bucket name "{}" has incorrect format'.format(bucket_name))

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
            location = self.config.get('region_name',
                                      self.DEFAULT_S3_REGION_NAME)
            if location == 'us-east-1':
                # us-east-1 location is not supported, bucket is created in
                # us-east-1 by default
                return self.s3.create_bucket(
                    Bucket=bucket_name,
                    ACL='private'
                )
            return self.s3.create_bucket(
                Bucket=bucket_name,
                ACL='private',
                CreateBucketConfiguration={
                    'LocationConstraint': location
                })

        actions = [
            ('create bucket {}'.format(bucket_name),
             create_bucket),
            ('configure bucket {} policy'.format(bucket_name),
             self.configure_bucket_policy)
        ]
        for step, func in actions:
            self._wrap(step, create_bucket_for_report_inner, func)

    def _find_exports(self):
        result = []
        for r in self.cur_2.list_exports()['Exports']:
            export = self.cur_2.get_export(ExportArn=r['ExportArn'])['Export']
            format_map = {
                'TEXT_OR_CSV': 'textORcsv', 'PARQUET': 'Parquet'
            }
            destination = export['DestinationConfigurations']['S3Destination']
            s3_conf = destination['S3OutputConfigurations']
            cost_and_usage_report = export['DataQuery'][
                'TableConfigurations'].get('COST_AND_USAGE_REPORT')
            if not cost_and_usage_report:
                continue
            result.append({
                'ReportName': export['Name'],
                'TimeUnit': cost_and_usage_report['TIME_GRANULARITY'],
                'Format': format_map.get(s3_conf['Format']) or s3_conf['Format'],
                'Compression': format_map.get(
                    s3_conf['Compression']) or s3_conf['Compression'],
                'S3Bucket': destination['S3Bucket'],
                'S3Prefix': destination['S3Prefix'],
                'S3Region': destination['S3Region'],
                'ReportVersioning': s3_conf['Overwrite'],
                'AdditionalSchemaElements': ['RESOURCES'],
                'RefreshClosedReports': True
            })
        return result

    def find_reports(self, name=None, raise_on_bad_config=False,
                     search_criteria=None, **kwargs):
        res = []
        if self.config.get('cur_version') == 2:
            reports = self._find_exports()
        else:
            reports = self.cur.describe_report_definitions()['ReportDefinitions']
        for r in reports:
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
        except ReportConfigurationException as exc:
            exc_str = str(exc) + (". Please try to set correct region name "
                                  "and check permissions for user and bucket")
            raise ReportConfigurationException(exc_str)

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

            def create_export(definition):
                try:
                    self.cur_2.create_export(
                        Export=AwsTemplates.get_data_export_template(
                            definition['ReportName'], definition['S3Bucket'],
                            definition['S3Prefix'], definition['S3Region']
                        ))
                except ParamValidationError:
                    raise ReportConfigurationException(
                        'Unable to create report: invalid parameters')
                except self.cur_2.exceptions.ServiceQuotaExceededException:
                    raise ReportConfigurationException(
                        'Unable to create report: quota exceeded')
                except self.cur_2.exceptions.ValidationException:
                    raise ReportConfigurationException(
                        'Unable to create report: validation error')

            report_definition = self.get_report_definition(
                report_name=report_name, bucket_name=bucket_name,
                prefix=prefix,
                region=self.config.get('region_name', self.DEFAULT_S3_REGION_NAME))
            func = create_export if self.config.get(
                'cur_version') == 2 else create_report
            self._wrap('create report {}'.format(report_name),
                       func, report_definition)
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
            'eu-central-1': {'name': 'Europe (Frankfurt)',
                             'alias': 'EU (Frankfurt)',
                             'longitude': 8.65399, 'latitude': 50.12581},
            'eu-central-2': {'name': 'Europe (Zurich)',
                             'longitude': 8.545094, 'latitude': 47.373878},
            'eu-west-1': {'name': 'Europe (Ireland)',
                          'alias': 'EU (Ireland)',
                          'longitude': -6.266155, 'latitude': 53.350140},
            'eu-west-2': {'name': 'Europe (London)',
                          'alias': 'EU (London)',
                          'longitude': -0.11362, 'latitude': 51.51768},
            'eu-west-3': {'name': 'Europe (Paris)',
                          'alias': 'EU (Paris)',
                          'longitude': 2.34293, 'latitude': 48.85717},
            'eu-south-1': {'name': 'Europe (Milan)',
                           'alias': 'EU (Milan)',
                           'latitude': 45.4668, 'longitude': 9.1905},
            'eu-south-2': {'name': 'Europe (Spain)',
                           'latitude': 40.416775, 'longitude': -3.703790},
            'eu-north-1': {'name': 'Europe (Stockholm)',
                           'alias': 'EU (Stockholm)',
                           'longitude': 18.04856, 'latitude': 59.33097},
            'us-east-1': {'name': 'US East (N. Virginia)',
                          'longitude': -78.45, 'latitude': 38.13},
            'us-east-2': {'name': 'US East (Ohio)',
                          'longitude': -83, 'latitude': 39.96},
            'us-west-1': {'name': 'US West (N. California)',
                          'longitude': -121.96, 'latitude': 37.35},
            'us-west-2': {'name': 'US West (Oregon)',
                          'longitude': -123.88, 'latitude': 46.15},
            'af-south-1': {'name': 'Africa (Cape Town)',
                           'latitude': -33.928992, 'longitude': 18.417396},
            'ap-east-1': {'name': 'Asia Pacific (Hong Kong)',
                          'longitude': 114.13624, 'latitude': 22.25424},
            'ap-south-1': {'name': 'Asia Pacific (Mumbai)',
                           'longitude': 72.86730, 'latitude': 19.07257},
            'ap-south-2': {'name': 'Asia Pacific (Hyderabad)',
                           'longitude': 78.491684, 'latitude': 17.387140},
            'ap-northeast-1': {'name': 'Asia Pacific (Tokyo)',
                               'longitude': 139.42, 'latitude': 35.41},
            'ap-northeast-2': {'name': 'Asia Pacific (Seoul)',
                               'longitude': 126.99272, 'latitude': 37.57444},
            'ap-northeast-3': {'name': 'Asia Pacific (Osaka)',
                               'longitude': 135.50674, 'latitude': 34.69857},
            'ap-southeast-1': {'name': 'Asia Pacific (Singapore)',
                               'longitude': 103.851959, 'latitude': 1.290270},
            'ap-southeast-2': {'name': 'Asia Pacific (Sydney)',
                               'longitude': 151.2, 'latitude': -33.8},
            'ap-southeast-3': {'name': 'Asia Pacific (Jakarta)',
                               'longitude': 106.8455, 'latitude': -6.2087},
            'ap-southeast-4': {'name': 'Asia Pacific (Melbourne)',
                               'longitude': 144.946547, 'latitude': -37.840935},
            'ap-southeast-5': {'name': 'Asia Pacific (Malaysia)',
                               'longitude': 101.693207, 'latitude': 3.140853},
            'ap-southeast-7': {'name': 'Asia Pacific (Thailand)',
                               'longitude': 100.523186, 'latitude': 13.736717},
            'ca-central-1': {'name': 'Canada (Central)',
                             'longitude': -73.6, 'latitude': 45.5},
            'ca-west-1': {'name': 'Canada West (Calgary)',
                          'longitude': -114.066666, 'latitude': 51.049999},
            'me-central-1': {'name': 'Middle East (UAE)',
                             'longitude': 55.296249, 'latitude': 24.467776},
            'me-south-1': {'name': 'Middle East (Bahrain)',
                           'longitude': 50.6377716, 'latitude': 25.9304142},
            'sa-east-1': {'name': 'South America (Sao Paulo)',
                          'longitude': -46.8754, 'latitude': -23.6815},
            'cn-north-1': {'name': 'China (Beijing)',
                           'longitude': 116.38570, 'latitude': 39.90388},
            'cn-northwest-1': {'name': 'China (Ningxia)',
                               'longitude': 103.7300, 'latitude': 37.2931},
            'us-gov-east-1': {'name': 'GovCloud (US-East)',
                              'longitude': -83.0235, 'latitude': 39.9653},
            'us-gov-west-1': {'name': 'GovCloud (US-West)',
                              'longitude': -97.09434, 'latitude': 31.78395},
            'il-central-1': {'name': 'Israel (Tel Aviv)',
                             'longitude': 34.855499, 'latitude': 32.109333},
            'mx-central-1': {'name': 'Mexico (Central)',
                             'longitude': -99.133209, 'latitude': 19.432608},
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
            InstanceTypes=flavors,
            StartTime=datetime.now(tz=timezone.utc).replace(tzinfo=None),
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
                cloud_created_at=int(datetime.strptime(
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
                   interval, start_date, end_date, dimension='InstanceId',
                   statistics='Average'):
        """
        Get metric for resources
        :param metric_name: metric name
        :param instance_ids: instance ids
        :param region: instance's region name
        :param interval: time interval in seconds
        :param start_date: metric start datetime date
        :param end_date: metric end datetime date
        :param dimension: metric dimension
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
                        'Name': dimension,
                        'Value': instance_id
                    }],
                    'MetricName': metric_name,
                    'Namespace': namespace,
                    'StartTime': start_date,
                    'EndTime': end_date,
                    'Period': interval,
                    'Statistics': [statistics],
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
            if ('InvalidParameter' in error_message
                    or 'InvalidInput' in error_message):
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
