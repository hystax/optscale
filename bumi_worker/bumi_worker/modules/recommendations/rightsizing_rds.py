from collections import OrderedDict
import logging

from bumi_worker.modules.rightsizing_base import RightsizingBase, LimitType

LOG = logging.getLogger(__name__)
DEFAULT_DAYS_THRESHOLD = 3
RECOMMENDED_FLAVOR_CPU_MIN = 1


DEFAULT_METRIC = {
    'type': LimitType.Q99.value,
    'limit': 80,
}


class RightsizingRds(RightsizingBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DEFAULT_DAYS_THRESHOLD},
            'metric': {
                'default': DEFAULT_METRIC,
                'clean_func': self.clean_rightsizing_metric,
            },
            self.excluded_flavor_regex_key: {
                'default': '',
                'clean_func': self.clean_excluded_flavor_regex,
            },
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'recommended_flavor_cpu_min': {
                'default': RECOMMENDED_FLAVOR_CPU_MIN
            },
            'skip_cloud_accounts': {'default': []}
        })

    @staticmethod
    def _get_alibaba_family_specs(resource_info):
        return {
            'zone_id': resource_info['meta']['zone_id'],
            'category': resource_info['meta']['category'],
            'engine': resource_info['meta']['engine'],
            'engine_version': resource_info['meta']['engine_version'],
            'storage_type': resource_info['meta']['storage_type'],
            'source_flavor_id': resource_info['meta']['flavor'],
        }

    def _get_alibaba_instances_info(self, resource_ids, cloud_account_ids):
        return self.get_base_alibaba_instances_info(
            resource_ids, cloud_account_ids,
            pay_as_you_go_item='Class Code')

    def _get_supported_func_map(self):
        return {
            'alibaba_cnr': {
                'instances_info': self._get_alibaba_instances_info,
                'family_specs': self._get_alibaba_family_specs,
                'metric': self.get_base_agr_cpu_metric,
            },
        }

    def get_insider_resource_type(self):
        return 'rds_instance'

    def _get_raw_expense_resource_filter(self):
        return {
            'resource_type': 'RDS Instance',
        }


def main(organization_id, config_client, created_at, **kwargs):
    return RightsizingRds(organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Underutilized RDS Instances'
