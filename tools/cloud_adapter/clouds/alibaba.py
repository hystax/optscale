import json
import logging
from datetime import datetime, timezone

import math
from aliyunsdkbssopenapi.request.v20171214 import (
    DescribeInstanceBillRequest,
    DescribePricingModuleRequest,
    GetPayAsYouGoPriceRequest,
    GetSubscriptionPriceRequest,
    QueryUserOmsDataRequest,
    QueryBillOverviewRequest,
    QueryProductListRequest,
)
from aliyunsdkcms.request.v20190101 import (
    DescribeMetricListRequest,
)
from aliyunsdkcore.acs_exception.exceptions import (
    ClientException,
    ServerException
)
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import RpcRequest
from aliyunsdkecs.request.v20140526 import (
    DescribeAvailableResourceRequest,
    DescribeRegionsRequest,
    DescribeDisksRequest,
    DescribeImagesRequest,
    DescribeInstancesRequest,
    DescribeInstanceTypesRequest,
    DescribeInstanceTypeFamiliesRequest,
    DescribeSnapshotLinksRequest,
    DescribeSnapshotsRequest,
    DescribeVpcsRequest,
    StartInstancesRequest,
    StopInstancesRequest
)
from aliyunsdkvpc.request.v20160428 import DescribeEipAddressesRequest
from aliyunsdkram.request.v20150501 import (
    ListPoliciesForUserRequest,
)
from aliyunsdkrds.endpoint import endpoint_data
from aliyunsdkrds.request.v20140815 import (
    DescribeAvailableClassesRequest,
    DescribeDBInstancesRequest,
    DescribeTagsRequest as DescribeRdsTagsRequest,
    DescribeDBInstanceAttributeRequest,
)
from aliyunsdksts.request.v20150401 import (
    GetCallerIdentityRequest,
)
from retrying import retry

from tools.cloud_adapter.exceptions import (
    CloudSettingNotSupported,
    InvalidParameterException,
    RegionNotFoundException,
    PricingNotFoundException,
    ResourceNotFound,
    InvalidResourceStateException
)
from tools.cloud_adapter.clouds.base import CloudBase
from tools.cloud_adapter.model import (
    VolumeResource,
    ImageResource,
    InstanceResource,
    SnapshotChainResource,
    SnapshotResource,
    RdsInstanceResource,
    IpAddressResource,
)
from tools.cloud_adapter.utils import CloudParameter, gbs_to_bytes

BILLING_REGION_ID = 'ap-southeast-1'
DEFAULT_CONNECT_TIMEOUT = 20
DEFAULT_READ_TIMEOUT = 60
SECONDS_IN_DAY = 60 * 60 * 24
LOG = logging.getLogger(__name__)


def _retry_on_error(exc):
    if isinstance(exc, ClientException):
        if exc.get_error_code() == 'SDK.ServerUnreachable':
            return True
        if exc.get_error_code() == 'SDK.HttpError':
            return True
    if isinstance(exc, ServerException):
        if exc.get_error_code() == 'UnknownError':
            return True
        if exc.get_error_code() == 'ServiceUnavailable':
            return True
        if exc.get_error_code() == 'InternalError':
            return True
    return False


