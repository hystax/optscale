from optscale_exceptions.common_exc import NotFoundException
from rest_api_server.controllers.base import BaseController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.exceptions import Err
from rest_api_server.models.models import ProfilingToken


class InfraProfilingTokenController(BaseController):
    def _get_model_type(self):
        return ProfilingToken

    def get(self, infrastructure_token, **kwargs):
        token = self.session.query(ProfilingToken).filter(
            ProfilingToken.deleted.is_(False),
            ProfilingToken.infrastructure_token == infrastructure_token
        ).one_or_none()
        if not token:
            raise NotFoundException(
                Err.OE0527, ["infrastructure token", infrastructure_token])
        return token


class InfraProfilingTokenAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return InfraProfilingTokenController
