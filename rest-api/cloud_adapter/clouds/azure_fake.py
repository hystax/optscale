import logging
import random
import uuid

from calendar import monthrange
from datetime import datetime, timedelta

from cloud_adapter.clouds.azure import Azure
from cloud_adapter.exceptions import InvalidParameterException
from cloud_adapter.clouds.fake_base import (
    FakeBase, ResourceKeys, encoded_tags, ResourceTypes, ETCD_FALSE)
from cloud_adapter.model import *


LOG = logging.getLogger(__name__)
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
METER_MAP = {
    ResourceTypes.snapshot.value: {  # monthly plan
        'UAE Central': ('f30013e2-2ef1-4ad6-b78e-a01fa48b985b', 0.065, 30),
        'North Central US': ('bf3fcbfd-1459-4fa2-a811-63c6b7e5c805', 0.05, 30),
        'Central India': ('f75ed2e9-e762-4c18-b03d-2418850912f7', 0.05, 30),
        'South Africa West': ('1406ae39-d98e-4177-9b07-5e55f90eecc3', 0.084, 30),
        'Switzerland North': ('d31c5659-3b5e-4cfd-ba54-ad2b5e40f13a', 0.06, 30),
        'UK West': ('cf857e09-a066-46e9-9f52-b6f73e70692c', 0.053, 30),
        'Australia Central': ('5de96fab-965a-48be-8174-1419c335bc65', 0.055, 30),
        'Japan West': ('8e3d0b36-054c-4a94-8d8c-f7f2a2e4daa6', 0.05, 30),
        'West Europe': ('78dd126f-f855-4670-8038-fd66cf0f43b9', 0.05, 30),
        'Norway West': ('fee77163-fb9e-48cf-aba9-2b457ebed767', 0.0715, 30),
        'Norway East': ('3fa6d328-9bfc-4cc7-b549-3ae101405b53', 0.055, 30),
        'Korea South': ('cbd1f9fd-e2ad-4043-b28b-7e9764c83941', 0.05, 30),
        'Australia Central 2': ('b75e9aa9-da53-4555-85a3-d959206da92c', 0.055, 30),
        'France South': ('25c4c0cf-5bca-4eb4-9ed4-b0af6debabb7', 0.0689, 30),
        'UAE North': ('859e2612-e6b8-45d9-90d5-fbf3451b5a97', 0.06, 30),
        'South India': ('2c792503-0329-4f07-a86d-318c81801fca', 0.055, 30),
        'East US 2': ('6856e970-1d46-4c02-b3a9-8b33439dcc86', 0.05, 30),
        'North Europe': ('5590d778-a6e7-40ec-bc83-c1440ed75c75', 0.05, 30),
        'West US 2': ('709fabfd-58d9-4d80-b214-fbbc2b382737', 0.05, 30),
        'South Central US': ('bf8b1219-1441-4585-bb79-d13b27d4902a', 0.05, 30),
        'South Africa North': ('6e6f4a74-4425-4c16-a322-dff1e1845e16', 0.067, 30),
        'Australia Southeast': ('a8198418-2e2e-4306-a8e9-6a4efde3706a', 0.055, 30),
        'West India': ('76a5b6f0-4f64-49db-91c3-4fe047e86404', 0.05, 30),
        'Japan East': ('9dff13fe-340b-4a4b-98f1-ea682bf1ff2a', 0.05, 30),
        'Australia East': ('c7f0301d-bf22-4299-a802-b109706ca30a', 0.055, 30),
        'Southeast Asia': ('4830addf-b282-4f09-b910-47058857b9b4', 0.05, 30),
        'Germany North': ('e40fd385-1bb9-4b86-a509-2481a930ac3d', 0.065, 30),
        'Brazil South': ('97983058-bc5b-4bcc-8b58-46a91a5cb44e', 0.068, 30),
        'France Central': ('321bade6-6e08-41c3-a31e-2b057aa509f8', 0.053, 30),
        'West US': ('2e0f67c4-2e4d-46aa-b617-9348babd963a', 0.055, 30),
        'Central US': ('d8c6d5bb-5bd3-4403-8e16-19d391afeab2', 0.05, 30),
        'Korea Central': ('aeac33d0-90de-4070-bdab-4fd10ae673c1', 0.05, 30),
        'West Central US': ('d2b75e2e-da31-47ee-a2b0-660392eeec97', 0.05, 30),
        'East Asia': ('efdeacff-60f6-42a9-9512-3ce598bfe4f5', 0.05, 30),
        'UK South': ('78f10ecd-833b-49d9-a405-778c5fb85b5e', 0.053, 30),
        'Canada Central': ('8a4972f2-3c82-42f6-a544-0098ccdf236d', 0.055, 30),
        'Germany West Central': ('1825ddae-c4eb-4eec-8e17-f3d2ff4e1e53', 0.05, 30),
        'Switzerland West': ('d520a841-c707-48b5-8d52-690036f7441c', 0.078, 30),
        'East US': ('5e2335d3-5b76-4bc3-a040-f3a4b0342ca7', 0.05, 30),
        'Canada East': ('a863cc88-6658-4c15-9e2e-ca7b8cab68a7', 0.055, 30)
    },
    ResourceTypes.bucket.value: {
        'Norway West': ('c5ecef5e-e46f-476a-9471-24778b512cbd', 0.00615, 1),
        'Global': ('40551b4c-e8be-48ed-b70b-f8d25c7de724', 0.00036, 1),
        'Norway East': ('c416c289-a03d-4801-8ad0-b32a3302c111', 0.00473, 1)
    },
    ResourceTypes.volume.value: {  # monthly plan
        'UAE Central': ('1e1213e1-0496-4acf-8c0f-7c9d29ff13f0', 1.9968, 30),
        'North Central US': ('8fdefc41-3297-4d45-91df-bef6503e6a35', 1.536, 30),
        'Central India': ('c5d27838-2db2-45df-96fd-04d97d099e74', 1.6896, 30),
        'South Africa West': ('3cc969b0-1255-4555-8e41-7999577cc4b3', 2.58, 30),
        'Switzerland North': ('ebb0eadb-1ede-42e6-bc10-25bccd66144c', 1.843, 30),
        'Australia Central 2': ('dca58fa3-b605-487a-ae02-d62b61c2beb4', 2.4576, 30),
        'Australia Central': ('01dfef31-f0fa-4272-8e30-1f3ad86d6c35', 2.4576, 30),
        'Japan West': ('cc288026-9ec7-44fe-9cfc-d0ea5fcc4941', 1.536, 30),
        'West Europe': ('17fff823-37f4-4e7c-904d-063ea1a0470f', 1.536, 30),
        'East US': ('ac5f153e-9a9e-480c-867d-95550d4ebdd4', 1.536, 30),
        'Norway West': ('497b2135-7df4-429f-9720-5c1bdcd00242', 2.196, 30),
        'Norway East': ('a4027573-483a-440e-8093-40b4db5c5376', 1.69, 30),
        'Korea South': ('550730bb-ca2c-4c72-86fd-8cefef01ae85', 1.536, 30),
        'UK West': ('c90b8f68-2874-44d0-b237-bae9dc89c4a6', 1.69, 30),
        'France South': ('cac60b83-0bae-481d-981d-6e32c8f9c41f', 2.197, 30),
        'South Africa North': ('f8aaf115-8eea-418f-b272-9e2676b62537', 2.058, 30),
        'UAE North': ('9217b7da-db3d-424f-be50-7d5dfbad00ba', 1.8432, 30),
        'Southeast Asia': ('f0bb3187-895f-48f6-b1fa-2b8c1ec5d3dd', 1.536),
        'East US 2': ('f1473d74-4582-414f-a3b8-72cc875f3083', 1.536, 30),
        'North Europe': ('e85fc914-f84f-4355-a58c-7428ff8d59a4', 1.536, 30),
        'West US 2': ('6996a834-1819-48f7-b3dd-870eff051738', 1.536, 30),
        'South Central US': ('40cde86c-fc11-4aae-b982-44c24a1f4f03', 1.536, 30),
        'South India': ('9edd296d-9b3a-4922-87f9-6947c6cf281e', 1.536, 30),
        'Australia Southeast': ('1a19c500-e0ff-4d17-92dc-14fb613deb0c', 2.4576, 30),
        'West India': ('7338c3d2-bf72-4d9f-bef1-0ac5465b8cf2', 1.6896, 30),
        'Japan East': ('27a287f3-2919-4084-99e8-03404a652117', 1.536, 30),
        'Australia East': ('973dcef7-0cbf-419a-91a8-cd74ce67b517', 2.4576, 30),
        'Germany North': ('4493a82f-97b2-4c3f-a3f2-44c3fe57bb8a', 1.997, 30),
        'Brazil South': ('bd5a77f6-93be-4dde-8822-be7f8f4df8d8', 3.6864, 30),
        'France Central': ('a92446f4-275d-42e7-ac2e-a11877ed2391', 1.69, 30),
        'West US': ('5bd2bbb3-f558-4760-a308-2ccf0d8213b6', 1.536, 30),
        'Central US': ('c7638eaa-5f35-42db-aed0-d4d45351167a', 1.536, 30),
        'Korea Central': ('981590b5-ed9d-4f1e-9ac3-60b069faffa3', 1.536, 30),
        'West Central US': ('a03bc5ba-8fc9-455d-a6ea-3899b974dd97', 1.536, 30),
        'East Asia': ('acd3af8c-a077-46bc-89b7-a1ed2e99ed32', 1.536, 30),
        'UK South': ('e7056c15-dc2d-4913-8b0e-06fd876a88ea', 1.69, 30),
        'Canada Central': ('afe37018-6f94-46fb-82e5-0c35b2dc9976', 1.69, 30),
        'Germany West Central': ('cc7e9b92-83fb-4d49-909f-5cfac1eb6dfb', 1.536, 30),
        'Switzerland West': ('d9b930b7-a805-4e38-8662-2d027cab4948', 2.396, 30),
        'Canada East': ('264e9592-46ba-4ca4-bc72-2aca119a5909', 1.69, 30)
    },
    ResourceTypes.instance.value: {  # hourly plan
        'UAE Central': ('ba97ea7b-f85a-44f0-b6f2-ffffe1f136cb', 0.0312, 0.042),
        'North Central US': ('9791eac0-bf09-45c6-ade0-07b8d3f6b24c', 0.0208, 0.042),
        'Central India': ('8a35c554-c469-44cd-b1ba-ed7cb1624dfd', 0.0224, 0.042),
        'South Africa West': ('c7e4ebab-7ad1-4476-a855-5c411e72370f', 0.033875, 0.042),
        'Switzerland North': ('7c2bb18f-c283-4a83-95fc-bef4fb8d4cd5', 0.0288, 0.042),
        'Australia Central 2': ('c54889f7-aeeb-478c-9cb0-3e8c631f684d', 0.0264, 0.042),
        'Australia Central': ('6c5a6ca8-86fe-46ac-98e1-b95d01dfe940', 0.0264, 0.042),
        'Japan West': ('6ec9692a-2fa4-4d1c-b55b-8691d03ff0b4', 0.03, 0.042),
        'West Europe': ('4acc0010-24b6-4abc-82cc-3b7debbcc98f', 0.024, 0.042),
        'Norway West': ('a3d7850d-b474-41dc-9a38-7852b3b8f220', 0.0343, 0.042),
        'Norway East': ('00282b36-8ce0-47c8-8906-d9c7e0a357ca', 0.0264, 0.042),
        'Korea South': ('71f9b500-841b-4bd5-9587-5f53a7d1667c', 0.026, 0.042),
        'UK West': ('3abaa14d-6308-4045-9829-b623e5d6a6f3', 0.0235, 0.042),
        'France South': ('fdd517dc-decc-4805-809e-716b80dc316c', 0.0338, 0.042),
        'South Africa North': ('321e26aa-5f7f-4f14-a409-58851b67c53f', 0.0271, 0.042),
        'Southeast Asia': ('a004a4c9-c952-4469-b334-ef882e857e50', 0.0264, 0.042),
        'UAE North': ('c7d515c1-f9d8-4987-b379-d7b86d0df8a8', 0.025, 0.042),
        'East US 2': ('d60b3b20-cc76-404d-a77c-f002a781aaa1', 0.0208, 0.042),
        'North Europe': ('2badf567-f11f-427b-8242-72d7727775ea', 0.0227, 0.042),
        'West US 2': ('e3932c3d-5dfd-40a5-b83e-109075894c9e', 0.0207, 0.042),
        'South Central US': ('fc24ad6b-7ead-4908-bed9-fd596bb27eab', 0.025, 0.042),
        'South India': ('ae5ff09f-98b8-4d78-a16d-8ee571763bb6', 0.0294, 0.042),
        'Australia Southeast': ('a605b0dc-4000-4c95-bdb5-bd3a8ae38ed2', 0.0264, 0.042),
        'West India': ('ce5e9b37-3d1b-436d-9425-b641755efe64', 0.03, 0.042),
        'Japan East': ('d16b2f57-71c9-4b01-afd5-f34b48ae1b4d', 0.0272, 0.042),
        'Australia East': ('3bad7410-2a95-4519-96a5-666d684068ae', 0.0264, 0.042),
        'Germany North': ('f0f415f3-8dc3-45f7-91c5-29313f7cccc8', 0.0312, 0.042),
        'Brazil South': ('a339df4e-9111-4caf-8c17-2027d279826b', 0.0336, 0.042),
        'France Central': ('ccebde6c-ccc9-43be-a10c-3f356e625b99', 0.0236, 0.042),
        'West US': ('3492700f-2a14-4f8a-8718-fb3db465ac4a', 0.0248, 0.042),
        'Central US': ('defe022f-4478-49c7-9629-1e351b7ba8f3', 0.025, 0.042),
        'Korea Central': ('f5eb2b36-d42b-4315-a767-ddb6247df2be', 0.026, 0.042),
        'West Central US': ('4a0cdecf-3dd7-4cad-b1df-6ee048510aab', 0.025, 0.042),
        'East Asia': ('9813a58c-d5fd-4f13-b341-c881c1017f1e', 0.0292, 0.042),
        'UK South': ('b27ce685-a5c9-41ec-be27-8129ed7d7f18', 0.0236, 0.042),
        'Canada Central': ('cecbfba3-a2fa-4ddb-a677-6fa4761fcffd', 0.023, 0.042),
        'Germany West Central': ('ea6a23ca-4b29-4087-a4bd-ed76145ecb3c', 0.024, 0.042),
        'Switzerland West': ('87f90c87-d087-47ee-a537-1db6aa5c849c', 0.0374, 0.042),
        'East US': ('5f4181a3-1b7a-4d22-8993-53944136a0c2', 0.0207, 0.042),
        'Canada East': ('a0716d5a-2c14-4fae-8ed1-d52b9812e329', 0.0233, 0.042)
    }
}

