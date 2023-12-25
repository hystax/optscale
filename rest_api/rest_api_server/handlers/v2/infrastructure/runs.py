import json

from rest_api.rest_api_server.controllers.infrastructure.run import RunAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.infrastructure.base import (
    InfrastructureHandler)
from rest_api.rest_api_server.utils import run_task, ModelEncoder


class RunAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                BaseAuthHandler,
                                InfrastructureHandler):
    def _get_controller_class(self):
        return RunAsyncController

    def post(self, *args, **kwargs):
        self.raise405()

    async def get(self, organization_id, runset_id, **url_params):
        """
        ---
        description: |
            Get list of runset runs
            Required permission: INFO_ORGANIZATION
        tags: [infrastructure_runs]
        summary: List of runset runs
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
                description: List of runset runs
                schema:
                    type: object
                    properties:
                        runs:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: Run id
                                    application_id:
                                        type: string
                                        description: Application id
                                    name:
                                        type: string
                                        description: Run name
                                    start:
                                        type: integer
                                        description: Start time
                                    finish:
                                        type: integer
                                        description: End time
                                    duration:
                                        type: integer
                                        description: Run duration
                                    state:
                                        type: integer
                                        description: Run state
                                        enum: [1, 2, 3, 4]
                                    status:
                                        type: string
                                        description: Run status
                                        enum: [running, completed, failed, aborted]
                                    number:
                                        type: integer
                                        description: Number of run
                                    tags:
                                        type: object
                                        description: Run tags
                                    data:
                                        type: object
                                        description: Run data
                                    imports:
                                        type: array
                                        description: Array of imports
                                        items:
                                            type: string
                                    executors:
                                        type: array
                                        description: List of run executors
                                        items:
                                            type: object
                                            properties:
                                                id:
                                                    type: string
                                                    description: Executor id
                                                platform_type:
                                                    type: string
                                                    description: Platform type
                                                instance_id:
                                                    type: string
                                                    description: Instance id
                                                instance_type:
                                                    type: string
                                                    description: Instance type
                                                total_cost:
                                                    type: number
                                                    description: Executor cost
                                    hyperparameters:
                                        type: object
                                        description: Run hyperparameters
                                    goals:
                                        type: array
                                        description: List of application goals
                                        items:
                                            type: object
                                            properties:
                                                id:
                                                    type: string
                                                    description: Goal id
                                                name:
                                                    type: string
                                                    description: Goal name
                                                key:
                                                    type: string
                                                    description: Goal key
                                                tendency:
                                                    type: string
                                                    description: Tendency
                                                func:
                                                    type: string
                                                    description: Func
                                                target_value:
                                                    type: number
                                                    description: Goal target value
                                    runset:
                                        type: object
                                        description: Runset object
                                    dataset:
                                        type: object
                                        description: Dataset object
                                    git:
                                        type: object
                                        description: Git object
                                    command:
                                        type: string
                                        description: |
                                            Command with which instrumented
                                            program has been launched

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
        res = await run_task(
            self.controller.list, organization_id, runset_id, token)
        runs_dict = {'runs': res}
        self.write(json.dumps(runs_dict, cls=ModelEncoder))
