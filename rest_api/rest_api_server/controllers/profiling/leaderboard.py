import logging
from requests.exceptions import HTTPError

from tools.optscale_exceptions.common_exc import (
    NotFoundException)

from rest_api.rest_api_server.controllers.profiling.base import format_dataset
from rest_api.rest_api_server.controllers.profiling.leaderboard_template import (
    LeaderboardTemplateController)
from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.exceptions import Err


LOG = logging.getLogger(__name__)


class LeaderboardController(LeaderboardTemplateController):
    @property
    def model_name(self):
        return 'Leaderboard'

    def create(self, leaderboard_template_id, profiling_token, **kwargs):
        try:
            leaderboard = self.create_leaderboard(
                profiling_token, leaderboard_template_id, **kwargs)
            return leaderboard
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Leaderboard template',
                                 leaderboard_template_id])
            raise

    def get(self, leaderboard_id, profiling_token, details=False):
        try:
            leaderboard = self.get_leaderboard(profiling_token, leaderboard_id)
            datasets = leaderboard.get('datasets')
            if datasets:
                for i, dataset in enumerate(datasets):
                    datasets[i] = format_dataset(dataset)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, [self.model_name, leaderboard_id])
            raise
        if details:
            leaderboard_details = self._get_details(
                leaderboard_id, profiling_token)
            leaderboard['details'] = leaderboard_details
        metrics_map = self.get_metrics(profiling_token, leaderboard,
                                       raise_exc=False)
        return self.format_leaderboard_template(leaderboard, metrics_map)

    def _get_details(self, leaderboard_id, profiling_token):
        resp = self.get_leaderboard_details(
            profiling_token, leaderboard_id)
        return resp

    def edit(self, leaderboard_id, profiling_token, **kwargs):
        try:
            self.update_leaderboard(profiling_token, leaderboard_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, [self.model_name,
                                                     leaderboard_id])
            raise
        return self.get(leaderboard_id, profiling_token)

    def delete(self, leaderboard_id, profiling_token):
        try:
            self.delete_leaderboard(profiling_token, leaderboard_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, [self.model_name, leaderboard_id])
            raise

    def generate(self, leaderboard_id, profiling_token):
        try:
            return self.generate_leaderboard(profiling_token, leaderboard_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, [self.model_name, id])
            raise

    def list(self, leaderboard_template_id, profiling_token):
        try:
            return self.list_leaderboard(
                profiling_token, leaderboard_template_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, [self.model_name, id])
            raise


class LeaderboardAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return LeaderboardController