EXPENSE_REGION_NAMES_MAP = {
    'Australia East': 'AU East',
    'Brazil South': 'BR South',
    'Australia Southeast': 'AU Southeast',
    'Germany North': 'DE North',
    'South Central US': 'US South Central',
    'Australia Central': 'AU Central',
    'UK West': 'UK West',
    'West India': 'IN West',
    'North Europe': 'EU North',
    'Korea Central': 'KR Central',
    'Norway West': 'NO West',
    'Japan West': 'JA West',
    'East US 2': 'US East 2',
    'West Europe': 'EU West',
    'France Central': 'FR Central',
    'West US 2': 'US West 2',
    'Australia Central 2': 'AU Central 2',
    'Japan East': 'JA East',
    'Switzerland North': 'CH North',
    'East Asia': 'AP East',
    'South Africa West': 'ZA West',
    'UAE Central': 'AE Central',
    'Norway East': 'NO East',
    'France South': 'FR South',
    'UAE North': 'AE North',
    'South Africa North': 'ZA North',
    'North Central US': 'US North Central',
    'East US': 'US East',
    'UK South': 'UK South',
    'Germany West Central': 'DE West Central',
    'Canada East': 'CA East',
    'South India': 'IN South',
    'Southeast Asia': 'AP Southeast',
    'Korea South': 'KR South',
    'West Central US': 'US West Central',
    'Canada Central': 'CA Central',
    'Switzerland West': 'CH West',
    'West US': 'US West',
    'Central US': 'US Central',
    'Central India': 'IN Central'
}


