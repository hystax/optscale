import json

from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler)
from rest_api.rest_api_server.controllers.profiling.label import (
    LabelAsyncController)
from rest_api.rest_api_server.utils import run_task, ModelEncoder
from rest_api.rest_api_server.handlers.v2.profiling.base import (
    ProfilingHandler)


class LabelsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                   BaseAuthHandler,
                                   ProfilingHandler):

    def _get_controller_class(self):
        return LabelAsyncController

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            List labels
            Required permission: INFO_ORGANIZATION
        tags: [profiling_labels]
        summary: List labels
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Labels list
                schema:
                    type: object
                    properties:
                        labels:
                            type: array
                            items:
                                type: string
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
                    - OE0543: External unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.list, token)
        datasets_dict = {'labels': res}
        self.write(json.dumps(datasets_dict, cls=ModelEncoder))

    async def post(self, **url_params):
        self.raise405()
