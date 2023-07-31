from collections import OrderedDict
import logging

from bumi_worker.modules.base import ModuleBase

SUPPORTED_CLOUD_TYPES = [
    'aws_cnr',
    'nebius'
]

LOG = logging.getLogger(__name__)


class S3PublicBuckets(ModuleBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []}
        })

    def _get(self):
        (excluded_pools, skip_cloud_accounts) = self.get_options_values()
        ca_type_map = self.get_cloud_accounts(
            SUPPORTED_CLOUD_TYPES, skip_cloud_accounts, True)
        _, response = self.rest_client.cloud_resources_discover(
            self.organization_id, 'bucket')
        employees = self.get_employees()
        pools = self.get_pools()
        result = [
            {
                'cloud_resource_id': bucket['cloud_resource_id'],
                'resource_name': bucket.get('name'),
                'resource_id': bucket['resource_id'],
                'cloud_account_id': bucket['cloud_account_id'],
                'cloud_type': ca_type_map.get(
                    bucket['cloud_account_id']),
                'region': bucket['region'],
                'owner': self._extract_owner(
                    bucket.get('owner_id'), employees),
                'pool': self._extract_pool(
                    bucket.get('pool_id'), pools),
                'is_excluded': bucket.get('pool_id') in excluded_pools,
                'is_public_policy': bucket.get('meta', {}).get(
                    'is_public_policy', False),
                'is_public_acls': bucket.get('meta', {}).get(
                    'is_public_acls', False),
            } for bucket in response['data']
            if (bucket['cloud_account_id'] in list(ca_type_map.keys()) and (
                    bucket.get('meta', {}).get('is_public_policy') or
                    bucket.get('meta', {}).get('is_public_acls')
            ))
        ]
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return S3PublicBuckets(organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Public Amazon S3 buckets'
