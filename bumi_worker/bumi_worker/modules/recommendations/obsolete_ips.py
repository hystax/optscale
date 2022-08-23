from collections import OrderedDict

from bumi_worker.modules.base import ModuleBase

DEFAULT_DAYS_THRESHOLD = 7
SUPPORTED_CLOUD_TYPES = [
    'aws_cnr',
    'azure_cnr',
    'alibaba_cnr',
]


class ObsoleteIps(ModuleBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DEFAULT_DAYS_THRESHOLD},
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []}
        })

    def _get(self):
        (days_threshold, excluded_pools,
         skip_cloud_accounts) = self.get_options_values()
        ca_type_map = self.get_cloud_accounts(
            SUPPORTED_CLOUD_TYPES, skip_cloud_accounts, True)
        date_field_name = 'last_used'
        available_ip_addresses = self.get_resources_stuck_in_state(
            resource_type='ip_address',
            status_field_name='available',
            date_field_name=date_field_name,
            resource_stuck_condition=True,
            cloud_account_ids=list(ca_type_map.keys()),
            delta_days=days_threshold,
        )
        result = [
            {
                'cloud_resource_id': ip_address['cloud_resource_id'],
                'resource_name': ip_address.get('name'),
                'resource_id': ip_address['resource_id'],
                'cloud_account_id': ip_address['cloud_account_id'],
                'cloud_type': ca_type_map.get(ip_address['cloud_account_id']),
                'cost_not_active_ip': ip_address['cost_in_resource_state'],
                'saving': ip_address['savings'],
                'last_seen_active': ip_address['meta'][date_field_name],
                'region': ip_address['region'],
                'is_excluded': ip_address.get('pool_id') in excluded_pools,
            } for ip_address in available_ip_addresses.values()
            if ip_address.get('savings', 0) > 0
        ]
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return ObsoleteIps(organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Obsolete IPs'
