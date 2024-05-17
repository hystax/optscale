from requests.exceptions import HTTPError

from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.profiling.base import (
    BaseProfilingController)
from rest_api.rest_api_server.exceptions import Err

from tools.optscale_exceptions.common_exc import (
    NotFoundException, ConflictException)


class ModelVersionController(BaseProfilingController):

    def create(self, run_id, model_id, profiling_token, **kwargs):
        try:
            model_version = self.create_model_version(
                profiling_token, run_id, model_id,  **kwargs)
        except HTTPError as exc:
            if exc.response.status_code == 409:
                raise ConflictException(Err.OE0557, [])
            elif exc.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Model', model_id])
            raise
        return model_version

    def edit(self, run_id, model_id, profiling_token, **kwargs):
        try:
            model_version = self.update_model_version(
                profiling_token, run_id, model_id, **kwargs)
        except HTTPError as exc:
            if exc.response.status_code == 409:
                raise ConflictException(
                    Err.OE0534, ['Model', kwargs.get('key')])
            elif exc.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Model version', ''])
            raise
        return model_version

    def delete(self, run_id, model_id, profiling_token):
        try:
            self.delete_model_version(profiling_token, run_id, model_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Model version', model_id])
            raise

    def get_versions_by_task(self, task_id, profiling_token):
        return self.get_model_version_by_task(profiling_token, task_id)


class ModelVersionAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ModelVersionController
