import json

from rest_api.rest_api_server.controllers.infrastructure.runner import (
    RunnerAsyncController)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder
from rest_api.rest_api_server.handlers.v2.infrastructure.base import (
    InfrastructureHandler)


class RunnersAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                    BaseAuthHandler,
                                    InfrastructureHandler):
    def _get_controller_class(self):
        return RunnerAsyncController

    async def post(self, *args, **kwargs):
        self.raise405()

    async def get(self, organization_id, runset_id, **url_params):
        """
        ---
        description: |
            Get list of runset runners
            Required permission: INFO_ORGANIZATION
        tags: [infrastructure_runners]
        summary: List of runset runners
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: runset_id
            in: path
            description: Runset id
            required: true
            type: string
        responses:
            200:
                description: Runset runners list
                schema:
                    type: object
                    properties:
                        runners:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: Unique runner id
                                    runset_id:
                                        type: string
                                        description: Runset id
                                    return_code:
                                        type: integer
                                        description: Runner return code
                                    error_reason:
                                        type: string
                                        description: |
                                            Runner error reason (if return code != 0)
                                    instance_id:
                                        type: string
                                        description: Runner instance id
                                    instance_name:
                                        type: string
                                        description: Runner instance name
                                    created_at:
                                        type: integer
                                        description: Created timestamp (service field)
                                    started_at:
                                        type: integer
                                        description: Runner start timestamp
                                    destroyed_at:
                                        type: integer
                                        description: Runner destroy timestamp
                                    state:
                                        type: string
                                        enum: [starting scheduled, starting preparing,
                                            starting, started, destroying scheduled,
                                            destroy preparing, destroying,
                                            destroyed, error, waiting arcee, unknown]
                                        description: Runner state
                                    cloud_account:
                                        type: object
                                        properties:
                                            id:
                                                type: string
                                                description: Cloud account id
                                            name:
                                                type: string
                                                description: Cloud account name
                                            type:
                                                type: string
                                                description: Cloud type
                                    instance_type:
                                        type: object
                                        properties:
                                            name:
                                                type: string
                                                description: Instance type name
                                            type:
                                                type: string
                                                description: Cloud type
                                    region:
                                        type: object
                                        properties:
                                            id:
                                                type: string
                                                description: Region id
                                            name:
                                                type: string
                                                description: Region name
                                            type:
                                                type: string
                                                description: Cloud type
                                    duration:
                                        type: integer
                                        description: |
                                            Runner duration since start till destroy
                                    cost:
                                        type: number
                                        description: Runner cost
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
        token = await self._get_infrastructure_token(organization_id)
        res = await run_task(self.controller.list,
                             organization_id, runset_id, token)
        runners_dict = {'runners': res}
        self.write(json.dumps(runners_dict, cls=ModelEncoder))
