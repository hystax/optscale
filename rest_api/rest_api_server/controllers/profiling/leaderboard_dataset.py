import logging
from requests.exceptions import HTTPError

from tools.optscale_exceptions.common_exc import (
    NotFoundException)

from rest_api.rest_api_server.controllers.profiling.base import format_dataset
from rest_api.rest_api_server.controllers.profiling.leaderboard import (
    LeaderboardController)
from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.exceptions import Err


LOG = logging.getLogger(__name__)


class LeaderboardDatasetController(LeaderboardController):
    @property
    def model_name(self):
        return 'LeaderboardDataset'

    def create(self, leaderboard_id, profiling_token, **kwargs):
        try:
            leaderboard_dataset = self.create_leaderboard_dataset(
                profiling_token, leaderboard_id, **kwargs)
            return leaderboard_dataset
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Leaderboard', leaderboard_id])
            raise

    def get(self, leaderboard_dataset_id, profiling_token, details=False):
        try:
            leaderboard_dataset = self.get_leaderboard_dataset(
                profiling_token, leaderboard_dataset_id)
            datasets = leaderboard_dataset.get('datasets')
            if datasets:
                for i, dataset in enumerate(datasets):
                    datasets[i] = format_dataset(dataset)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, [self.model_name, leaderboard_dataset_id])
            raise
        if details:
            leaderboard_dataset_details = self._get_details(
                leaderboard_dataset_id, profiling_token)
            leaderboard_dataset['details'] = leaderboard_dataset_details
        metrics_map = self.get_metrics(profiling_token, leaderboard_dataset,
                                       raise_exc=False)
        return self.format_leaderboard(leaderboard_dataset, metrics_map)

    def _get_details(self, leaderboard_dataset_id, profiling_token):
        resp = self.get_leaderboard_dataset_details(
            profiling_token, leaderboard_dataset_id)
        return resp

    def edit(self, leaderboard_dataset_id, profiling_token, **kwargs):
        try:
            self.update_leaderboard_dataset(
                profiling_token, leaderboard_dataset_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, [self.model_name,
                                                     leaderboard_dataset_id])
            raise
        return self.get(leaderboard_dataset_id, profiling_token)

    def delete(self, leaderboard_dataset_id, profiling_token):
        try:
            self.delete_leaderboard_dataset(
                profiling_token, leaderboard_dataset_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, [self.model_name, id])
            raise

    def generate(self, leaderboard_dataset_id, profiling_token):
        try:
            return self.generate_leaderboard(
                profiling_token, leaderboard_dataset_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, [self.model_name, id])
            raise

    def list(self, leaderboard_id, profiling_token):
        try:
            return self.list_leaderboard_dataset(
                profiling_token, leaderboard_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, [self.model_name, id])
            raise


class LeaderboardDatasetAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return LeaderboardDatasetController
