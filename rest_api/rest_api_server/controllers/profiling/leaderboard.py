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

    def get_goals(self, profiling_token, leaderboard, raise_exc=True):
        goals_ids = [leaderboard['primary_goal']] + leaderboard.get(
            'other_goals', [])
        existing_goals = self.list_goals(profiling_token)
        not_exist = set(goals_ids) - set(x['id'] for x in existing_goals)
        if not_exist and raise_exc:
            message = ', '.join(not_exist)
            raise NotFoundException(Err.OE0002, ['Goal', message])
        return {x['id']: x for x in existing_goals if x['id'] in goals_ids}

    @staticmethod
    def format_leaderboard(leaderboard, goals_map):
        for filter_ in leaderboard['filters']:
            filter_goal = goals_map.get(filter_['id'])
            if filter_goal:
                filter_['name'] = filter_goal.get('name')
        primary_metric = goals_map.pop(
            leaderboard['primary_goal'], None)
        leaderboard['primary_goal'] = primary_metric
        leaderboard['other_goals'] = list(goals_map.values())
        return leaderboard

    def create(self, application_id, profiling_token, **kwargs):
        self.check_application(application_id, profiling_token)
        try:
            goals_map = self.get_goals(profiling_token, kwargs)
            leaderboard = self.create_leaderboard(profiling_token,
                                                  application_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 409:
                raise ConflictException(Err.OE0549, [application_id])
            raise
        return self.format_leaderboard(leaderboard, goals_map)

    def check_application(self, application_id, profiling_token):
        try:
            self.get_application(profiling_token, application_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002,
                                        ['Application', application_id])
            raise

    def get(self, application_id, profiling_token, details=False):
        self.check_application(application_id, profiling_token)
        leaderboard = self.get_leaderboard(profiling_token, application_id)
        if leaderboard:
            goals_map = self.get_goals(profiling_token, leaderboard,
                                       raise_exc=False)
            leaderboard = self.format_leaderboard(leaderboard, goals_map)
            if details:
                leaderboard['details'] = self._get_details(
                    application_id, profiling_token)
        return leaderboard or {}

    def _get_details(self, application_id, profiling_token):
        return self.get_leaderboard_details(profiling_token, application_id)

    def edit(self, application_id, profiling_token, **kwargs):
        self.check_application(application_id, profiling_token)
        try:
            self.update_leaderboard(profiling_token, application_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, [self.model_name,
                                                     application_id])
        return self.get(application_id, profiling_token)

    def delete(self, application_id, profiling_token):
        try:
            self.delete_leaderboard(profiling_token, application_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, [self.model_name, id])
            raise


class LeaderboardAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return LeaderboardController
