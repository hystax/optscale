import logging
from bumi_worker.modules.recommendations.volumes_not_attached_for_a_long_time import SUPPORTED_CLOUD_TYPES
from bumi_worker.modules.stuck_in_state_for_a_long_time_base import StuckInStateForALongTimeBase

LOG = logging.getLogger(__name__)


class VolumesNotAttachedForALongTime(StuckInStateForALongTimeBase):
    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    @property
    def resource_type(self):
        return 'volume'

    def is_state_changed(self, resource, start_date):
        return (resource.get('meta', {}).get('attached') or
                resource.get('meta', {}).get('last_attached', 0) > start_date)


def main(organization_id, config_client, created_at, **kwargs):
    return VolumesNotAttachedForALongTime(
        organization_id, config_client, created_at).get()
