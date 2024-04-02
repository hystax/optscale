from requests.exceptions import HTTPError

from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.profiling.base import (
    BaseProfilingController)
from rest_api.rest_api_server.exceptions import Err

from tools.optscale_exceptions.common_exc import (
    NotFoundException, ConflictException)


class ModelController(BaseProfilingController):

    def create(self, profiling_token, **kwargs):
        return self.create_model(profiling_token,  **kwargs)

    def get(self, model_id, profiling_token):
        try:
            model = self.get_model(profiling_token, model_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Model', model_id])
            raise
        return model

    def list(self, profiling_token):
        models = self.list_models(profiling_token)
        return models

    def edit(self, model_id, profiling_token, **kwargs):
        try:
            self.update_model(profiling_token, model_id, **kwargs)
        except HTTPError as exc:
            if exc.response.status_code == 409:
                raise ConflictException(
                    Err.OE0534, ['Model', kwargs.get('key')])
            elif exc.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Model', model_id])
            raise
        return self.get(model_id, profiling_token)

    def delete(self, model_id, profiling_token):
        try:
            self.delete_model(profiling_token, model_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Model', model_id])
            raise


class ModelAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ModelController
