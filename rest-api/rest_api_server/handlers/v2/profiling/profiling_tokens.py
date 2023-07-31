from rest_api_server.controllers.profiling.profiling_token import (
    ProfilingTokenAsyncController)
from rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task


class ProfilingTokenAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                           BaseAuthHandler):
    def _get_controller_class(self):
        return ProfilingTokenAsyncController

    async def post(self, organization_id, **url_params):
        self.raise405()

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get list of organization profiling tokens
            Required permission: INFO_ORGANIZATION
        tags: [profiling_tokens]
        summary: List of organization profiling tokens
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Organization profiling tokens list
                schema:
                    type: object
                    properties:
                        profiling_tokens:
                            type: array
                            items:
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
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        res = await run_task(self.controller.get,
                             organization_id=organization_id)
        self.write(res.to_json())
