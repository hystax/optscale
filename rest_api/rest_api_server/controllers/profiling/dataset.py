from requests.exceptions import HTTPError

from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.profiling.base import (
    BaseProfilingController)
from rest_api.rest_api_server.exceptions import Err

from tools.optscale_exceptions.common_exc import (
    NotFoundException, ConflictException)


class DatasetController(BaseProfilingController):
    def create(self, profiling_token, **kwargs):
        try:
            return self.create_dataset(profiling_token, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 409:
                raise ConflictException(
                    Err.OE0551,
                    ['Dataset', 'path', kwargs.get('path')])
            raise

    def __get(self, profiling_token, dataset_id) -> dict:
        try:
            dataset = self.get_dataset(profiling_token, dataset_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Dataset', dataset_id])
            raise
        return dataset

    def __edit(self, profiling_token, dataset_id, **kwargs) -> dict:
        try:
            dataset = self.update_dataset(
                profiling_token, dataset_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Dataset', dataset_id])
            raise
        return dataset

    def get(self, dataset_id, profiling_token):
        return self.__get(profiling_token, dataset_id)

    def edit(self, dataset_id, profiling_token, **kwargs):
        self.__get(profiling_token, dataset_id)
        return self.__edit(
            profiling_token, dataset_id, **kwargs)

    def delete(self, dataset_id, profiling_token):
        try:
            self.delete_dataset(profiling_token, dataset_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Dataset', dataset_id])
            if ex.response.status_code == 409:
                raise ConflictException(
                    Err.OE0555, [dataset_id])
            raise

    def list(self, profiling_token, dataset_ids=None):
        return self.list_datasets(profiling_token, dataset_ids=dataset_ids)


class DatasetAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return DatasetController
