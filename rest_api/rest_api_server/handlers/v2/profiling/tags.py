import json

from rest_api.rest_api_server.handlers.v2.profiling.labels import (
    LabelsAsyncCollectionHandler
)
from rest_api.rest_api_server.controllers.profiling.tag import (
    TagAsyncController)
from rest_api.rest_api_server.utils import run_task, ModelEncoder


class TagsAsyncCollectionHandler(LabelsAsyncCollectionHandler):

    def _get_controller_class(self):
        return TagAsyncController

    async def get(self, organization_id, task_id, **url_params):
        """
        ---
        description: |
            List runs tags
            Required permission: INFO_ORGANIZATION
        tags: [profiling_tags]
        summary: List tags
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: task_id
            in: path
            description: Task id
            required: true
            type: string
        responses:
            200:
                description: Task tags list
                schema:
                    type: object
                    properties:
                        tags:
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
        res = await run_task(self.controller.list, token, task_id)
        self.write(json.dumps({'tags': res}, cls=ModelEncoder))

    async def post(self, **url_params):
        self.raise405()
