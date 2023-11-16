import grpc
import json
import jwt
import logging
import os
import re
import requests
import time
import yandexcloud
import yandex.cloud.mdb.mysql.v1.cluster_service_pb2 as mysql_cluster_service_pb2
import yandex.cloud.mdb.mongodb.v1.cluster_service_pb2 as mongodb_cluster_service_pb2
import yandex.cloud.mdb.clickhouse.v1.cluster_service_pb2 as clickhouse_cluster_service_pb2
import yandex.cloud.mdb.postgresql.v1.cluster_service_pb2 as postgresql_cluster_service_pb2
import yandex.cloud.mdb.mysql.v1.resource_preset_service_pb2 as mysql_resource_preset_pb2
import yandex.cloud.mdb.mongodb.v1.resource_preset_service_pb2 as mongodb_resource_preset_pb2
import yandex.cloud.mdb.clickhouse.v1.resource_preset_service_pb2 as clickhouse_resource_preset_pb2
import yandex.cloud.mdb.postgresql.v1.resource_preset_service_pb2 as postgresql_resource_preset_pb2
from botocore.exceptions import ClientError, ParamValidationError, EndpointConnectionError
from tools.cloud_adapter.clouds.base import S3CloudMixin
from tools.cloud_adapter.exceptions import (
    ReportFilesNotFoundException, CloudConnectionError,
    ReportConfigurationException, BucketNotFoundException,
    BucketNameValidationError, BucketPrefixValidationError, S3ConnectionError)
from tools.cloud_adapter.model import (
    BucketResource,
    VolumeResource,
    ImageResource,
    InstanceResource,
    SnapshotResource,
    IpAddressResource,
    RdsInstanceResource
)
from tools.cloud_adapter.utils import CloudParameter
from google.protobuf.json_format import MessageToDict
from yandex.cloud.billing.v1.sku_service_pb2 import ListSkusRequest
from yandex.cloud.billing.v1.sku_service_pb2_grpc import SkuServiceStub
from yandex.cloud.compute.v1.disk_service_pb2 import ListDisksRequest
from yandex.cloud.compute.v1.disk_service_pb2_grpc import DiskServiceStub
from yandex.cloud.compute.v1.image_service_pb2 import ListImagesRequest
from yandex.cloud.compute.v1.image_service_pb2_grpc import ImageServiceStub
from yandex.cloud.compute.v1.instance_service_pb2 import ListInstancesRequest
from yandex.cloud.compute.v1.instance_service_pb2_grpc import InstanceServiceStub
from yandex.cloud.compute.v1.snapshot_service_pb2 import ListSnapshotsRequest
from yandex.cloud.compute.v1.snapshot_service_pb2_grpc import SnapshotServiceStub
from yandex.cloud.endpoint.api_endpoint_service_pb2 import ListApiEndpointsRequest
from yandex.cloud.endpoint.api_endpoint_service_pb2_grpc import ApiEndpointServiceStub
from yandex.cloud.iam.v1.iam_token_service_pb2 import CreateIamTokenRequest
from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub
from yandex.cloud.iam.v1.service_account_service_pb2 import ListServiceAccountsRequest
from yandex.cloud.iam.v1.service_account_service_pb2_grpc import ServiceAccountServiceStub
from yandex.cloud.resourcemanager.v1.cloud_service_pb2 import ListCloudsRequest
from yandex.cloud.resourcemanager.v1.cloud_service_pb2_grpc import CloudServiceStub
from yandex.cloud.resourcemanager.v1.folder_service_pb2 import ListFoldersRequest
from yandex.cloud.resourcemanager.v1.folder_service_pb2_grpc import FolderServiceStub
from yandex.cloud.vpc.v1.address_service_pb2 import ListAddressesRequest
from yandex.cloud.vpc.v1.address_service_pb2_grpc import AddressServiceStub
from yandex.cloud.vpc.v1.security_group_service_pb2 import ListSecurityGroupsRequest
from yandex.cloud.vpc.v1.security_group_service_pb2_grpc import SecurityGroupServiceStub
from yandex.cloud.vpc.v1.network_service_pb2 import ListNetworksRequest
from yandex.cloud.vpc.v1.network_service_pb2_grpc import NetworkServiceStub
from yandex.cloud.vpc.v1.subnet_service_pb2 import ListSubnetsRequest
from yandex.cloud.vpc.v1.subnet_service_pb2_grpc import SubnetServiceStub

