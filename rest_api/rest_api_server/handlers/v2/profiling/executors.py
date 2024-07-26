import json
from rest_api.rest_api_server.utils import run_task, ModelEncoder
from rest_api.rest_api_server.controllers.profiling.executor import (
    ExecutorAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api.rest_api_server.handlers.v2.profiling.base import ProfilingHandler
from rest_api.rest_api_server.handlers.v1.base import (
    BaseAuthHandler, BaseAuthQueryTokenHandler)


class ExecutorAsyncCollectionHandler(
        BaseAsyncCollectionHandler, BaseAuthQueryTokenHandler,
        ProfilingHandler):

    def _get_controller_class(self):
        return ExecutorAsyncController

    def post(self, *args, **kwargs):
        self.raise405()

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get list of task executors
            Required permission: INFO_ORGANIZATION
        tags: [profiling_executors]
        summary: List of task executors
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: task_id
            in: query
            description: Task id
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: run_id
            in: query
            description: Run id
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: token
            in: query
            description: |
                Unique token related to organization profiling token (only
                with run_id)
            required: false
            type: string
        responses:
            200:
                description: Task executors
                schema:
                    type: object
                    properties:
                        executors:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: |
                                            Unique organization task id
                                    platform_type:
                                        type: string
                                        description: |
                                            platform type
                                    platform_type:
                                        type: string
                                        description: |
                                            platform type
                                    instance_id:
                                        type: string
                                        description: |
                                            instance id
                                    account_id:
                                        type: string
                                        description: |
                                            account id
                                    local_ip:
                                        type: string
                                        description: |
                                            local ip address
                                    public_ip:
                                        type: string
                                        description: |
                                            public ip address
                                    instance_region:
                                        type: string
                                        description: |
                                            instance region
                                    instance_type:
                                        type: string
                                        description: |
                                            instance type
                                    last_seen:
                                        type: string
                                        description: |
                                            Executor last seen
                                    cloud_account:
                                        type: object
                                        properties:
                                            id:
                                                type: string
                                                description: cloud account id
                                            name:
                                                type: string
                                                description: cloud account name
                                            type:
                                                type: string
                                                description: cloud type
                                    cloud_resource_id:
                                        type: string
                                        description: |
                                            Cloud resource id
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
                    - OE0002: Organization not found
        security:
        - token: []
        """
        token = self.get_arg('token', str)
        run_ids = self.get_arg('run_id', str, repeated=True)
        if not await self.check_md5_profiling_token(
                organization_id, token, raises=False) or not run_ids:
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        task_ids = self.get_arg('task_id', str, repeated=True)
        res = await run_task(
            self.controller.list, organization_id, task_ids, token,
            run_ids=run_ids
        )
        tasks_dict = {'executors': res}
        self.write(json.dumps(tasks_dict, cls=ModelEncoder))


class ExecutorBreakdownAsyncCollectionHandler(
        BaseAsyncCollectionHandler, BaseAuthHandler, ProfilingHandler):

    def _get_controller_class(self):
        return ExecutorAsyncController

    def post(self, *args, **kwargs):
        self.raise405()

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Breakdown of task executors
            Required permission: INFO_ORGANIZATION
        tags: [profiling_executors]
        summary: Task executors breakdown
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Executors breakdown
                schema:
                    type: object
                    properties:
                        breakdown:
                            type: object
                            example:
                                1640995200: 24
                                1641168000: 32
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
                    - OE0002: Organization not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(
            self.controller.breakdown_get, token)
        self.write(json.dumps(res, cls=ModelEncoder))
