import uuid
from sqlalchemy import exists, and_
from rest_api_server.exceptions import Err
from rest_api_server.models.models import ProfilingToken, Organization
from optscale_exceptions.common_exc import NotFoundException, ConflictException
from rest_api_server.controllers.profiling.base import BaseProfilingController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper


class ProfilingTokenController(BaseProfilingController):
    def _get_model_type(self):
        return ProfilingToken

    def get(self, organization_id, **kwargs):
        return super().get_or_create_profiling_token(organization_id)


class ProfilingTokenAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ProfilingTokenController
