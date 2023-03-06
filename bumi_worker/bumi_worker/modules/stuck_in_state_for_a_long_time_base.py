import logging

from collections import defaultdict
from datetime import datetime, timedelta

from bumi_worker.consts import ArchiveReason
from bumi_worker.modules.base import ArchiveBase

LOG = logging.getLogger(__name__)


class StuckInStateForALongTimeBase(ArchiveBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            self.reason_description_map[ArchiveReason.RESOURCE_DELETED])
        self.reason_description_map[ArchiveReason.RECOMMENDATION_IRRELEVANT] = (
            'state changed')

    @property
    def resource_type(self):
        return NotImplemented

    def is_state_changed(self, resource, start_date):
        return NotImplemented

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        now = datetime.utcnow()
        days_threshold = previous_options['days_threshold']
        start_date = int((now - timedelta(days=days_threshold)).timestamp())
        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)

        result = []
        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            _, response = self.rest_client.cloud_resources_discover(
                self.organization_id, self.resource_type,
                filters={'cloud_account_id': [cloud_account_id]})
            resources_map = {r['cloud_resource_id']: r for r in response['data']}
            for optimization in optimizations_:
                resource = resources_map.get(
                    optimization['cloud_resource_id'], {})
                if not resource:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_APPLIED)
                elif self.is_state_changed(resource, start_date):
                    self._set_reason_properties(
                            optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT)
                else:
                    self._set_reason_properties(
                        optimization, ArchiveReason.OPTIONS_CHANGED)
                result.append(optimization)
        return result
