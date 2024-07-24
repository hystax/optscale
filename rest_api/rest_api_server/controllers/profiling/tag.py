from requests.exceptions import HTTPError

from tools.optscale_exceptions.common_exc import NotFoundException

from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.profiling.base import (
    BaseProfilingController)
from rest_api.rest_api_server.exceptions import Err


class TagController(BaseProfilingController):
    def list(self, profiling_token, task_id):
        try:
            return self.list_tags(profiling_token, task_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Task', task_id])


class TagAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return TagController
