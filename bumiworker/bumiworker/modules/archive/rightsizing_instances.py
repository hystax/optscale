from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.recommendations.rightsizing_instances import (
    RightsizingInstances as RightsizingInstancesRecommendation
)
from bumiworker.bumiworker.modules.rightsizing_base import (
    HOURS_IN_DAY, DAYS_IN_MONTH, RightsizingArchiveBase)

NEBIUS_CLOUD_TYPE = 'nebius'


class RightsizingInstances(RightsizingArchiveBase,
                           RightsizingInstancesRecommendation):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'flavor changed')
        self.reason_description_map[
            ArchiveReason.RECOMMENDATION_IRRELEVANT] = (
            'recommended flavor more expensive')

    def set_additional_reasons(self, cloud_resource_map, cloud_account,
                               cloud_resource_id_instance_map,
                               optimizations_dict, days_threshold, result):
        cloud_resource_id_info_map = self._get_instances_info(
            list(cloud_resource_map.values()), cloud_account['id'],
            cloud_account['type'])
        metrics_map = self._get_metrics(
            list(cloud_resource_map.keys()), cloud_account['id'],
            days_threshold, cloud_account['type'])
        current_flavor_params = self._get_flavor_params(
            cloud_resource_id_info_map, cloud_resource_id_instance_map,
            cloud_account['type'])

        for params in current_flavor_params:
            cloud_resource_ids = params['resource_ids']
            region = params['region']
            family_specs = params['family_specs']
            flavor_params = params['flavor_params']
            if cloud_account['type'] == NEBIUS_CLOUD_TYPE:
                flavor_params['cloud_account_id'] = cloud_account['id']
            current_flavor = self._find_flavor(
                cloud_account['type'], region, family_specs, 'current',
                **flavor_params)
            if not current_flavor:
                for cloud_resource_id in cloud_resource_ids:
                    instance = cloud_resource_id_instance_map[
                        cloud_resource_id]
                    instance_key = self.get_record_key(instance)
                    optimization = optimizations_dict[instance_key]
                    self._set_reason_properties(
                        optimization, ArchiveReason.FAILED_DEPENDENCY,
                        'flavor not found')
                    result.append(optimization)
                continue

            cpu_flavor_map = {}
            for cloud_resource_id in cloud_resource_ids:
                current_r_info = cloud_resource_id_info_map[
                    cloud_resource_id][0]
                if (cloud_account['type'] == 'azure_cnr' and len(
                        cloud_resource_id_info_map[cloud_resource_id]) != 1):
                    meter_id = flavor_params['meter_id']
                    current_r_info = [
                        x for x in cloud_resource_id_info_map[
                            cloud_resource_id] if x['meter_id'] == meter_id][0]

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
                current_cost = current_r_info.get('day_cost',
                                                  0) * DAYS_IN_MONTH
                if not current_cost:
                    continue
                discount_multiplier = current_r_info.get(
                    'discount_multiplier', 1)
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


def main(organization_id, config_client, created_at, **kwargs):
    return RightsizingInstances(
        organization_id, config_client, created_at).get()
