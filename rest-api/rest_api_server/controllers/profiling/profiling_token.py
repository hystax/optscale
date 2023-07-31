from rest_api_server.models.models import ProfilingToken
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
