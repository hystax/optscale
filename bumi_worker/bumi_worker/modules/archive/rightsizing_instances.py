import logging

from collections import defaultdict
from datetime import datetime, timedelta

from bumi_worker.consts import ArchiveReason
from bumi_worker.modules.base import ArchiveBase
from bumi_worker.modules.recommendations.rightsizing_instances import (
    RightsizingInstances as RightsizingInstancesRecommendation)
from bumi_worker.modules.rightsizing_base import (
    HOURS_IN_DAY, DAYS_IN_MONTH)

LOG = logging.getLogger(__name__)


class RightsizingInstances(ArchiveBase, RightsizingInstancesRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'flavor changed')
        self.reason_description_map[ArchiveReason.RECOMMENDATION_IRRELEVANT] = (
            'recommended flavor more expensive')

    def _get_instances(self, cloud_account_ids, start_date):
        instances = super()._get_instances(cloud_account_ids, start_date)
        instances_by_account_map = {x: [] for x in cloud_account_ids}
        for instance in instances:
            cloud_account_id = instance['cloud_account_id']
            instances_by_account_map[cloud_account_id].append(instance)
        return instances_by_account_map

    def _get(self, previous_options, optimizations, **kwargs):
        days_threshold = previous_options['days_threshold']
        skip_cloud_accounts = previous_options['skip_cloud_accounts']

        supported_func_map = self._get_supported_func_map()
        cloud_accounts_map = self.get_cloud_accounts(
            list(supported_func_map.keys()), skip_cloud_accounts)

        cloud_acc_instances_map = defaultdict(dict)
        min_dt = datetime.utcnow() - timedelta(days=days_threshold)
        for cloud_acc_id, instances in self._get_instances(
                list(cloud_accounts_map.keys()), int(min_dt.timestamp())).items():
            for instance in instances:
                instance_key = self.get_record_key(instance)
                cloud_acc_instances_map[cloud_acc_id][instance_key] = instance

        account_optimizations_map = defaultdict(dict)
        for optimization in optimizations:
            optimization_key = self.get_record_key(optimization)
            account_optimizations_map[optimization['cloud_account_id']][
                optimization_key] = optimization

        result = []
        for cloud_account_id, optimizations_dict in account_optimizations_map.items():
            cloud_account = cloud_accounts_map.get(cloud_account_id)
            if not cloud_account:
                for optimization in optimizations_dict.values():
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            instances_map = cloud_acc_instances_map.get(cloud_account_id, {})
            cloud_resource_id_map = {}
            cloud_resource_id_instance_map = {}
            for instance_key, optimization in optimizations_dict.items():
                instance = instances_map.get(instance_key)
                if not instance:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RESOURCE_DELETED)
                    result.append(optimization)
                    continue
                elif instance['meta']['flavor'] == optimization['recommended_flavor']:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_APPLIED)
                    result.append(optimization)
                    continue
                else:
                    cloud_resource_id_map[instance['cloud_resource_id']] = instance['_id']
                    cloud_resource_id_instance_map[instance['cloud_resource_id']] = instance

            if not cloud_resource_id_instance_map:
                continue

            cloud_resource_id_info_map = self._get_instances_info(
                list(cloud_resource_id_map.keys()), cloud_account_id,
                cloud_account['type'])
            metrics_map = self._get_metrics(
                list(cloud_resource_id_map.values()), cloud_account_id,
                days_threshold, cloud_account['type'])
            current_flavor_params = self._get_flavor_params(
                cloud_resource_id_info_map, cloud_resource_id_instance_map,
                cloud_account['type'])

            for params in current_flavor_params:
                cloud_resource_ids = params['resource_ids']
                region = params['region']
                family_specs = params['family_specs']
                flavor_params = params['flavor_params']
                current_flavor = self._find_flavor(
                    cloud_account['type'], region, family_specs, 'current',
                    **flavor_params)
                if not current_flavor:
                    for cloud_resource_id in cloud_resource_ids:
                        instance = cloud_resource_id_instance_map[cloud_resource_id]
                        instance_key = self.get_record_key(instance)
                        optimization = optimizations_dict[instance_key]
                        self._set_reason_properties(
                            optimization, ArchiveReason.FAILED_DEPENDENCY,
                            'flavor not found')
                        result.append(optimization)
                    continue

                cpu_flavor_map = {}
                for cloud_resource_id in cloud_resource_ids:
                    instance = cloud_resource_id_instance_map[cloud_resource_id]
                    metric = metrics_map.get(instance['_id'])
                    instance_key = self.get_record_key(instance)
                    optimization = optimizations_dict[instance_key]
                    if metric is None:
                        self._set_reason_properties(
                            optimization, ArchiveReason.FAILED_DEPENDENCY,
                            'metric not found')
                        result.append(optimization)
                        continue
                    recommended_cpu = optimization['recommended_flavor_cpu']
                    if not cpu_flavor_map.get(recommended_cpu):
                        flavor_params['cpu'] = recommended_cpu
                        recommended_flavor = self._find_flavor(
                            cloud_account['type'], region, family_specs,
                            'search_relevant', **flavor_params)
                        if not recommended_flavor:
                            self._set_reason_properties(
                                optimization, ArchiveReason.FAILED_DEPENDENCY,
                                'recommended flavor not found')
                            result.append(optimization)
                            continue
                        cpu_flavor_map[recommended_cpu] = recommended_flavor
                    else:
                        recommended_flavor = cpu_flavor_map[recommended_cpu]
                    current_cost = cloud_resource_id_info_map.get(
                        cloud_resource_id, {}).get('day_cost', 0) * DAYS_IN_MONTH
                    if not current_cost:
                        continue
                    discount_multiplier = cloud_resource_id_info_map.get(
                        cloud_resource_id).get('discount_multiplier', 1)
                    recommended_cost = (
                            recommended_flavor.get('price') * HOURS_IN_DAY *
                            DAYS_IN_MONTH * discount_multiplier)
                    if recommended_cost >= current_cost:
                        self._set_reason_properties(
                            optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT)
                    else:
                        self._set_reason_properties(
                            optimization, ArchiveReason.OPTIONS_CHANGED)
                    result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return RightsizingInstances(
        organization_id, config_client, created_at).get()
