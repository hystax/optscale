import logging
from rest_api_server.controllers.shareable_resource import ShareableBookingController
from optscale_exceptions.common_exc import NotFoundException
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.exceptions import Err

LOG = logging.getLogger(__name__)


class SplitShareableResourceController(ShareableBookingController):

    def split_resources(self, organization_id, resource_ids):
        resources, invalid_res, not_active_res = self._check_resources(
            organization_id, resource_ids)
        if invalid_res:
            raise NotFoundException(
                Err.OE0002, ['Resources', ', '.join(
                    x['id'] for x in invalid_res)])
        shareable, not_shareable, already = self.split_resources_by_shareability(
            resources)
        return {
            'not_eligible': not_shareable + not_active_res,
            'eligible': shareable,
            'already_shareable': already
        }


class SplitShareableResourceAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return SplitShareableResourceController