class AzureExpenseModel(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, dict):
                setattr(self, k, AzureExpenseModel(**v))
            else:
                setattr(self, k, v)

    def as_dict(self):
        res = {}
        for key in self.__dict__:
            val = getattr(self, key)
            if isinstance(val, AzureExpenseModel):
                res[key] = val.as_dict()
            else:
                res[key] = val
        return res


class AzureFake(FakeBase, Azure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cloud_type = 'azure_cnr'

    @property
    def location_map(self):
        return {k: v['name'] for k, v in self._get_coordinates_map().items()}

    def _gen_id(self, resource_key, region, base=None):
        new_id = '/subscriptions/%s/%s/%s/%s/%s' % (
            self._subscription_id,
            self._cloud_type.split('_')[0],
            region,
            resource_key.value,
            base if base else uuid.uuid4().hex)
        # otherwise several accs rss will point to the same base
        # (instance -> image for example) due to hash based logic
        if self.config.get('id'):
            new_id = '%s/%s' % (new_id, self.config['id'])
        return new_id

    def _get_existing_resources_query(self, resource_type, region,
                                      config_hash):
        query = {
            'active': True,
            'resource_type': resource_type,
            'region': self.location_map.get(region),
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
            'region': {'$in': [self.location_map.get(r)
                               for r in regions]},
            **{'tags.%s' % k: {'$in': v}
               for k, v in encoded_config_hash.items()}
        }
        if self.config.get('id'):
            query['cloud_account_id'] = self.config['id']
        if active:
            query['active'] = True
        elif first_seen > 0:
            query['first_seen'] = {'$gte': first_seen}
        LOG.debug(query)
        return query

    def _create_volume(self, region, resource_config, config_hash,
                       volume_id=None, attached=False, **kwargs):
        if not volume_id:
            volume_id = self._gen_id(ResourceKeys.volumes, region)
        cloud_console_link = self._generate_cloud_link(volume_id)

        tags = resource_config.get('tags', {}).copy()
        tags['group_config_hash'] = config_hash

        obj = VolumeResource(
            cloud_resource_id=volume_id,
            cloud_account_id=self.cloud_account_id,
            region=self.location_map.get(region),
            name=tags.get('Name'),
            size=10,
            volume_type='Microsoft.Compute/disks',
            organization_id=self.organization_id,
            tags=tags,
            attached=attached,
            cloud_console_link=cloud_console_link
        )
        return obj

    def discover_volume_resources(self):
        result = list()
        for region in self.config_regions:
            result.extend(self._discover_resources(
                ResourceKeys.volumes, region))
        return result

    def _create_snapshot(self, region, resource_config, config_hash,
                         snapshot_id=None, **kwargs):
        if not snapshot_id:
            snapshot_id = self._gen_id(ResourceKeys.snapshots, region)
        cloud_console_link = self._generate_cloud_link(snapshot_id)

        tags = resource_config.get('tags', {}).copy()
        tags['group_config_hash'] = config_hash

        obj = SnapshotResource(
            cloud_resource_id=snapshot_id,
            cloud_account_id=self.cloud_account_id,
            region=self.location_map.get(region),
            organization_id=self.organization_id,
            name=tags.get('Name'),
            size=10,
            description=None,
            state='Succeeded',
            tags=tags,
            cloud_console_link=cloud_console_link
        )
        return obj

    def discover_snapshot_resources(self):
        result = list()
        for region in self.config_regions:
            result.extend(self._discover_resources(
                ResourceKeys.snapshots, region))
        return result

    def _create_bucket(self, region, resource_config, config_hash,
                       bucket_id=None, **kwargs):
        if not bucket_id:
            bucket_id = self._gen_id(ResourceKeys.buckets, region)
        cloud_console_link = self._generate_cloud_link(bucket_id)

        tags = resource_config.get('tags', {}).copy()
        tags['group_config_hash'] = config_hash

        obj = BucketResource(
            cloud_resource_id=bucket_id,
            cloud_account_id=self.cloud_account_id,
            region=self.location_map.get(region),
            organization_id=self.organization_id,
            name=bucket_id,
            tags=tags,
            cloud_console_link=cloud_console_link
        )
        return obj

    def discover_bucket_resources(self):
        result = list()
        for region in self.config_regions:
            result.extend(self._discover_resources(
                ResourceKeys.buckets, region))
        return result

    def _create_instance(self, region, resource_config, config_hash,
                         instance_id=None, **kwargs):
        if not instance_id:
            instance_id = self._gen_id(ResourceKeys.instances, region)
        cloud_console_link = self._generate_cloud_link(instance_id)

        tags = resource_config.get('tags', {}).copy()
        tags['group_config_hash'] = config_hash

        obj = InstanceResource(
            cloud_resource_id=instance_id,
            cloud_account_id=self.cloud_account_id,
            region=self.location_map.get(region),
            name=tags.get('Name'),
            flavor='Standard_B1ms',
            stopped_allocated=bool(
                random.getrandbits(1)) if self._check_bool_key(
                resource_config, 'stopped_allocated', ETCD_FALSE) else False,
            organization_id=self.organization_id,
            tags=tags,
            spotted=self._check_bool_key(resource_config, 'spot', ETCD_FALSE),
            cloud_console_link=cloud_console_link
        )
        return obj

    def discover_instance_resources(self):
        result = list()
        for region in self.config_regions:
            result.extend(self._discover_resources(
                ResourceKeys.instances, region))
        return result

    @staticmethod
    def _region_usage(resource_type, region, period_start, period_end):
        resource_meter_map = METER_MAP.get(resource_type, {})
        meter_id, price, divider = resource_meter_map.get(
            region, resource_meter_map.get('Global', (None, 0, 1)))
        if not meter_id:
            return meter_id, price, 0
        quantity = (period_end - period_start).total_seconds() / 3600 / 24 / divider
        cost = price * quantity
        return meter_id, cost, quantity

    def _get_expense_record(self, resource, usage_start, usage_end):
        resource_type_meter_map = {
            ResourceTypes.instance.value: 'Virtual Machines',
            ResourceTypes.volume.value: 'Storage',
            ResourceTypes.snapshot.value: 'Storage',
            ResourceTypes.bucket.value: 'Storage'
        }
        region = resource['region']

        resource_meter_map = METER_MAP.get(resource['resource_type'], {})
        meter_id, price, divider = resource_meter_map.get(
            region, resource_meter_map.get('Global', (None, 0, 1)))
        if not meter_id:
            return
        quantity = (usage_end - usage_start).total_seconds() / 3600 / 24 / divider
        billing_period = (usage_start + timedelta(
            days=monthrange(usage_start.year, usage_start.month)[1]
        )).strftime('%Y%m')

        return AzureExpenseModel(
            meter_id=meter_id,
            billing_period_id='/subscriptions/%s/providers/Microsoft.Billing/billingPeriods/%s' % (
                self._subscription_id, billing_period),
            instance_id=resource['cloud_resource_id'],
            instance_name=resource.get('name'),
            instance_location=EXPENSE_REGION_NAMES_MAP.get(region),
            subscription_guid=self._subscription_id,
            tags=encoded_tags(resource['tags'], decode=True),
            usage_end=(usage_end + timedelta(
                seconds=1)).strftime(DATE_FORMAT),
            usage_start=usage_start.strftime(DATE_FORMAT),
            currency='USD',
            consumed_service='Microsoft.Compute',
            type='Microsoft.Consumption/usageDetails',
            pretax_cost=price * quantity,
            usage_quantity=quantity,
            meter_details={
                "meter_category": resource_type_meter_map.get(
                    resource['resource_type']),
            }
        )

    def get_usage(self, start_date, range_end=None, limit=None):
        now = datetime.utcnow()
        if start_date > now:
            start_date = now
        if range_end is None or range_end < start_date:
            range_end = now

        LOG.info('Collecting expenses for %s-%s', start_date, range_end)
        for expense in self._get_expenses(start_date, range_end):
            yield expense

    def validate_credentials(self, org_id=None):
        if not self.config['subscription_id'].strip():
            raise InvalidParameterException(
                "The subscription '%s' could not be found." %
                self.config['subscription_id'])
        return {'account_id': self.config['subscription_id'], 'warnings': []}

    def configure_last_import_modified_at(self):
        pass

    def set_currency(self, currency):
        pass
