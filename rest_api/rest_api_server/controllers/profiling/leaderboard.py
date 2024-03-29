import logging
from requests.exceptions import HTTPError

from tools.optscale_exceptions.common_exc import (
    NotFoundException, ConflictException)

from rest_api.rest_api_server.controllers.profiling.base import (
    BaseProfilingController)
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.exceptions import Err

LOG = logging.getLogger(__name__)


class LeaderboardController(BaseProfilingController):
    @property
    def model_name(self):
        return 'Leaderboard'

    def get_metrics(self, profiling_token, leaderboard, raise_exc=True):
        metrics_ids = [leaderboard['primary_metric']] + leaderboard.get(
            'other_metrics', [])
        existing_metrics = self.list_metrics(profiling_token)
        not_exist = set(metrics_ids) - set(x['id'] for x in existing_metrics)
        if not_exist and raise_exc:
            message = ', '.join(not_exist)
            raise NotFoundException(Err.OE0002, ['Metric', message])
        return {x['id']: x for x in existing_metrics if x['id'] in metrics_ids}

    @staticmethod
    def format_leaderboard(leaderboard, metrics_map):
        for filter_ in leaderboard['filters']:
            filter_metric = metrics_map.get(filter_['id'])
            if filter_metric:
                filter_['name'] = filter_metric.get('name')
        primary_metric = metrics_map.pop(
            leaderboard['primary_metric'], None)
        leaderboard['primary_metric'] = primary_metric
        leaderboard['other_metrics'] = list(metrics_map.values())
        return leaderboard

    def create(self, task_id, profiling_token, **kwargs):
        self.check_task(task_id, profiling_token)
        try:
            metrics_map = self.get_metrics(profiling_token, kwargs)
            leaderboard = self.create_leaderboard(profiling_token,
                                                  task_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 409:
                raise ConflictException(Err.OE0549, [task_id])
            raise
        return self.format_leaderboard(leaderboard, metrics_map)

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
        leaderboard = self.get_leaderboard(profiling_token, task_id)
        if leaderboard:
            metrics_map = self.get_metrics(profiling_token, leaderboard,
                                           raise_exc=False)
            leaderboard = self.format_leaderboard(leaderboard, metrics_map)
            if details:
                leaderboard['details'] = self._get_details(
                    task_id, profiling_token)
        return leaderboard or {}

    def _get_details(self, task_id, profiling_token):
        return self.get_leaderboard_details(profiling_token, task_id)

    def edit(self, task_id, profiling_token, **kwargs):
        self.check_task(task_id, profiling_token)
        try:
            self.update_leaderboard(profiling_token, task_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, [self.model_name,
                                                     task_id])
        return self.get(task_id, profiling_token)

    def delete(self, task_id, profiling_token):
        try:
            self.delete_leaderboard(profiling_token, task_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, [self.model_name, id])
            raise


class LeaderboardAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return LeaderboardController
