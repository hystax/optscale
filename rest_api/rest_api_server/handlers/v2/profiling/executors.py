import json
from rest_api.rest_api_server.utils import run_task, ModelEncoder
from rest_api.rest_api_server.controllers.profiling.executor import ExecutorAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v2.profiling.base import ProfilingHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler


class ExecutorAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                     BaseAuthHandler, ProfilingHandler):
    def _get_controller_class(self):
        return ExecutorAsyncController

    def post(self, *args, **kwargs):
        self.raise405()

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get list of application executors
            Required permission: INFO_ORGANIZATION
        tags: [profiling_executors]
        summary: List of application executors
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: application_id
            in: query
            description: Application id
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
        responses:
            200:
                description: Application executors
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
                                            Unique organization application id
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
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        application_ids = self.get_arg('application_id', str, repeated=True)
        run_ids = self.get_arg('run_id', str, repeated=True)
        res = await run_task(
            self.controller.list, organization_id, application_ids, token,
            run_ids=run_ids
        )
        applications_dict = {'executors': res}
        self.write(json.dumps(applications_dict, cls=ModelEncoder))


class ExecutorBreakdownAsyncCollectionHandler(ExecutorAsyncCollectionHandler,
                                              ProfilingHandler):
    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Breakdown of application executors
            Required permission: INFO_ORGANIZATION
        tags: [profiling_executors]
        summary: Application executors breakdown
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: breakdown_by
            in: query
            description: Breakdown by
            required: true
            type: string
            enum: ['executors_count', 'cpu', 'ram', 'process_cpu', 'process_ram',
                'gpu_load', 'gpu_memory_free', 'gpu_memory_total',
                'gpu_memory_used']
        responses:
            200:
                description: Executors breakdown
                schema:
                    type: object
                    properties:
                        breakdown:
                            type: object
                            description: breakdown by day
                            example:
                                1640995200: 24
                                1641168000: 32
                        breakdown_by:
                            type: string
                            description: applied breakdown_by filter
                            example: executors_count
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
        breakdown_by = self.get_arg('breakdown_by', str)
        if breakdown_by is None:
            raise OptHTTPError(400, Err.OE0216, ['breakdown_by'])
        allowed_breakdowns = [
            'executors_count', 'cpu', 'ram', 'process_cpu', 'process_ram',
            'gpu_load', 'gpu_memory_free', 'gpu_memory_total',
            'gpu_memory_used'
        ]
        if breakdown_by not in allowed_breakdowns:
            raise OptHTTPError(400, Err.OE0217, ['breakdown_by'])
        token = await self._get_profiling_token(organization_id)
        res = await run_task(
            self.controller.breakdown_get, breakdown_by, token)
        self.write(json.dumps(res, cls=ModelEncoder))
