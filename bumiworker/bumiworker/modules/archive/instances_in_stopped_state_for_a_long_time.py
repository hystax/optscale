import logging
from bumiworker.bumiworker.modules.recommendations.instances_in_stopped_state_for_a_long_time import (
    SUPPORTED_CLOUD_TYPES)
from bumiworker.bumiworker.modules.stuck_in_state_for_a_long_time_base import StuckInStateForALongTimeBase

LOG = logging.getLogger(__name__)


class InstancesInStoppedStateForALongTime(StuckInStateForALongTimeBase):
    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    @property
    def resource_type(self):
        return 'instance'

    def is_state_changed(self, resource, start_date):
        return (resource.get('meta', {}).get(
            'last_seen_not_stopped', 0) >= start_date or
                not resource.get('meta', {}).get('stopped_allocated'))


def main(organization_id, config_client, created_at, **kwargs):
    return InstancesInStoppedStateForALongTime(
        organization_id, config_client, created_at).get()
