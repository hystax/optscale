import logging

from collections import defaultdict
from datetime import datetime, timezone
from requests import HTTPError
from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.instance_generation_upgrade import (
    InstanceGenerationUpgrade as InstanceGenerationUpgradeRecommendation,
    SUPPORTED_CLOUD_TYPES
)

LOG = logging.getLogger(__name__)


class InstanceGenerationUpgrade(ArchiveBase,
                                InstanceGenerationUpgradeRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RESOURCE_DELETED] = (
            'instance deleted')
        self.reason_description_map[ArchiveReason.FAILED_DEPENDENCY] = (
            'recommended flavor unavailable')
        self.reason_description_map[ArchiveReason.RECOMMENDATION_IRRELEVANT] = (
            'flavor changed')

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get_recommended_flavor(self, instance, raw_info, cloud_type):
        meter_id = raw_info.get('meter_id')
        os_type = instance['meta'].get('os') or raw_info.get('os')
        preinstalled = raw_info.get('software')
        generation_params = {
            'cloud_type': cloud_type,
            'region': instance['region'],
            'current_flavor': instance['meta'].get('flavor'),
            'os_type': os_type,
        }
        if preinstalled and cloud_type == 'aws_cnr':
            generation_params['preinstalled'] = preinstalled
        if meter_id and cloud_type == 'azure_cnr':
            generation_params['meter_id'] = meter_id
        currency = self.get_organization_currency()
        current_daily_cost = self.get_current_daily_cost(raw_info)
        try:
            _, gen_resp = self.insider_cl.find_flavor_generation(
                **generation_params, currency=currency)
        except HTTPError:
            return
        if round(gen_resp.get('proposed_daily_price'), 8) <= round(
                current_daily_cost, 8):
            return gen_resp['proposed_flavor']

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        now = datetime.now(tz=timezone.utc)

        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)

        instances_map = self.get_instances_map(
            list(account_optimizations_map.keys()))

        result = []
        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue
            cloud_type = cloud_accounts_map[cloud_account_id]['type']
            cloud_resource_ids = [x['cloud_resource_id']
                                  for x in optimizations_]
            raw_infos = self.get_raw_expenses(now, [cloud_account_id],
                                              cloud_resource_ids)
            raw_infos_map = {x['_id']: x for x in raw_infos}

            for optimization in optimizations_:
                cloud_resource_id = optimization['cloud_resource_id']
                instance = instances_map.get(cloud_resource_id, {})
                current_flavor = instance.get('meta', {}).get('flavor')
                previous_flavor = optimization['flavor']
                raw_info = raw_infos_map.get(cloud_resource_id)
                if not instance:
                    reason = ArchiveReason.RESOURCE_DELETED
                elif current_flavor == optimization['recommended_flavor']:
                    reason = ArchiveReason.RECOMMENDATION_APPLIED
                elif current_flavor != previous_flavor:
                    reason = ArchiveReason.RECOMMENDATION_IRRELEVANT
                elif not self._get_recommended_flavor(
                        instance, raw_info, cloud_type):
                    reason = ArchiveReason.FAILED_DEPENDENCY
                else:
                    reason = ArchiveReason.OPTIONS_CHANGED
                self._set_reason_properties(optimization, reason)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return InstanceGenerationUpgrade(
        organization_id, config_client, created_at).get()
