from requests.exceptions import HTTPError

from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.profiling.base import (
    BaseProfilingController)
from rest_api.rest_api_server.exceptions import Err

from tools.optscale_exceptions.common_exc import NotFoundException


class ArtifactController(BaseProfilingController):

    def create(self, profiling_token, **kwargs):
        try:
            artifact = self.create_artifact(profiling_token, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Run', kwargs['run_id']])
            raise
        return artifact

    def get(self, artifact_id, profiling_token):
        try:
            artifact = self.get_artifact(profiling_token, artifact_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Artifact', artifact_id])
            raise
        return artifact

    def list(self, profiling_token, **kwargs):
        artifacts = self.list_artifacts(profiling_token, **kwargs)
        return artifacts

    def edit(self, artifact_id, profiling_token, **kwargs):
        try:
            self.update_artifact(profiling_token, artifact_id, **kwargs)
        except HTTPError as exc:
            if exc.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Artifact', artifact_id])
            raise
        return self.get(artifact_id, profiling_token)

    def delete(self, artifact_id, profiling_token):
        try:
            self.delete_artifact(profiling_token, artifact_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Artifact', artifact_id])
            raise


class ArtifactAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ArtifactController