from yandex.cloud.mdb.mysql.v1.cluster_service_pb2_grpc import ClusterServiceStub as MySQLClStub
from yandex.cloud.mdb.clickhouse.v1.cluster_service_pb2_grpc import ClusterServiceStub as CHClStub
from yandex.cloud.mdb.mongodb.v1.cluster_service_pb2_grpc import ClusterServiceStub as MongoClStub
from yandex.cloud.mdb.postgresql.v1.cluster_service_pb2_grpc import ClusterServiceStub as PostgreClStub
from yandex.cloud.mdb.mysql.v1.resource_preset_service_pb2_grpc import ResourcePresetServiceStub as MySQLRPStub
from yandex.cloud.mdb.clickhouse.v1.resource_preset_service_pb2_grpc import ResourcePresetServiceStub as CHRPStub
from yandex.cloud.mdb.mongodb.v1.resource_preset_service_pb2_grpc import ResourcePresetServiceStub as MongoRPStub
from yandex.cloud.mdb.postgresql.v1.resource_preset_service_pb2_grpc import ResourcePresetServiceStub as PostgreRPStub


LOG = logging.getLogger(__name__)
MSEC_IN_SEC = 1000
MSEC_IN_DAY = 24 * 60 * 60 * 1000

CLOUD_LINK_PATTERN = 'https://{0}/folders/{1}/{2}/{3}/{4}/overview'
BUCKET_ACCEPTED_PERMISSIONS = ['PERMISSION_FULL_CONTROL', 'PERMISSION_READ',
                               'PERMISSION_WRITE', 'PERMISSION_READ_ACP',
                               'PERMISSION_WRITE_ACP']
BUCKET_ACCEPTED_GRANT_TYPES = ['GRANT_TYPE_ALL_AUTHENTICATED_USERS',
                               'GRANT_TYPE_ALL_USERS']
DEFAULT_BUCKET_PREFIX = ''
RETRYABLE_CODES = [grpc.StatusCode.UNAVAILABLE]

# according to https://nebius.com/il/docs/compute/concepts/performance-levels
PLATFORMS = {
    'standard-v3': {
        'name': 'Intel Ice Lake',
        'core_fraction': {
            20: [{
                'cpu': [2, 4],
                'ram_per_core': [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]
            }],
            50: [{
                'cpu': [2, 4],
                'ram_per_core': [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]
            }],
            100: [{
                'cpu': [2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 36, 40],
                'ram_per_core': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                                 14, 15, 16]
            }, {
                'cpu': [44],
                'ram_per_core': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
            }, {
                'cpu': [48],
                'ram_per_core': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
            }, {
                'cpu': [52],
                'ram_per_core': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            }, {
                'cpu': [56],
                'ram_per_core': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            }, {
                'cpu': [60, 64],
                'ram_per_core': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            }, {
                'cpu': [68],
                'ram_per_core': [1, 2, 3, 4, 5, 6, 7, 8, 9]
            }, {
                'cpu': [72, 76, 80],
                'ram_per_core': [1, 2, 3, 4, 5, 6, 7, 8]
            }, {
                'cpu': [84, 88],
                'ram_per_core': [1, 2, 3, 4, 5, 6, 7]
            }, {
                'cpu': [92, 96],
                'ram_per_core': [1, 2, 3, 4, 5, 6]
            }]
        }
    },
    'gpu-standard-v3': {
        'name': 'AMD EPYC with NVIDIA Ampere A100'
    },
}
# according to https://nebius.com/il/docs/managed-clickhouse/concepts/instance-types
RDS_PLATFORM_FAMILIES = {'Intel Ice Lake': ['b3', 'c3', 'm3', 's3']}
REGIONS_COORDINATES = {
        # Lod
        'il1-a': {'longitude': 34.8881, 'latitude': 31.9510},
        # Jerusalem
        'il1-b': {'longitude': 35.2137, 'latitude': 31.7683},
        # Tirat Carmel
        'il1-c': {'longitude': 34.9730, 'latitude': 32.7621},
        # Israel
        'il1': {'longitude': 34.8516, 'latitude': 31.0461}
    }


