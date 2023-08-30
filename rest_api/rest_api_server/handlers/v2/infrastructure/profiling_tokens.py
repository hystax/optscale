from rest_api.rest_api_server.controllers.infrastructure.profiling_token import (
    InfraProfilingTokenAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task

from tools.optscale_exceptions.common_exc import NotFoundException
from tools.optscale_exceptions.http_exc import OptHTTPError


class InfraProfilingTokenAsyncCollectionHandler(BaseAsyncItemHandler,
                                                BaseAuthHandler):
    def _get_controller_class(self):
        return InfraProfilingTokenAsyncController

    def patch(self, *args, **kwargs):
        self.raise405()

    def delete(self, *args, **kwargs):
        self.raise405()

    async def get(self, infrastructure_token, **url_params):
        """
        ---
        description: |
            Get profiling token by infrastructure_token
            Required permission: CLUSTER_SECRET
        tags: [profiling_tokens]
        summary: Get profiling token by infrastructure_token
        parameters:
        -   name: infrastructure_token
            in: path
            description: Infrastructure token
            required: true
            type: string
        responses:
            200:
                description: Profiling token
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Unique profiling token id
                        token:
                            type: string
                            description: Profiling token
                        organization_id:
                            type: string
                            description: Organization id
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0527: Infrastructure token not found
        security:
        - secret: []
        """
        self.check_cluster_secret(raises=True)
        try:
            res = await run_task(
                self.controller.get,
                infrastructure_token=infrastructure_token)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.write(res.to_json())
