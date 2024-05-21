from collections import OrderedDict

from bumiworker.bumiworker.modules.base import ModuleBase

DEFAULT_DAYS_THRESHOLD = 1
SUPPORTED_CLOUD_TYPES = [
    'azure_cnr',
    'alibaba_cnr',
]


class InstancesInStoppedStateForALongTime(ModuleBase):
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
        ca_map = self.get_cloud_accounts(
            SUPPORTED_CLOUD_TYPES, skip_cloud_accounts)
        date_field_name = 'last_seen_not_stopped'
        stopped_instances = self.get_resources_stuck_in_state(
            resource_type='instance',
            status_field_name='stopped_allocated',
            date_field_name=date_field_name,
            resource_stuck_condition=True,
            cloud_account_ids=list(ca_map.keys()),
            delta_days=days_threshold,
        )
        result = [
            {
                'cloud_resource_id': instance['cloud_resource_id'],
                'resource_name': instance.get('name'),
                'resource_id': instance['resource_id'],
                'cloud_account_id': instance['cloud_account_id'],
                'cloud_type': ca_map.get(
                    instance['cloud_account_id'], {}).get('type'),
                'cloud_account_name': ca_map.get(
                    instance['cloud_account_id'], {}).get('name'),
                'cost_in_stopped_state': instance['cost_in_resource_state'],
                'saving': instance['savings'],
                'last_seen_active': instance['meta'][date_field_name],
                'region': instance['region'],
                'is_excluded': instance.get('pool_id') in excluded_pools,
            } for instance in stopped_instances.values()
            if instance.get('savings', 0) > 0
        ]
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return InstancesInStoppedStateForALongTime(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Not deallocated Instances'
