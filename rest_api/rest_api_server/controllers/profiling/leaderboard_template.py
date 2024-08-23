import logging
from requests.exceptions import HTTPError

from tools.optscale_exceptions.common_exc import (
    NotFoundException, ConflictException, WrongArgumentsException)

from rest_api.rest_api_server.controllers.profiling.base import (
    BaseProfilingController)
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.exceptions import Err

LOG = logging.getLogger(__name__)


class LeaderboardTemplateController(BaseProfilingController):
    @property
    def model_name(self):
        return 'LeaderboardTemplate'

    def get_metrics(self, profiling_token, lb_template, raise_exc=True):
        metrics_ids = [lb_template['primary_metric']] + lb_template.get(
            'other_metrics', [])
        existing_metrics = self.list_metrics(profiling_token)
        not_exist = set(metrics_ids) - set(x['id'] for x in existing_metrics)
        if not_exist and raise_exc:
            message = ', '.join(not_exist)
            raise NotFoundException(Err.OE0002, ['Metric', message])
        return {x['id']: x for x in existing_metrics if x['id'] in metrics_ids}

    @staticmethod
    def format_leaderboard_template(lb_template, metrics_map):
        for filter_ in lb_template['filters']:
            filter_metric = metrics_map.get(filter_['id'])
            if filter_metric:
                filter_['name'] = filter_metric.get('name')
        primary_metric = metrics_map.pop(
            lb_template['primary_metric'], None)
        lb_template['primary_metric'] = primary_metric
        lb_template['other_metrics'] = list(metrics_map.values())
        return lb_template

    def create(self, task_id, profiling_token, **kwargs):
        self.check_task(task_id, profiling_token)
        try:
            metrics_map = self.get_metrics(profiling_token, kwargs)
            lb_template = self.create_leaderboard_template(
                profiling_token, task_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 409:
                raise ConflictException(Err.OE0549, [task_id])
            raise
        return self.format_leaderboard_template(lb_template, metrics_map)

    def check_task(self, task_id, profiling_token):
        try:
            self.get_task(profiling_token, task_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002,
                                        ['Task', task_id])
            raise

    def get(self, task_id, profiling_token, details=False):
        self.check_task(task_id, profiling_token)
        lb_template = self.get_leaderboard_template(profiling_token, task_id)
        if lb_template:
            metrics_map = self.get_metrics(profiling_token, lb_template,
                                           raise_exc=False)
            lb_template = self.format_leaderboard_template(lb_template,
                                                           metrics_map)
            if details:
                lb_template['details'] = self._get_details(
                    task_id, profiling_token)
        return lb_template or {}

    def get_by_id(self, lb_template_id, profiling_token):
        lb_template = self.get_leaderboard_template_by_id(
            profiling_token, lb_template_id)
        return lb_template or {}

    def _get_details(self, task_id, profiling_token):
        return self.get_leaderboard_template_details(profiling_token, task_id)

    def edit(self, task_id, profiling_token, **kwargs):
        self.check_task(task_id, profiling_token)
        try:
            self.update_leaderboard_template(profiling_token, task_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, ['Task', task_id])
            raise
        return self.get(task_id, profiling_token)

    def delete(self, task_id, profiling_token):
        try:
            self.delete_leaderboard_template(profiling_token, task_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, ['Task', task_id])
            raise


class LeaderboardTemplateAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return LeaderboardTemplateController