class Alibaba(CloudBase):
    BILLING_CREDS = [
        CloudParameter(name='access_key_id', type=str, required=True),
        CloudParameter(name='secret_access_key', type=str, required=True,
                       protected=True),
        CloudParameter(name='skip_refunds', type=bool, required=False)
    ]
    DEFAULT_CURRENCY = 'USD'
    SUPPORTS_REPORT_UPLOAD = False

    _CLOUD_CONSOLE_LINKS = {
        VolumeResource: (
            'https://ecs.console.aliyun.com/#/diskdetail/{id}/detail?'
            'regionId={region_id}'
        ),
        InstanceResource: (
            'https://ecs.console.aliyun.com/#/server/{id}/detail?'
            'regionId={region_id}'
        ),
        SnapshotChainResource: (
            'https://ecs.console.aliyun.com/#/snapshotChainDetail/'
            '{region_id}/{id}/detail'
        ),
        SnapshotResource: (
            # Note: there is a bug in Alibaba UI that may require you to click
            # 'search' manually to actually filter snapshots
            'https://ecs.console.aliyun.com/#/snapshot/region/'
            '{region_id}?snapshotIds={id}'
        ),
        RdsInstanceResource: (
            'https://rdsnext.console.aliyun.com/detail/{id}/basicInfo?'
            'region={region_id}'
        ),
        IpAddressResource: (
            'https://vpc.console.aliyun.com/eip/{region_id}/eips/{id}'
        ),
    }

    def __init__(self, cloud_config, *args, **kwargs):
        self.config = cloud_config
        self._regional_clients = {}
        self._regions_map = {}
        self._currency = self.DEFAULT_CURRENCY

    def discovery_calls_map(self):
        return {
            VolumeResource: self.volume_discovery_calls,
            InstanceResource: self.instance_discovery_calls,
            SnapshotChainResource: self.snapshot_chain_discovery_calls,
            RdsInstanceResource: self.rds_instance_discovery_calls,
            IpAddressResource: self.ip_address_discovery_calls,
        }

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
    def region_id(self):
        return self.config.get('region_id') or BILLING_REGION_ID

    @retry(retry_on_exception=_retry_on_error, wait_fixed=2000,
           stop_max_attempt_number=10)
    def _send_request(self, request, region_id=None):
        region = region_id or self.region_id
        client = self._regional_clients.get(region)
        if not client:
            client = AcsClient(
                ak=self.config['access_key_id'],
                secret=self.config['secret_access_key'],
                region_id=region,
                connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                timeout=DEFAULT_READ_TIMEOUT,
            )
            self._regional_clients[region] = client
        response = client.do_action_with_exception(request)
        return json.loads(response.decode('utf-8'))

    def _send_paged_request(self, request, paged_item, nested_item=None,
                            region_id=None):
        current_page = 1
        while True:
            if hasattr(request, 'set_PageNumber'):
                request.set_PageNumber(current_page)
            elif hasattr(request, 'set_PageNum'):
                request.set_PageNum(current_page)
            else:
                raise ValueError('Can\'t set page number in request')
            response = self._send_request(request, region_id)
            try:
                if nested_item:
                    response = response[nested_item]

                if paged_item + 's' in response:
                    item_list = response[paged_item + 's'][paged_item]
                elif paged_item + 'es' in response:
                    item_list = response[paged_item + 'es'][paged_item]
                elif paged_item + 'List' in response:
                    item_list = response[paged_item + 'List'][paged_item]
                else:
                    item_list = response['Items'][paged_item]

                for item in item_list:
                    yield item

                if 'TotalCount' in response:
                    total_count = response['TotalCount']
                elif 'TotalRecordCount' in response:
                    total_count = response['TotalRecordCount']
                elif len(item_list) == 0:
                    total_count = 0
                else:
                    raise ValueError('Can\'t find record count in '
                                     'response: {}'.format(response))

                if 'PageSize' in response:
                    page_size = response['PageSize']
                else:
                    page_size = request.get_PageSize()

                page_count = math.ceil(total_count / page_size)
                current_page += 1
                if current_page > page_count:
                    break
            except KeyError:
                raise ValueError('Unexpected response format: {}'.format(
                    response))

    def _send_marker_paged_request(self, request, paged_item, nested_item=None,
                                   region_id=None):
        marker = None
        while True:
            if marker:
                if hasattr(request, 'set_Marker'):
                    request.set_Marker(marker)
                elif hasattr(request, 'set_NextToken'):
                    request.set_NextToken(marker)
                else:
                    raise ValueError('Can\'t set page marker in request')
            response = self._send_request(request, region_id)
            try:
                if nested_item:
                    response = response[nested_item]
                marker = response.get('Marker') or response.get('NextToken')
                result = response[paged_item]
                if isinstance(result, str):
                    result = json.loads(result)
                for item in result:
                    yield item
                if not marker:
                    break
            except (KeyError, json.JSONDecodeError):
                raise ValueError('Unexpected response format: {}'.format(
                    response))

    def _list_region_details(self):
        request = DescribeRegionsRequest.DescribeRegionsRequest()
        request.set_AcceptLanguage('en-US')  # The default is Chinese
        return self._send_request(request)['Regions']['Region']

    def _find_region(self, id_or_name):
        if id_or_name not in self._regions_map:
            for region_info in self._list_region_details():
                region_id = region_info['RegionId']
                region_name = region_info['LocalName']
                self._regions_map[region_name] = region_id
                self._regions_map[region_id] = region_id
        region_id = self._regions_map.get(id_or_name)
        if not region_id:
            raise RegionNotFoundException(
                'Region `{}` was not found in cloud'.format(id_or_name))
        return self._regions_map.get(id_or_name)

    def _extract_tags(self, resource_info):
        return {t['TagKey']: t['TagValue']
                for t in resource_info.get('Tags', {}).get('Tag', [])}

    def _datetime_from_str(self, date_str, seconds=False):
        format = '%Y-%m-%dT%H:%M:%SZ' if seconds else '%Y-%m-%dT%H:%MZ'
        return datetime.strptime(date_str, format).replace(tzinfo=timezone.utc)

    def _discover_region_volumes(self, region_details):
        request = DescribeDisksRequest.DescribeDisksRequest()
        request.set_PageSize(100)
        volumes = self._send_paged_request(
            request, paged_item='Disk', region_id=region_details['RegionId'])
        for item in volumes:
            tags = self._extract_tags(item)
            link = self._CLOUD_CONSOLE_LINKS[VolumeResource].format(
                id=item['DiskId'], region_id=region_details['RegionId'])
            resource = VolumeResource(
                cloud_resource_id=item['DiskId'],
                cloud_account_id=self.cloud_account_id,
                region=region_details['LocalName'],
                name=item['DiskName'],
                size=gbs_to_bytes(item['Size']),
                volume_type=item['Category'],
                organization_id=self.organization_id,
                tags=tags,
                attached=item['Status'] == 'In_use',
                snapshot_id=item['SourceSnapshotId'],
                cloud_console_link=link,
            )
            yield resource

    def _discover_region_vpcs(self, region_details):
        request = DescribeVpcsRequest.DescribeVpcsRequest()
        resp = self._send_request(request, region_details['RegionId'])
        vpcs = resp.get('Vpcs')
        if vpcs:
            vpc_list = vpcs.get('Vpc', [])
            if vpc_list:
                return {vpc['VpcId']: vpc.get('VpcName') for vpc in vpc_list if vpc.get('VpcId')}
        return {}

    def _discover_region_instances(self, region_details):
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_PageSize(100)
        instances = self._send_paged_request(
            request, paged_item='Instance',
            region_id=region_details['RegionId'])
        vpc_id_to_name = self._discover_region_vpcs(region_details)
        for item in instances:
            vpc_id = item.get('VpcAttributes', {}).get('VpcId')
            tags = self._extract_tags(item)
            link = self._CLOUD_CONSOLE_LINKS[InstanceResource].format(
                id=item['InstanceId'], region_id=region_details['RegionId'])
            resource = InstanceResource(
                cloud_resource_id=item['InstanceId'],
                cloud_account_id=self.cloud_account_id,
                region=region_details['LocalName'],
                name=item['InstanceName'],
                flavor=item['InstanceType'],
                stopped_allocated=(item['Status'] == 'Stopped' and
                                   item['StoppedMode'] == 'KeepCharging'),
                security_groups=item.get('SecurityGroupIds', {}).get(
                    'SecurityGroupId', []),
                organization_id=self.organization_id,
                tags=tags,
                spotted=item['SpotStrategy'] != 'NoSpot',
                image_id=item['ImageId'],
                cloud_created_at=int(self._datetime_from_str(
                    item['CreationTime']).timestamp()),
                cpu_count=item['Cpu'],
                cloud_console_link=link,
                vpc_id=vpc_id,
                vpc_name=vpc_id_to_name.get(vpc_id)
            )
            yield resource

    def _discover_region_snapshots(self, region_details, chain_id=None):
        request = DescribeSnapshotsRequest.DescribeSnapshotsRequest()
        if chain_id:
            request.set_SnapshotLinkId(chain_id)
        request.set_PageSize(100)
        snapshots = self._send_paged_request(
            request, paged_item='Snapshot',
            region_id=region_details['RegionId'])
        for item in snapshots:
            tags = self._extract_tags(item)
            link = self._CLOUD_CONSOLE_LINKS[SnapshotResource].format(
                id=item['SnapshotId'], region_id=region_details['RegionId'])
            resource = SnapshotResource(
                cloud_resource_id=item['SnapshotId'],
                cloud_account_id=self.cloud_account_id,
                region=region_details['LocalName'],
                organization_id=self.organization_id,
                name=item['SnapshotName'],
                size=gbs_to_bytes(item['SourceDiskSize']),
                description=item['Description'],
                state=item['Status'],
                tags=tags,
                volume_id=item['SourceDiskId'] or None,
                cloud_console_link=link,
            )
            yield resource

    def _discover_region_snapshot_chains(
            self, region_details, include_snapshots=True):
        request = DescribeSnapshotLinksRequest.DescribeSnapshotLinksRequest()
        request.set_PageSize(100)
        snapshot_chains = self._send_paged_request(
            request, paged_item='SnapshotLink',
            region_id=region_details['RegionId'])
        for item in snapshot_chains:
            link = self._CLOUD_CONSOLE_LINKS[SnapshotChainResource].format(
                id=item['SnapshotLinkId'],
                region_id=region_details['RegionId'])
            snapshots = []
            if include_snapshots:
                # Snapshot items do not contain chain IDs, but snapshot list
                # request can filter by chain ID. So, we have to request a
                # snapshot list for each chain
                snapshots = [
                    {
                        'cloud_resource_id': s.cloud_resource_id,
                        'name': s.name,
                        'cloud_console_link': s.cloud_console_link,
                    }
                    for s in self._discover_region_snapshots(
                        region_details, chain_id=item['SnapshotLinkId'])
                ]
            resource = SnapshotChainResource(
                cloud_resource_id=item['SnapshotLinkId'],
                size=item['TotalSize'],
                volume_id=item['SourceDiskId'] or None,
                snapshots=snapshots,
                cloud_account_id=self.cloud_account_id,
                region=region_details['LocalName'],
                organization_id=self.organization_id,
                cloud_console_link=link,
            )
            yield resource

    def _get_rds_tags(self, region_id):
        """
        Get RDS instances tags
        :param region_id: Region ID
        :return: dict with instance IDs as keys and tag maps as values.
            Note that instances without tags won't be present in this dict.
        """
        request = DescribeRdsTagsRequest.DescribeTagsRequest()
        response = self._send_request(request, region_id=region_id)
        tag_map = {}
        try:
            for tag_info in response['Items']['TagInfos']:
                for instance_id in tag_info['DBInstanceIds']['DBInstanceIds']:
                    tag_map.setdefault(instance_id, {}).update({
                        tag_info['TagKey']: tag_info['TagValue']})
        except KeyError:
            raise ValueError('Unexpected response format: {}'.format(
                response))
        return tag_map

    def _get_rds_details(self, instance_ids, region_id):
        page_size = 10  # Up to 10 instance IDs are allowed
        for i in range(0, len(instance_ids), page_size):
            request = (DescribeDBInstanceAttributeRequest
                       .DescribeDBInstanceAttributeRequest())
            chunk_ids = instance_ids[i:i + page_size]
            request.set_DBInstanceId(','.join(chunk_ids))
            response = self._send_request(request, region_id=region_id)
            try:
                for item in response['Items']['DBInstanceAttribute']:
                    yield item
            except KeyError:
                raise ValueError('Unexpected response format: {}'.format(
                    response))

    def _discover_region_rds_instances(self, region_details):
        request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
        request.set_PageSize(100)
        instances = list(self._send_paged_request(
            request, paged_item='DBInstance',
            region_id=region_details['RegionId']))
        instance_ids = [x['DBInstanceId'] for x in instances]
        tag_map = self._get_rds_tags(region_details['RegionId'])
        details_map = {x['DBInstanceId']: x for x in self._get_rds_details(
            instance_ids, region_details['RegionId'])}
        vpc_id_to_name = self._discover_region_vpcs(region_details)
        for item in instances:
            link = self._CLOUD_CONSOLE_LINKS[RdsInstanceResource].format(
                id=item['DBInstanceId'], region_id=region_details['RegionId'])
            details = details_map[item['DBInstanceId']]
            vpc_id = item.get('VpcId')
            resource = RdsInstanceResource(
                cloud_account_id=self.cloud_account_id,
                organization_id=self.organization_id,
                cloud_console_link=link,
                cloud_resource_id=item['DBInstanceId'],
                tags=tag_map.get(item['DBInstanceId'], {}),
                name=details.get('DBInstanceDescription'),
                # Note: there is also DBInstanceClass in basic instance info,
                # but that one seems to be lying: if you create an instance,
                # then change flavor, it will still report the old flavor.
                flavor=details['DBInstanceClass'],
                region=region_details['LocalName'],
                zone_id=details['ZoneId'],
                category=details['Category'],
                engine=details['Engine'],
                engine_version=details['EngineVersion'],
                storage_type=details['DBInstanceStorageType'],
                cpu_count=int(details['DBInstanceCPU']),
                cloud_created_at=int(self._datetime_from_str(
                    details['CreationTime'], seconds=True).timestamp()),
                vpc_id=vpc_id,
                vpc_name=vpc_id_to_name.get(vpc_id)
            )
            yield resource

    def _discover_ip_addresses(self, region_details):
        eip_address_request = DescribeEipAddressesRequest.DescribeEipAddressesRequest()
        eip_address_request.set_PageSize(100)
        ip_addresses = list(self._send_paged_request(
            eip_address_request, paged_item='EipAddress',
            region_id=region_details['RegionId']))
        instance_map = {
            'EcsInstance': {
                'request': DescribeInstancesRequest.DescribeInstancesRequest(),
                'status': 'Status',
                'type': 'Instance',
                'instances': []
            }
        }
        for ip_address in ip_addresses:
            ip_address_id = ip_address['AllocationId']
            link = self._CLOUD_CONSOLE_LINKS[IpAddressResource].format(
                id=ip_address_id, region_id=region_details['RegionId'])
            instance_id = ip_address.get('InstanceId')
            instance_type = ip_address.get('InstanceType')
            available = ip_address['Status'] == 'Available'
            # check instances if ip is not available and instance is not rds
            if instance_id and available is False and instance_type in list(instance_map.keys()):
                instance_type_map = instance_map.get(instance_type, {})
                instance_request = instance_type_map.get('request')
                instance_request.set_PageSize(100)
                paged_type = instance_type_map.get('type')
                instances = instance_type_map.get('instances')
                if not instances:
                    instances = list(self._send_paged_request(
                        instance_request, paged_item=paged_type,
                        region_id=region_details['RegionId']))
                    instance_type_map['instances'] = instances
                ip_current_instance = next((instance for instance in instances
                                            if instance[paged_type + 'Id'] == instance_id), None)
                status_field = instance_type_map.get('status')
                if ip_current_instance:
                    available = ip_current_instance[status_field] == 'Stopped'
            resource = IpAddressResource(
                cloud_account_id=self.cloud_account_id,
                organization_id=self.organization_id,
                name=ip_address.get('Name'),
                cloud_console_link=link,
                cloud_resource_id=ip_address_id,
                region=region_details['LocalName'],
                instance_id=instance_id,
                available=available
            )
            yield resource

    def _discover_region_images(self, region_details, by_owner=True,
                                filter_by=None):
        request = (DescribeImagesRequest.DescribeImagesRequest())
        request.set_PageSize(100)
        if filter_by:
            request.set_Filters(filter_by)
        if by_owner:
            request.set_ImageOwnerAlias('self')
        response = self._send_paged_request(
            request, 'Image', region_id=region_details['RegionId'])
        for image in response:
            image_resource = ImageResource(
                cloud_resource_id=image['ImageId'],
                cloud_account_id=self.cloud_account_id,
                region=region_details['LocalName'],
                name=image.get('ImageName'),
                block_device_mappings=[
                    {
                        'device_name': bdm.get('Device'),
                        'snapshot_id': bdm.get('SnapshotId'),
                        'volume_size': bdm.get('Size'),
                    }
                    for bdm in image.get('DiskDeviceMappings', {}).get(
                        'DiskDeviceMapping', [])
                ],
                cloud_created_at=int(self._datetime_from_str(
                    image['CreationTime'], seconds=True).timestamp()),
                tags=self._extract_tags(image),
            )
            yield image_resource

    def _check_user_policy(self, user_name):
        try:
            policies_request = (
                ListPoliciesForUserRequest.ListPoliciesForUserRequest())
            policies_request.set_UserName(user_name)
            policies = self._send_request(policies_request)
            has_required_policy = any(
                p['PolicyType'] == 'System' and p['PolicyName'] in [
                    'ReadOnlyAccess',
                    # We are going to ask for read-only access, but let's
                    # support admin accounts as well
                    'AdministratorAccess',
                ]
                for p in policies['Policies']['Policy']
            )
        except ServerException as exc:
            LOG.error(str(exc))
            if exc.get_error_code() == 'NoPermission':
                has_required_policy = False
            else:
                raise

        if not has_required_policy:
            raise InvalidParameterException(
                'The provided user ({}) does not have `ReadOnlyAccess` '
                'system permission, please assign it in Alibaba Cloud'.format(
                    user_name))

    def validate_credentials(self, org_id=None):
        try:
            identity_request = GetCallerIdentityRequest.GetCallerIdentityRequest()
            identity = self._send_request(identity_request)
            if identity['IdentityType'] != 'RAMUser':
                raise InvalidParameterException(
                    'Invalid credentials. Please provide programmatic '
                    'credentials from a RAM user')
            user_name = identity['Arn'].split('/')[-1]
            account_id = identity['AccountId']
            self._check_user_policy(user_name)
        except (ClientException, ServerException) as exc:
            message = getattr(exc, 'message', str(exc))
            raise InvalidParameterException(
                'Error from Alibaba Cloud: {}'.format(message))
        return {'account_id': account_id,
                'warnings': []}

    def volume_discovery_calls(self):
        return [(self._discover_region_volumes, (r,))
                for r in self._list_region_details()]

    def instance_discovery_calls(self):
        return [(self._discover_region_instances, (r,))
                for r in self._list_region_details()]

    def snapshot_chain_discovery_calls(self):
        return [(self._discover_region_snapshot_chains, (r,))
                for r in self._list_region_details()]

    def rds_instance_discovery_calls(self):
        excluded_regions = ['cn-wuhan-lr']
        # rds instances discover in this regions raises error for some reasons
        return [(self._discover_region_rds_instances, (r,))
                for r in self._list_region_details()
                if r['RegionId'] not in excluded_regions]

    def ip_address_discovery_calls(self):
        return [(self._discover_ip_addresses, (r,))
                for r in self._list_region_details()]

    def image_discovery_calls(self):
        return [(self._discover_region_images, (r,))
                for r in self._list_region_details()]

    def snapshot_discovery_calls(self):
        # There is no per-snapshot billing import yet, so let's skip discover
        return []

    def bucket_discovery_calls(self):
        # There is no per-bucket billing import yet, so let's skip discover
        return []

    def pod_discovery_calls(self):
        # Alibaba Cloud is not Kubernetes, there are no pods to discover
        return []

    def configure_report(self):
        now = datetime.utcnow()
        config_update = {}
        currency = self.DEFAULT_CURRENCY
        try:
            response = self.get_bill_overview(
                now, region_id=BILLING_REGION_ID)
            config_update['region_id'] = BILLING_REGION_ID
        except ServerException as exc:
            if exc.http_status == 400 and 'the API domain regionId' in exc.message:
                cn_region = 'cn-hangzhou'
                response = self.get_bill_overview(
                    now, region_id=cn_region)
                config_update['region_id'] = cn_region
            else:
                raise exc
        items = response.get('Data', {}).get('Items', {}).get('Item', [])
        if items:
            currency = items[0]['Currency']
        if currency != self._currency:
            raise CloudSettingNotSupported(
                "Account currency '%s' doesn’t match organization"
                " currency '%s'" % (currency, self._currency))
        return {
            'config_updates': config_update,
            'warnings': []
        }

    def _get_coordinates_map(self):
        # region Hard-coded coordinates map
        return {
            'cn-qingdao': {
                'name': 'China (Qingdao)',
                'longitude': 120.2244126, 'latitude': 36.1359886},
            'cn-beijing': {
                'name': 'China (Beijing)',
                'longitude': 116.2570342, 'latitude': 39.9387991},
            'cn-zhangjiakou': {
                'name': 'China (Zhangjiakou)',
                'longitude': 114.7628346, 'latitude': 40.78441},
            'cn-huhehaote': {
                'name': 'China (Hohhot)',
                'longitude': 111.577662, 'latitude': 40.8169826},
            'cn-wulanchabu': {
                'name': 'China (Ulanqab)',
                'longitude': 113.0597863, 'latitude': 41.0177905},
            'cn-hangzhou': {
                'name': 'China (Hangzhou)',
                'longitude': 120.0314647, 'latitude': 30.2613156},
            'cn-shanghai': {
                'name': 'China (Shanghai)',
                'longitude': 121.195889, 'latitude': 31.2240438},
            'cn-shenzhen': {
                'name': 'China (Shenzhen)',
                'longitude': 113.9134528, 'latitude': 22.5550993},
            'cn-heyuan': {
                'name': 'China (Heyuan)',
                'longitude': 114.6613867, 'latitude': 23.7292598},
            'cn-guangzhou': {
                'name': 'China (Guangzhou)',
                'longitude': 112.9469781, 'latitude': 23.1253491},
            'cn-chengdu': {
                'name': 'China (Chengdu)',
                'longitude': 103.9351208, 'latitude': 30.6584531},
            'cn-hongkong': {
                'name': 'China (Hong Kong)',
                'longitude': 113.987274, 'latitude': 22.3526629},
            'ap-northeast-1': {
                'name': 'Japan (Tokyo)',
                'longitude': 139.2080387, 'latitude': 35.5079383},
            'ap-southeast-1': {
                'name': 'Singapore',
                'longitude': 103.7038234, 'latitude': 1.3139961},
            'ap-southeast-2': {
                'name': 'Australia (Sydney)',
                'longitude': 150.7915495, 'latitude': -33.8481643},
            'ap-southeast-3': {
                'name': 'Malaysia (Kuala Lumpur)',
                'longitude': 101.6167781, 'latitude': 3.1385035},
            'ap-southeast-5': {
                'name': 'Indonesia (Jakarta)',
                'longitude': 106.7593066, 'latitude': -6.2297419},
            'ap-south-1': {
                'name': 'India (Mumbai)',
                'longitude': 72.74076, 'latitude': 19.0821976},
            'us-east-1': {
                'name': 'US (Virginia)',
                'longitude': -81.6690617, 'latitude': 37.9819836},
            'us-west-1': {
                'name': 'US (Silicon Valley)',
                'longitude': -122.181523, 'latitude': 37.4027205},
            'eu-west-1': {
                'name': 'UK (London)',
                'longitude': -0.2420222, 'latitude': 51.5285578},
            'me-east-1': {
                'name': 'UAE (Dubai)',
                'longitude': 55.087321, 'latitude': 25.0759564},
            'eu-central-1': {
                'name': 'Germany (Frankfurt)',
                'longitude': 8.5663531, 'latitude': 50.1211908},
            'cn-nanjing': {
                'name': 'China (Nanjing)',
                'longitude': 118.5973253, 'latitude': 32.0991916},
        }
        # endregion

    def get_regions_coordinates(self):
        coordinates_map = self._get_coordinates_map()
        try:
            for region_details in self._list_region_details():
                region_id = region_details['RegionId']
                if region_id not in coordinates_map:
                    coordinates_map[region_id] = {
                        'name': region_details['LocalName'],
                        'longitude': None,
                        'latitude': None,
                    }
        except Exception:
            LOG.info(
                'Cannot retrieve the list of regions for %s cloud account',
                self.cloud_account_id)
        return coordinates_map

    def get_billing_items(self, billing_date, granularity='DAILY',
                          region_id=None):
        request = DescribeInstanceBillRequest.DescribeInstanceBillRequest()
        request.set_BillingCycle(billing_date.strftime('%Y-%m'))
        request.set_BillingDate(billing_date.strftime('%Y-%m-%d'))
        request.set_Granularity(granularity)
        request.set_IsBillingItem(True)
        request.set_MaxResults(300)
        return self._send_marker_paged_request(
            request, paged_item='Items', nested_item='Data',
            region_id=region_id)

    def get_raw_usage(self, usage_table, data_type, start_time, end_time,
                      region_id=None):
        """
        Get raw usage data

        Log into Alibaba UI and then go to
        https://libra-intl.console.aliyun.com/oms/queryTables.json
        to see a list of available table names and data types (dimensions)

        Or, check "Expenses -> Usage Records" in Alibaba UI: it uses the
        aforementioned API URL
        """
        date_format = '%Y-%m-%dT%H:%M:%SZ'
        request = QueryUserOmsDataRequest.QueryUserOmsDataRequest()
        request.set_Table(usage_table)
        request.set_DataType(data_type)
        request.set_StartTime(start_time.strftime(date_format))
        request.set_EndTime(end_time.strftime(date_format))
        request.set_PageSize(200)
        return self._send_marker_paged_request(
            request, paged_item='OmsData', nested_item='Data',
            region_id=region_id)

    def get_metric(self, namespace, metric_name, instance_ids, region,
                   interval, start_date, end_date):
        """
        Get metric for instances

        :param metric_name: metric name
        :param instance_ids: a list of instance ids
        :param region: instance region ID or name
        :param interval: time interval in seconds
        :param start_date: metric start datetime date
        :param end_date: metric end datetime date
        :return: dict
        """
        date_format = '%Y-%m-%dT%H:%M:%SZ'
        request = DescribeMetricListRequest.DescribeMetricListRequest()
        request.set_MetricName(metric_name)
        request.set_Namespace(namespace)
        request.set_Dimensions([{'instanceId': x} for x in instance_ids])
        request.set_Period(interval)
        request.set_StartTime(start_date.strftime(date_format))
        request.set_EndTime(end_date.strftime(date_format))
        return self._send_marker_paged_request(
            request, 'Datapoints', region_id=self._find_region(region))

    def _get_product_list(self):
        """
        Get Alibaba product list. This method is not very useful by itself, but
        you can call it to see which parameters can go to `_get_pricing_module`
        and `_get_pay_as_you_go_prices`.

        :return: a generator with product codes and types
        """
        request = QueryProductListRequest.QueryProductListRequest()
        request.set_PageSize(300)
        request.set_QueryTotalCount(True)
        return self._send_paged_request(
            request, paged_item='Product', nested_item='Data')

    def _get_pricing_module(self, product_code, product_type=None,
                            subscription_type='PayAsYouGo'):
        """
        Get Alibaba pricing module descriptions. This method is not very useful
        by itself, but you can call it to see which parameters can go to
        `_get_pay_as_you_go_prices`

        :param product_code: product code, call `_get_product_list` to see them
        :param product_type: product type, call `_get_product_list` to see
            them. For some products, setting product type is required to get
            any result, for others it is optional.
        :param subscription_type: subscription type, PayAsYouGo or Subscription
        :return: dict with some stuff. It contains `AttributeList` (allowed
            values for parameters) and `ModuleList` (which parameters go to
            which pricing module).
        """
        request = DescribePricingModuleRequest.DescribePricingModuleRequest()
        request.set_ProductCode(product_code)
        request.set_SubscriptionType(subscription_type)
        if product_type:
            request.set_ProductType(product_type)
        return self._send_request(request)

    def _get_pay_as_you_go_prices(self, product_code, region, module_list,
                                  product_type=None):
        """
        Get Pay-As-You-Go prices
        API doc page: https://www.alibabacloud.com/help/doc-detail/91486.htm

        :param product_code: product code, call `_get_product_list` to see them
        :param region: region ID or name
        :param module_list: list with pricing module dictionaries, call
           `_get_pricing_module` to check which field values should go there.
           Alibaba has also had a page with examples of pricing modules, but
           now it is gone. Fortunately, it is still saved by Internet Archive:
           https://web.archive.org/web/20200811191532/https://www.alibabacloud.com/help/doc-detail/140572.htm
           Note that Internet Archive may tell that it "has not archived that
           URL" when you click on links. But it has actually archived them,
           just remove the`?spm=...` part from link URLs.
        :param product_type: product type, call `_get_product_list` to see
            them. For some products, setting product type is required to get
            any result, for others it is optional.
        :return: a generator with prices for every pricing module
        """
        def send_prices_request(module_lists):
            request = GetPayAsYouGoPriceRequest.GetPayAsYouGoPriceRequest()
            if product_type:
                request.set_ProductType(product_type)
            request.set_ProductCode(product_code)
            request.set_SubscriptionType('PayAsYouGo')
            request.set_Region(region_id)
            # Warning: `set_ModuleLists` does not overwrite old values properly
            # when it is called for second time. That's why a new request
            # object is constructed on every function call.
            request.set_ModuleLists(module_lists)
            response = self._send_request(request)
            try:
                return response['Data']['ModuleDetails']['ModuleDetail']
            except KeyError:
                pricing_not_found_code = 'PRICE.PRICING_PLAN_RESULT_NOT_FOUND'
                if response.get('Message') == pricing_not_found_code:
                    raise PricingNotFoundException('Pricing not found')
                else:
                    raise ValueError('Unexpected response format: {}'.format(
                        response))

        # A single API call can return up to 50 results, but let's reduce it to
        # avoid making too many calls when bulk fails.
        page_size = 20
        region_id = self._find_region(region)
        for i in range(0, len(module_list), page_size):
            module_chunk = module_list[i:i + page_size]
            try:
                for item in send_prices_request(module_chunk):
                    yield item
            except PricingNotFoundException:
                if len(module_chunk) > 1:
                    LOG.warning(
                        'Price for one of pricing modules was not found! '
                        'Resorting to individual requests instead of bulk')
                    for module in module_chunk:
                        try:
                            yield send_prices_request([module])[0]
                        except PricingNotFoundException:
                            LOG.warning('Price for module %s is not found, '
                                        'will return None', module)
                            yield None
                else:
                    LOG.warning('Price for module %s is not found, '
                                'will return None', module_chunk[0])
                    yield None

    def _get_subscription_prices(self, product_code, region, module_list,
                                 product_type=None, quantity=1, is_new=True):
        """
        Get Subscription prices
        API doc page: https://www.alibabacloud.com/help/doc-detail/91481.htm

        :param product_code: product code, call `_get_product_list` to see them
        :param region: region ID or name
        :param module_list: list with pricing module dictionaries, call
           `_get_pricing_module` to check which field values should go there.
           Alibaba has also had a page with examples of pricing modules, but
           now it is gone. Fortunately, it is still saved by Internet Archive:
           https://web.archive.org/web/20200811191532/https://www.alibabacloud.com/help/doc-detail/140572.htm
           Note that Internet Archive may tell that it "has not archived that
           URL" when you click on links. But it has actually archived them,
           just remove the`?spm=...` part from link URLs.
        :param product_type: product type, call `_get_product_list` to see
            them. For some products, setting product type is required to get
            any result, for others it is optional.
        :param quantity: months count for which price is requesting
        :param is_new: look for prices for new Pay-As-You-Go products or for
            upgrade of existing
        :return: a generator with prices for every pricing module
        """
        page_size = 50  # Single API call returns up to 50 results
        region_id = self._find_region(region)
        for i in range(0, len(module_list), page_size):
            request = GetSubscriptionPriceRequest.GetSubscriptionPriceRequest()
            if product_type:
                request.set_ProductType(product_type)
            request.set_ProductCode(product_code)
            request.set_SubscriptionType('Subscription')
            request.set_Region(region_id)
            request.set_ServicePeriodUnit('Month')
            request.set_ServicePeriodQuantity(quantity)
            order_type = 'NewOrder'
            if not is_new:
                order_type = 'Upgrade'
            request.set_OrderType(order_type)

            # Warning: `set_ModuleLists` does not overwrite old values properly
            # when it is called for second time. That's why a new request
            # object is constructed on each iteration.
            request.set_ModuleLists(module_list[i:i + page_size])
            response = self._send_request(request)
            try:
                for item in response['Data']['ModuleDetails']['ModuleDetail']:
                    yield item
            except KeyError:
                raise ValueError('Unexpected response format: {}'.format(
                    response))

    def get_flavor_prices(self, flavor_ids, region, io_optimized=False,
                          os_type='linux', billing_method='pay_as_you_go',
                          quantity=1, price_only=True):
        module_list = []
        for flavor_id in flavor_ids:
            config = {
                'InstanceType': flavor_id,
                'IoOptimized': 'optimized' if io_optimized else 'none',
                'ImageOs': os_type,
            }
            module = {
                'ModuleCode': 'InstanceType',
                'PriceType': 'Hour',
                'Config': ','.join(f'{k}:{v}' for k, v in config.items())
            }
            module_list.append(module)
        if billing_method == 'pay_as_you_go':
            response = self._get_pay_as_you_go_prices(
                product_code='ecs', region=region, module_list=module_list)
        elif billing_method == 'subscription':
            response = self._get_subscription_prices(
                product_code='ecs', region=region, module_list=module_list,
                quantity=quantity)
        else:
            raise ValueError('Incorrect billing_method %s' % billing_method)
        result = {}
        for i, item in enumerate(response):
            if item is not None:  # Skip flavors with no prices found
                if price_only:
                    result[flavor_ids[i]] = item['CostAfterDiscount']
                else:
                    item['billing_method'] = billing_method
                    result[flavor_ids[i]] = item
        return result

    def get_all_flavors(self, region, family=None, flavor_ids=None):
        request = DescribeInstanceTypesRequest.DescribeInstanceTypesRequest()
        if family:
            request.set_InstanceTypeFamily(family)
        if flavor_ids:
            request.set_InstanceTypess(flavor_ids)  # Yes, two "s", not my typo
        response = self._send_request(
            request, region_id=self._find_region(region))
        try:
            return {x['InstanceTypeId']: x for x in response[
                'InstanceTypes']['InstanceType']}
        except KeyError:
            raise ValueError('Unexpected response format: {}'.format(
                response))

    def get_all_families(self, region):
        request_family = (DescribeInstanceTypeFamiliesRequest
                          .DescribeInstanceTypeFamiliesRequest())
        region_id = self._find_region(region)
        response_family = self._send_request(
            request_family, region_id=region_id)
        family_map = {}
        for instance_type_family in response_family['InstanceTypeFamilies'][
                'InstanceTypeFamily']:
            family_id = instance_type_family['InstanceTypeFamilyId']
            generation = instance_type_family['Generation']
            family_map[family_id] = generation
        return family_map

    def get_available_flavors(self, region):
        request = (DescribeAvailableResourceRequest
                   .DescribeAvailableResourceRequest())
        request.set_DestinationResource('InstanceType')
        request.set_InstanceChargeType('PostPaid')
        response = self._send_request(
            request, region_id=self._find_region(region))
        flavors = set()
        for zone in response['AvailableZones']['AvailableZone']:
            for res in zone['AvailableResources']['AvailableResource']:
                for info in res['SupportedResources']['SupportedResource']:
                    flavors.add(info['Value'])
        return sorted(flavors)

    def get_all_rds_flavors(self, region, commodity_code='bards_intl',
                            order_type='BUY'):
        """
        Query RDS instance flavors and prices.
        See https://www.alibabacloud.com/help/doc-detail/258230.htm for details.

        :param region: region name or ID
        :param commodity_code: commodity code of the instances
        :return: dict with flavor IDs as keys and flavor info dicts as values.
            Note that prices (ReferencePrice) are strings with cents and CPU
            counts (Cpu) are strings that may contain trailing spaces.
        """

        class ListClassesRequest(RpcRequest):
            # ListClasses is a new API that is not available in the current SDK
            # TODO: remove this and use class from SDK once it's available
            def __init__(self):
                RpcRequest.__init__(self, 'Rds', '2014-08-15',
                                    'ListClasses', 'rds')
                self.set_method('POST')
                if hasattr(self, "endpoint_map"):
                    setattr(self, "endpoint_map",
                            endpoint_data.getEndpointMap())
                if hasattr(self, "endpoint_regional"):
                    setattr(self, "endpoint_regional",
                            endpoint_data.getEndpointRegional())

            def set_CommodityCode(self, CommodityCode):
                self.add_query_param('CommodityCode', CommodityCode)

            def set_OrderType(self, OrderType):
                self.add_query_param('OrderType', OrderType)

        request = ListClassesRequest()
        request.set_CommodityCode(commodity_code)
        request.set_OrderType(order_type)
        response = self._send_request(
            request, region_id=self._find_region(region))
        try:
            return {x['ClassCode']: x for x in response['Items']}
        except KeyError:
            raise ValueError('Unexpected response format: {}'.format(
                response))

    def get_available_rds_flavors(self, region, zone_id, category, engine,
                                  engine_version, storage_type):
        request = (DescribeAvailableClassesRequest
                   .DescribeAvailableClassesRequest())
        request.set_ZoneId(zone_id)
        request.set_Engine(engine)
        request.set_EngineVersion(engine_version)
        request.set_DBInstanceStorageType(storage_type)
        request.set_Category(category)
        try:
            response = self._send_request(
                request, region_id=self._find_region(region))
            return sorted(x['DBInstanceClass']
                          for x in response['DBInstanceClasses'])
        except ServerException as exc:
            if exc.error_code == 'InvalidCondition.NotFound':
                return []
            else:
                raise

    def get_bill_overview(self, billing_date, region_id=None):
        request = QueryBillOverviewRequest.QueryBillOverviewRequest()
        request.set_BillingCycle(billing_date.strftime('%Y-%m'))
        return self._send_request(request, region_id=region_id)

    def get_round_down_discount(self, billing_date, region_id=None):
        service_rdd_map = {}
        response = self.get_bill_overview(billing_date, region_id=region_id)
        try:
            for i in response['Data']['Items']['Item']:
                item_resource_id = '%s RDD' % i['ProductName']
                if not service_rdd_map.get(item_resource_id):
                    service_rdd_map[item_resource_id] = {
                        **i, 'resource_id': item_resource_id, 'cost': 0}
                service_rdd_map[item_resource_id]['cost'] += i[
                    'RoundDownDiscount']
            return service_rdd_map
        except KeyError:
            raise ValueError('Unexpected response format: {}'.format(response))

    def configure_last_import_modified_at(self):
        pass

    def set_currency(self, currency):
        self._currency = currency

    def start_instance(self, instance_ids, region_id):
        request = StartInstancesRequest.StartInstancesRequest()
        request.set_InstanceIds(instance_ids)
        try:
            return self._send_request(
                request, region_id=self._find_region(region_id))
        except ServerException as exc:
            if 'InvalidInstanceId' in exc.error_code:
                raise ResourceNotFound(str(exc))
            elif 'IncorrectInstanceStatus' in exc.error_code:
                raise InvalidResourceStateException(str(exc))
            else:
                raise

    def stop_instance(self, instance_ids, region_id):
        request = StopInstancesRequest.StopInstancesRequest()
        request.set_InstanceIds(instance_ids)
        try:
            return self._send_request(
                request, region_id=self._find_region(region_id))
        except ServerException as exc:
            if 'InvalidInstanceId' in exc.error_code:
                raise ResourceNotFound(str(exc))
            elif 'IncorrectInstanceStatus' in exc.error_code:
                raise InvalidResourceStateException(str(exc))
            else:
                raise
