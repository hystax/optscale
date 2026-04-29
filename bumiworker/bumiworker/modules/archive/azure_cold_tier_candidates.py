import logging
from collections import OrderedDict

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase

LOG = logging.getLogger(__name__)

SUPPORTED_CLOUD_TYPES = ['azure_cnr']
DEFAULT_DAYS_THRESHOLD = 30


class AzureColdTierCandidates(ArchiveBase):
    # Does NOT subclass the live recommendation class — the live module owns
    # Azure SDK calls; the archive only needs options comparison + MongoDB
    # lookups, both of which ArchiveBase already provides.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DEFAULT_DAYS_THRESHOLD},
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []},
        })
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'storage account moved to cold tier')
        self.reason_description_map[ArchiveReason.RECOMMENDATION_IRRELEVANT] = (
            'storage account no longer meets cold-tier criteria')

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        current_options = self.get_options()
        current_excluded_pools = set(
            (current_options.get('excluded_pools') or {}).keys())
        current_skip_accounts = set(
            current_options.get('skip_cloud_accounts') or [])

        resources_collection = self.mongo_client.restapi.resources
        result = []

        for optimization in optimizations:
            cloud_account_id = optimization['cloud_account_id']

            if cloud_account_id not in cloud_accounts_map:
                self._set_reason_properties(
                    optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                result.append(optimization)
                continue

            if cloud_account_id in current_skip_accounts:
                self._set_reason_properties(
                    optimization, ArchiveReason.OPTIONS_CHANGED)
                result.append(optimization)
                continue

            # options comparison: days_threshold or excluded_pools changed
            prev_days = (previous_options.get('days_threshold')
                         or DEFAULT_DAYS_THRESHOLD)
            curr_days = (current_options.get('days_threshold')
                         or DEFAULT_DAYS_THRESHOLD)
            if int(prev_days) != int(curr_days):
                self._set_reason_properties(
                    optimization, ArchiveReason.OPTIONS_CHANGED)
                result.append(optimization)
                continue

            pool_id = optimization.get('pool_id')
            if pool_id and pool_id in current_excluded_pools:
                self._set_reason_properties(
                    optimization, ArchiveReason.OPTIONS_CHANGED)
                result.append(optimization)
                continue

            # check whether the resource still exists in MongoDB
            resource_id = optimization.get('resource_id')
            resource = None
            if resource_id:
                resource = resources_collection.find_one({'_id': resource_id})

            if not resource:
                self._set_reason_properties(
                    optimization, ArchiveReason.RESOURCE_DELETED)
                result.append(optimization)
                continue

            # resource exists but was dropped from the live checklist —
            # either the tier was changed (applied) or it no longer qualifies
            current_tier = (resource.get('meta') or {}).get(
                'current_access_tier')
            target_tier = optimization.get('target_tier')
            if (current_tier and target_tier and
                    str(current_tier).lower() == str(target_tier).lower()):
                reason = ArchiveReason.RECOMMENDATION_APPLIED
            else:
                reason = ArchiveReason.RECOMMENDATION_IRRELEVANT

            self._set_reason_properties(optimization, reason)
            result.append(optimization)

        return result


def main(organization_id, config_client, created_at, **kwargs):
    return AzureColdTierCandidates(
        organization_id, config_client, created_at).get()