class RdsService(object):
    def __init__(self, sdk, service_type):
        self.sdk = sdk
        self.service_type = service_type
        self._cluster_service = None
        self._resource_preset_service = None

    @property
    def cluster_service(self):
        if not self._cluster_service:
            service_stub_map = {
                'mysql': MySQLClStub,
                'postgresql': PostgreClStub,
                'mongodb': MongoClStub,
                'clickhouse': CHClStub
            }
            self._cluster_service = self.sdk.client(
                service_stub_map[self.service_type])
        return self._cluster_service

    @property
    def resource_preset_service(self):
        if not self._resource_preset_service:
            service_stub_map = {
                'mysql': MySQLRPStub,
                'postgresql': PostgreRPStub,
                'mongodb': MongoRPStub,
                'clickhouse': CHRPStub
            }
            self._resource_preset_service = self.sdk.client(
                service_stub_map[self.service_type])
        return self._resource_preset_service

    def resource_preset_request(self, **kwargs):
        resource_preset_r_map = {
            'mysql': mysql_resource_preset_pb2,
            'postgresql': postgresql_resource_preset_pb2,
            'mongodb': mongodb_resource_preset_pb2,
            'clickhouse': clickhouse_resource_preset_pb2
        }
        return resource_preset_r_map[
            self.service_type].ListResourcePresetsRequest(**kwargs)

    def clusters_list_request(self, **kwargs):
        resource_preset_r_map = {
            'mysql': mysql_cluster_service_pb2,
            'postgresql': postgresql_cluster_service_pb2,
            'mongodb': mongodb_cluster_service_pb2,
            'clickhouse': clickhouse_cluster_service_pb2
        }
        return resource_preset_r_map[
            self.service_type].ListClustersRequest(**kwargs)

    def cluster_hosts_list_request(self, **kwargs):
        resource_preset_r_map = {
            'mysql': mysql_cluster_service_pb2,
            'postgresql': postgresql_cluster_service_pb2,
            'mongodb': mongodb_cluster_service_pb2,
            'clickhouse': clickhouse_cluster_service_pb2
        }
        return resource_preset_r_map[
            self.service_type].ListClusterHostsRequest(**kwargs)


