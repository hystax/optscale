from bumi_worker.modules.rightsizing_base import RightsizingBase, LimitType
from collections import OrderedDict
import logging

LOG = logging.getLogger(__name__)

DAYS_THRESHOLD = 3
RECOMMENDED_FLAVOR_CPU_MIN = 1


DEFAULT_METRIC = {
    'type': LimitType.Q99.value,
    'limit': 80,
}


class RightsizingInstances(RightsizingBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DAYS_THRESHOLD},
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

    def _get_alibaba_instances_info(self, resource_ids, cloud_account_ids):
        return self.get_base_alibaba_instances_info(
            resource_ids, cloud_account_ids,
            pay_as_you_go_item='Cloud server configuration')

    def _get_supported_func_map(self):
        return {
            'aws_cnr': {
                'instances_info': self.get_base_aws_instances_info,
                'family_specs': self.get_base_family_specs,
                'metric': self.get_base_agr_cpu_metric,
            },
            'azure_cnr': {
                'instances_info': self.get_base_azure_instances_info,
                'family_specs': self.get_base_family_specs,
                'metric': self.get_base_agr_cpu_metric,
            },
            'alibaba_cnr': {
                'instances_info': self._get_alibaba_instances_info,
                'family_specs': self.get_base_family_specs,
                'metric': self.get_base_agr_cpu_metric,
            },
            'gcp_cnr': {
                'instances_info': self.get_base_gcp_instances_info,
                'family_specs': self.get_base_family_specs,
                'metric': self.get_base_agr_cpu_metric,
            },
            'nebius': {
                'instances_info': self.get_base_nebius_instances_info,
                'family_specs': self.get_base_nebius_family_specs,
                'metric': self.get_base_agr_cpu_metric,
            }
        }

    def get_insider_resource_type(self):
        return 'instance'

    def _get_raw_expense_resource_filter(self):
        return {
            'resource_type': 'Instance',
            'meta.spotted': {'$ne': True},
        }


def main(organization_id, config_client, created_at, **kwargs):
    return RightsizingInstances(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Underutilized Instances'
