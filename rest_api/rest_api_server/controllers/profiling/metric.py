from tools.optscale_exceptions.common_exc import (NotFoundException,
                                                  ConflictException)
from rest_api.rest_api_server.exceptions import Err
from requests.exceptions import HTTPError
from rest_api.rest_api_server.controllers.profiling.base import BaseProfilingController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper


class MetricController(BaseProfilingController):

    def create(self, profiling_token, **kwargs):
        self.fix_kwargs(kwargs)
        try:
            metric = self.create_metric(profiling_token, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 409:
                raise ConflictException(Err.OE0535, [kwargs['key']])
            raise
        return metric

    def get(self, id, profiling_token):
        try:
            metric = self.get_metric(profiling_token, id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, ['Metric', id])
            raise
        return metric

    def list(self, profiling_token):
        return self.list_metrics(profiling_token)

    @staticmethod
    def fix_kwargs(kwargs):
        # we can't pass a parameter with a service name `func`
        function = kwargs.pop('function', None)
        if function:
            kwargs['func'] = function

    def edit(self, id, profiling_token, **kwargs):
        self.fix_kwargs(kwargs)
        self.update_metric(profiling_token, id, **kwargs)
        return self.get(id, profiling_token)

    def delete(self, id, profiling_token):
        try:
            self.delete_metric(profiling_token, id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, ['Metric', id])
            if ex.response.status_code == 409:
                raise ConflictException(Err.OE0554, [id])
            raise


class MetricAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return MetricController
