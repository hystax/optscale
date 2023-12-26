from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.profiling.base import (
    BaseProfilingController)


class LabelController(BaseProfilingController):
    def list(self, profiling_token):
        return self.list_labels(profiling_token)


class LabelAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return LabelController