class Nebius(S3CloudMixin):
    BILLING_CREDS = [
        CloudParameter(name='service_account_id', type=str, required=True),
        CloudParameter(name='key_id', type=str, required=True),
        CloudParameter(name='private_key', type=str, required=True,
                       check_len=False, protected=True),
        CloudParameter(name='bucket_name', type=str, required=True),
        CloudParameter(name='bucket_prefix', type=str, required=True),
        CloudParameter(name='access_key_id', type=str, required=True),
        CloudParameter(name='secret_access_key', type=str, required=True,
                       protected=True),
        CloudParameter(name='cloud_name', type=str, required=True),

        CloudParameter(name='endpoint', type=str, required=False),
        CloudParameter(name='region_name', type=str, required=False),
        CloudParameter(name='s3_endpoint', type=str, required=False),
        CloudParameter(name='console_endpoint', type=str, required=False),
        CloudParameter(name='regions_coordinates', type=dict, required=False),
        CloudParameter(name='platforms', type=dict, required=False),
        CloudParameter(name='rds_platforms', type=dict, required=False),
    ]
    CONSOLE_ENDPOINT = 'console.il.nebius.com'
    DEFAULT_S3_REGION_NAME = 'il1'
    MAIN_ENDPOINT = 'api.il.nebius.cloud'
    MONITORING_ENDPOINT = 'monitoring.api.il.nebius.cloud'
    S3_ENDPOINT = 'https://storage.il.nebius.cloud'

    def __init__(self, cloud_config, *args, **kwargs):
        super().__init__(cloud_config, *args, **kwargs)
        self._sdk = None
        self._token = None

    @property
    def endpoint(self):
        return self.config.get('endpoint', self.MAIN_ENDPOINT)

    @property
    def service_account_id(self):
        return self.config.get('service_account_id')

    @property
    def private_key(self):
        return self.config.get('private_key')

    @property
    def key_id(self):
        return self.config.get('key_id')

    @property
    def sdk(self):
        if self._sdk is None:
            interceptor = yandexcloud.RetryInterceptor(
                max_retry_count=5, retriable_codes=RETRYABLE_CODES)
            sa_key = {
                'id': self.key_id,
                'private_key': self.private_key,
                'service_account_id': self.service_account_id
            }
            self._sdk = yandexcloud.SDK(interceptor=interceptor,
                                        service_account_key=sa_key,
                                        endpoint=self.endpoint)
        return self._sdk

    @property
    def cloud_account_id(self):
        return self.config.get('cloud_account_id')

    @property
    def organization_id(self):
        return self.config.get('organization_id')

    @property
    def cloud_id(self):
        return self.config.get('account_id')

    @property
    def cloud_service(self):
        return self.sdk.client(CloudServiceStub)

    @property
    def folder_service(self):
        return self.sdk.client(FolderServiceStub)

    @property
    def disk_service(self):
        return self.sdk.client(DiskServiceStub)

    @property
    def instance_service(self):
        return self.sdk.client(InstanceServiceStub)

    @property
    def snapshot_service(self):
        return self.sdk.client(SnapshotServiceStub)

    @property
    def image_service(self):
        return self.sdk.client(ImageServiceStub)

    @property
    def ip_address_service(self):
        return self.sdk.client(AddressServiceStub)

    @property
    def sku_service(self):
        return self.sdk.client(SkuServiceStub)

    @property
    def sg_service(self):
        return self.sdk.client(SecurityGroupServiceStub)

    @property
    def subnet_service(self):
        return self.sdk.client(SubnetServiceStub)

    @property
    def network_service(self):
        return self.sdk.client(NetworkServiceStub)

    @property
    def iam_service(self):
        return self.sdk.client(IamTokenServiceStub)

    @property
    def service_acc_service(self):
        return self.sdk.client(ServiceAccountServiceStub)

    @property
    def endpoint_service(self):
        return self.sdk.client(ApiEndpointServiceStub)

    @property
    def service_endpoints(self):
        endpoints_map = {}
        request = ListApiEndpointsRequest()
        response = self.send_list_paged_request(
            self.endpoint_service.List, request, 'endpoints')
        for item in response:
            endpoints_map[item.id] = item.address
        return endpoints_map

    def discovery_calls_map(self):
        return {
            BucketResource: self.bucket_discovery_calls,
            VolumeResource: self.volume_discovery_calls,
            InstanceResource: self.instance_discovery_calls,
            SnapshotResource: self.snapshot_discovery_calls,
            IpAddressResource: self.ip_address_discovery_calls,
            ImageResource: self.image_discovery_calls,
            RdsInstanceResource: self.rds_instance_discovery_calls
        }

    def _wrap(self, action, method, *args, **kwargs):
        try:
            return method(*args, **kwargs)
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

    def send_list_paged_request(self, operation, request, data_field):
        results = []
        single_result = operation(request)
        if getattr(single_result, data_field):
            results.extend(getattr(single_result, data_field))
        if single_result.next_page_token:
            request.page_token = single_result.next_page_token
            results.extend(self.send_list_paged_request(
                operation, request, data_field))
        return results

    def _generate_cloud_link(self, resource_type, resource_value, folder_id,
                             cluster_value, category):
        cluster_query = '?section=hosts&hostName={}'.format(resource_value)
        cloud_link_map = {
            InstanceResource: CLOUD_LINK_PATTERN.format(
                self.config.get('console_endpoint', self.CONSOLE_ENDPOINT),
                folder_id, 'compute', 'instances', resource_value),
            VolumeResource: CLOUD_LINK_PATTERN.format(
                self.config.get('console_endpoint', self.CONSOLE_ENDPOINT),
                folder_id, 'compute', 'disks', resource_value),
            SnapshotResource: CLOUD_LINK_PATTERN.format(
                self.config.get('console_endpoint', self.CONSOLE_ENDPOINT),
                folder_id, 'compute', 'snapshots', resource_value),
            BucketResource: CLOUD_LINK_PATTERN.format(
                self.config.get('console_endpoint', self.CONSOLE_ENDPOINT),
                folder_id, 'storage', 'buckets', resource_value),
            IpAddressResource: CLOUD_LINK_PATTERN.format(
                self.config.get('console_endpoint', self.CONSOLE_ENDPOINT),
                folder_id, 'vpc', 'ipaddresses', resource_value),
            RdsInstanceResource: CLOUD_LINK_PATTERN.format(
                self.config.get('console_endpoint', self.CONSOLE_ENDPOINT),
                folder_id, 'managed-{}'.format(category), 'cluster',
                cluster_value) + cluster_query
        }
        return cloud_link_map.get(resource_type)

    def _set_cloud_link(self, resource_obj, folder_id=None, cluster_value=None,
                        category=None):
        resource_type = type(resource_obj)
        resource_obj.cloud_console_link = self._generate_cloud_link(
            resource_type, resource_obj.cloud_resource_id, folder_id,
            cluster_value, category)

    @property
    def folders(self):
        request = ListFoldersRequest(cloud_id=self.cloud_id)
        result = self.send_list_paged_request(
            self.folder_service.List, request, 'folders')
        return [r.id for r in result]

    @staticmethod
    def get_region_by_zone(zone_id):
        if zone_id:
            prefix_num = zone_id.rfind('-')
            if prefix_num != -1:
                return zone_id[:prefix_num]

    def bucket_discovery_calls(self):
        return [(self.discover_bucket_resources, (r,)) for r in self.folders]

    def discover_bucket_resources(self, folder_id):
        endpoint = self.service_endpoints.get('storage-api')
        base_url = f'https://{endpoint}/storage/v1/buckets'
        list_url = base_url + f'?folderId={folder_id}'
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(list_url, headers=headers)
        buckets = json.loads(response.content.decode())
        for bucket in buckets['buckets']:
            name = bucket['name']
            is_public_policy, is_public_acls = False, False
            detail_url = base_url + f'/{name}?view=VIEW_FULL'
            response = requests.get(detail_url, headers=headers)
            details = json.loads(response.content.decode())
            access_flags = details.get('anonymousAccessFlags', {})
            if any(access_flags.values()):
                is_public_acls = True
            acls = details.get('acl', {}).get('grants', [])
            for acl in acls:
                permission = acl.get('permission')
                grant_type = acl.get('grantType')
                is_public_acls = (permission in BUCKET_ACCEPTED_PERMISSIONS and
                                  grant_type in BUCKET_ACCEPTED_GRANT_TYPES)
                if is_public_acls:
                    break
            policies = details.get('policy', {}).get('Statement', [])
            for policy in policies:
                if (policy.get('Effect') == 'Allow' and
                        policy.get('Principal') == '*'):
                    is_public_policy = True
            resource = BucketResource(
                cloud_resource_id=name,
                cloud_account_id=self.cloud_account_id,
                organization_id=self.organization_id,
                name=name,
                is_public_acls=is_public_acls,
                is_public_policy=is_public_policy
            )
            self._set_cloud_link(resource, folder_id=folder_id)
            yield resource

    def volume_discovery_calls(self):
        return [(self.discover_volume_resources, (r,)) for r in
                self.folders]

    def discover_volume_resources(self, folder_id):
        request = ListDisksRequest(folder_id=folder_id, page_size=1000)
        result = self.send_list_paged_request(
            self.disk_service.List, request, 'disks')
        for item in result:
            resource = VolumeResource(
                cloud_resource_id=item.id,
                cloud_account_id=self.cloud_account_id,
                zone_id=item.zone_id,
                name=item.name,
                size=item.size,
                volume_type=item.type_id,
                organization_id=self.organization_id,
                tags=dict(item.labels),
                attached=(bool(item.instance_ids)),
                snapshot_id=item.source_snapshot_id,
                folder_id=item.folder_id,
                image_id=item.source_image_id,
                region=self.get_region_by_zone(item.zone_id)
            )
            self._set_cloud_link(resource, folder_id)
            yield resource

    def _discover_network_resources(self, folder_id):
        request = ListNetworksRequest(folder_id=folder_id)
        result = self.send_list_paged_request(
            self.network_service.List, request, 'networks')
        return [MessageToDict(x) for x in result]

    def _discover_subnet_resources(self, folder_id):
        request = ListSubnetsRequest(folder_id=folder_id)
        result = self.send_list_paged_request(
            self.subnet_service.List, request, 'subnets')
        return [MessageToDict(x) for x in result]

    def instance_discovery_calls(self):
        return [(self.discover_instance_resources, (r,)) for r in
                self.folders]

    def _raw_discover_instances(self, folder_id):
        request = ListInstancesRequest(folder_id=folder_id, page_size=1000)
        return self.send_list_paged_request(
            self.instance_service.List, request, 'instances')

    def discover_instance_resources(self, folder_id):
        networks = self._discover_network_resources(folder_id)
        network_id_name_map = {x['id']: x['name'] for x in networks}
        subnets = self._discover_subnet_resources(folder_id)
        subnet_network_id_map = {x['id']: x['networkId'] for x in subnets}
        for item in self._raw_discover_instances(folder_id):
            sgs = []
            for nic in item.network_interfaces:
                sgs.extend(nic.security_group_ids)
            subnet_id = item.network_interfaces[0].subnet_id
            network_id = subnet_network_id_map.get(subnet_id)
            network_name = network_id_name_map.get(network_id)
            resource = InstanceResource(
                cloud_resource_id=item.id,
                cloud_account_id=self.cloud_account_id,
                zone_id=item.zone_id,
                name=item.name,
                stopped_allocated=False,
                security_groups=sgs,
                organization_id=self.organization_id,
                tags=dict(item.labels),
                spotted=item.scheduling_policy.preemptible,
                cloud_created_at=item.created_at.seconds,
                cpu_count=item.resources.cores,
                folder_id=item.folder_id,
                platform_id=item.platform_id,
                platform_name=self.config['platforms'].get(
                    item.platform_id, {}).get('name'),
                cpu_fraction=item.resources.core_fraction,
                ram=item.resources.memory,
                vpc_id=network_id,
                vpc_name=network_name,
                region=self.get_region_by_zone(item.zone_id)
            )
            self._set_cloud_link(resource, folder_id)
            yield resource

    def snapshot_discovery_calls(self):
        return [(self.discover_snapshot_resources, (r,)) for r in
                self.folders]

    def discover_snapshot_resources(self, folder_id):
        request = ListSnapshotsRequest(folder_id=folder_id, page_size=1000)
        result = self.send_list_paged_request(
            self.snapshot_service.List, request, 'snapshots')
        for item in result:
            resource = SnapshotResource(
                    cloud_resource_id=item.id,
                    cloud_account_id=self.cloud_account_id,
                    organization_id=self.organization_id,
                    name=item.name,
                    size=int(item.storage_size),
                    description=item.description,
                    state=item.Status.Name(item.status),
                    tags=dict(item.labels),
                    volume_id=item.source_disk_id,
                    folder_id=item.folder_id
                )
            self._set_cloud_link(resource, folder_id)
            yield resource

    def image_discovery_calls(self):
        return [(self.discover_image_resources, (r,)) for r in
                self.folders]

    def discover_image_resources(self, folder_id):
        request = ListImagesRequest(folder_id=folder_id, page_size=1000)
        result = self.send_list_paged_request(
            self.image_service.List, request, 'images')
        for item in result:
            resource = ImageResource(
                cloud_resource_id=item.id,
                cloud_account_id=self.cloud_account_id,
                folder_id=item.folder_id,
                name=item.name,
                cloud_created_at=item.created_at.seconds,
                tags=dict(item.labels),
            )
            self._set_cloud_link(resource, folder_id)
            yield resource

    def _public_ip_to_instance_id_map(self, folder_id):
        result = {}
        for instance in self._raw_discover_instances(folder_id):
            for interface in instance.network_interfaces:
                if hasattr(interface.primary_v4_address,
                           'one_to_one_nat'):
                    address = interface.primary_v4_address.one_to_one_nat.address
                    result[address] = instance.id
        return result

    def ip_address_discovery_calls(self):
        return [(self.discover_ip_address_resources, (r,)) for r in
                self.folders]

    def discover_ip_address_resources(self, folder_id):
        request = ListAddressesRequest(folder_id=folder_id, page_size=1000)
        result = self.send_list_paged_request(
            self.ip_address_service.List, request, 'addresses')
        ip_instance_id_map = self._public_ip_to_instance_id_map(folder_id)
        for item in result:
            instance_id = ip_instance_id_map.get(
                item.external_ipv4_address.address)
            resource = IpAddressResource(
                cloud_account_id=self.cloud_account_id,
                organization_id=self.organization_id,
                cloud_resource_id=item.id,
                zone_id=item.external_ipv4_address.zone_id,
                available=not item.used,
                folder_id=item.folder_id,
                instance_id=instance_id,
                region=self.get_region_by_zone(
                    item.external_ipv4_address.zone_id)
            )
            self._set_cloud_link(resource, folder_id)
            yield resource

    def get_rds_flavors(self, service_name=None, rds_service_cls=None):
        if not rds_service_cls:
            rds_service_cls = RdsService(self.sdk, service_name)
        flavors_request = rds_service_cls.resource_preset_request()
        return self.send_list_paged_request(
            rds_service_cls.resource_preset_service.List, flavors_request,
            'resource_presets')

    def rds_instance_discovery_calls(self):
        return [(self.discover_rds_instance_resources, (r,)) for r in
                self.folders]

    def discover_rds_instance_resources(self, folder_id):
        supported_services = ['mysql', 'mongodb', 'clickhouse', 'postgresql']
        networks = self._discover_network_resources(folder_id)
        network_id_name_map = {x['id']: x['name'] for x in networks}
        subnets = self._discover_subnet_resources(folder_id)
        subnet_network_id_map = {x['id']: x['networkId'] for x in subnets}
        for service in supported_services:
            rds_service = RdsService(self.sdk, service)
            flavors = self.get_rds_flavors(rds_service_cls=rds_service)
            clusters_request = rds_service.clusters_list_request(
                folder_id=folder_id)
            clusters = self.send_list_paged_request(
                rds_service.cluster_service.List, clusters_request,
                'clusters')
            for cluster in clusters:
                rds_instances_request = rds_service.cluster_hosts_list_request(
                    cluster_id=cluster.id)
                rds_instances = self.send_list_paged_request(
                    rds_service.cluster_service.ListHosts,
                    rds_instances_request,
                    'hosts')
                for item in rds_instances:
                    flavor_id = item.resources.resource_preset_id
                    separator = '.' if '.' in flavor_id else '-'
                    flavor_family = flavor_id.split(separator)
                    flavor_info = [x for x in flavors if x.id == flavor_id]
                    platform_name = None
                    if flavor_family:
                        for name, values in self.config['rds_platforms'].items():
                            if flavor_family[0] in values:
                                platform_name = name
                    network_id = subnet_network_id_map.get(item.subnet_id)
                    network_name = network_id_name_map.get(network_id)

                    # services property may be empty if cluster is stopped, set
                    # rds service name as category
                    category = rds_service.service_type.upper()
                    if item.services:
                        category = item.services[0].Type.Name(
                            item.services[0].type)

                    resource = RdsInstanceResource(
                        cloud_resource_id=item.name,
                        cloud_account_id=self.cloud_account_id,
                        folder_id=folder_id,
                        name=item.name,
                        flavor=flavor_id,
                        zone_id=item.zone_id,
                        storage_type=item.resources.disk_type_id,
                        category=category,
                        source_cluster_id=item.cluster_id,
                        platform_name=platform_name,
                        vpc_id=network_id,
                        vpc_name=network_name,
                        region=self.get_region_by_zone(item.zone_id)
                    )
                    if flavor_info:
                        resource.cpu_count = flavor_info[0].cores
                        resource.ram = flavor_info[0].memory
                    self._set_cloud_link(
                        resource, folder_id, category=resource.category,
                        cluster_value=resource.source_cluster_id)
                    yield resource

    def validate_credentials(self, org_id=None):
        request = ListCloudsRequest(
            filter='name="%s"' % self.config['cloud_name'])
        try:
            clouds = getattr(self.cloud_service.List(request), 'clouds')
        except grpc.RpcError as exc:
            raise CloudConnectionError(
                'Cloud connection error: %s' % exc.details())
        except RuntimeError as exc:
            raise CloudConnectionError(
                'Cloud connection error: %s' % str(exc))
        if clouds:
            account_id = clouds[0].id
        else:
            raise CloudConnectionError(
                'Cloud with name %s not found. Please check cloud name or '
                'service account permissions' % self.config['cloud_name'])
        if 'platforms' not in self.config:
            self.config['platforms'] = PLATFORMS
        if 'rds_platforms' not in self.config:
            self.config['rds_platforms'] = RDS_PLATFORM_FAMILIES
        return {'account_id': account_id, 'warnings': []}

    def check_bucket_exists(self, bucket_name):
        try:
            self.s3.get_bucket_location(Bucket=bucket_name)
        except EndpointConnectionError as exc:
            raise S3ConnectionError(str(exc))
        except self.s3.exceptions.NoSuchBucket:
            raise BucketNotFoundException(
                'Bucket {} not found'.format(bucket_name))
        except ParamValidationError:
            raise BucketNameValidationError(
                'Bucket name "{}" has incorrect format'.format(bucket_name))

    def check_prefix_report_name(self, prefix):
        if prefix and not self.is_valid_s3_object_key(prefix):
            raise BucketPrefixValidationError('Bucket prefix "{}" has incorrect'
                                              ' format'.format(prefix))

    def configure_report(self):
        for param in ['bucket_name', 'bucket_prefix']:
            if self.config.get(param) is None:
                raise ReportConfigurationException(
                    '{} is required'.format(param))
        bucket_name = self.config.get('bucket_name')
        prefix = self.config.get('bucket_prefix')
        if not self.config.get('s3_endpoint'):
            endpoint = self.service_endpoints.get('storage')
            self.config['s3_endpoint'] = (
                'https://' + endpoint if endpoint else self.S3_ENDPOINT)
        try:
            self._wrap(
                'check bucket {} existence'.format(bucket_name),
                self.check_bucket_exists, bucket_name)
        except BucketNotFoundException:
            raise ReportConfigurationException(
                'Bucket {} not found'.format(bucket_name))
        except CloudConnectionError as ex:
            raise S3ConnectionError(str(ex))

        self.check_prefix_report_name(prefix)
        try:
            reports = self._wrap(
                'check {}/{} access'.format(bucket_name, prefix),
                self.get_report_files)
            if reports:
                report = reports.popitem()[1][0]
                with open(os.devnull, 'wb') as f:
                    self._wrap('perform test {} download'.format(report),
                               self.download_report_file, report['Key'], f)
        except ReportFilesNotFoundException:
            LOG.warning('Report files not found')

    @staticmethod
    def find_csv_reports(s3_objects, prefix, reports):
        report_regex_fmt = '^{0}/[0-9]{{8}}.csv$'
        try:
            report_regex = re.compile(
                report_regex_fmt.format(re.escape(prefix)))
            for report in [f for f in s3_objects['Contents']
                           if re.match(report_regex, f['Key'])]:
                group = re.search(r'[0-9]{6}', report['Key']).group(0)
                if group not in reports:
                    reports[group] = []
                reports[group].append(report)
        except KeyError:
            pass

    def download_report_file(self, report_name, file_obj):
        self.s3.download_fileobj(
            self.config['bucket_name'], report_name, file_obj)

    def get_report_files(self):
        bucket_name = self.config['bucket_name']
        prefix = self.config.get('bucket_prefix', DEFAULT_BUCKET_PREFIX)
        if prefix.endswith('/'):
            prefix = prefix[:-1]
        reports = {}
        params = {
            'Bucket': bucket_name,
            'Prefix': prefix
        }
        while True:
            resp = self.s3.list_objects_v2(**params)
            self.find_csv_reports(resp, prefix, reports)
            if not resp['IsTruncated']:
                break
            params['ContinuationToken'] = resp['NextContinuationToken']
        if not reports:
            raise ReportFilesNotFoundException(
                'Report files for report {} not found in bucket {}'.format(
                    prefix, bucket_name))
        return reports

    @property
    def token(self):
        if not self._token:
            token_url = 'https://{}/iam/v1/tokens'.format(
                self.service_endpoints['iam'].split(':')[0])
            now = int(time.time())
            payload = {
                'aud': token_url,
                'iss': self.service_account_id,
                'iat': now,
                'exp': now + 360}
            encoded_token = jwt.encode(
                payload,
                self.private_key,
                algorithm='PS256',
                headers={'kid': self.key_id})
            request = CreateIamTokenRequest(jwt=encoded_token)
            result = self.iam_service.Create(request)
            self._token = result.iam_token
        return self._token

    def _get_metrics(self, start_date, end_date, query, folder_id,
                     downsampling):
        url = 'https://{0}/monitoring/v2/data/read?folderId={1}'.format(
            self.service_endpoints.get('monitoring', self.MONITORING_ENDPOINT),
            folder_id)
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        body = {
            "query": query,
            "fromTime": start_date_str,
            "toTime": end_date_str,
            "downsampling": downsampling
        }
        headers = {'Authorization': f'Bearer {self.token}'}
        r = requests.post(url, json=body, headers=headers)
        return json.loads(r.content.decode())

    def get_service_account_metrics(self, service_accounts_ids, start_date,
                                    end_date, folder_id):
        downsampling = {
                "gridInterval": str(MSEC_IN_DAY),
                "gridAggregation": "MAX",
                "gapFilling": "NONE"
            }
        resource_ids_str = '|'.join(service_accounts_ids)
        query = '\"service_account.*\"{service=\"iam\", ' \
                'service_account=\"%s\"}' % resource_ids_str
        return self._get_metrics(start_date, end_date, query, folder_id,
                                 downsampling)

    def get_metric(self, metric_name, instance_ids, start_date, end_date,
                   interval=0, folder_id=None):
        """
        Get metric for instances

        :param metric_name: metric name
        :param instance_ids: a list of instance ids
        :param start_date: metric start datetime date
        :param end_date: metric end datetime date
        :param interval: time interval in seconds
        :param folder_id: id of folder
        :return: dict
        """
        resource_ids_str = '|'.join(instance_ids)
        query = "%s{resource_id=\"%s\"}" % (metric_name, resource_ids_str)
        downsampling = {
            "gridInterval": str(interval * MSEC_IN_SEC),
            "gapFilling": "NONE"
        }
        return self._get_metrics(start_date, end_date, query, folder_id,
                                 downsampling)

    def get_regions_coordinates(self):
        return self.config.get('regions_coordinates', {}) or REGIONS_COORDINATES

    def get_prices(self, currency='USD', filter=None, **kwargs):
        request = ListSkusRequest(currency=currency)
        if filter:
            request.filter = filter
        result = self.send_list_paged_request(
            self.sku_service.List, request, 'skus')
        return [MessageToDict(x) for x in result]

    def security_groups_list(self, folder_id):
        request = ListSecurityGroupsRequest(folder_id=folder_id)
        security_groups = self.send_list_paged_request(
            self.sg_service.List, request, 'security_groups')
        return [MessageToDict(x) for x in security_groups]

    def service_accounts_list(self, folder_id):
        request = ListServiceAccountsRequest(folder_id=folder_id)
        service_accounts = self.send_list_paged_request(
            self.service_acc_service.List, request, 'service_accounts')
        return [MessageToDict(x) for x in service_accounts]

    def set_currency(self, currency):
        pass

    def configure_last_import_modified_at(self):
        pass
