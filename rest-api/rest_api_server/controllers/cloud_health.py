import logging

import pymongo

from optscale_exceptions.common_exc import FailedDependency
from rest_api_server.controllers.base import BaseController, MongoMixin
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.exceptions import Err
from rest_api_server.models.models import Organization

LOG = logging.getLogger(__name__)


class CloudHealthController(BaseController, MongoMixin):
    def _get_model_type(self):
        return Organization

    def get_cloud_health(self, organization_id):
        latest_health_result = list(self.health_collection.find(
            {'organization_id': organization_id}).sort(
            'created_at', pymongo.DESCENDING).limit(1))
        if not latest_health_result:
            raise FailedDependency(Err.OE0458, [])
        return latest_health_result[0]['health']


class CloudHealthAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return CloudHealthController
