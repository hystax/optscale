import json
from rest_api.rest_api_server.controllers.profiling.optimization import (
    TaskOptimizationAsyncController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v2.profiling.base import ProfilingHandler
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import (NotFoundException,
                                                  WrongArgumentsException)


class TaskOptimizationsAsyncHandler(BaseAsyncItemHandler,
                                    BaseAuthHandler, ProfilingHandler):
    def _get_controller_class(self):
        return TaskOptimizationAsyncController

    async def get(self, organization_id, task_id, **kwargs):
        """
        ---
        description: |
            Get task optimizations info by task id
            Required permission: INFO_ORGANIZATION
        tags: [profiling_optimizations]
        summary: Get task recommendations
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
        -   name: type
            type: array
            in: query
            items:
                type: string
            collectionFormat: multi
            description: Types for which details must be returned
            required: false
        -   name: status
            in: query
            description: |
                Return active, dismissed or excluded recommendations details.
                Required together with type parameter
            required: false
            type: string
            default: active
            enum: [active, dismissed, excluded]
        responses:
            200:
                description: Task optimizations list
                schema:
                    type: object
                    properties:
                        total_saving: {type: number, description:
                            "Saving value"}
                        total_count: {type: number, description:
                            "total optimizations count"}
                        optimizations:
                            type: object
                            properties:
                                short_living_instances:
                                    type: object
                                    properties:
                                        count: {type: integer, description:
                                            "Optimization objects count"}
                                        saving: {type: number, description:
                                            "Optimization saving"}
                                        limit: {type: integer, description:
                                            "Max objects amount (limit applied)"}
                                        items:
                                            type: array
                                            description: >
                                                Short living instances objects
                                                if short_living_instances type specified
                                            items:
                                                type: object
                                                properties:
                                                    cloud_resource_id: {type: string, description:
                                                        "Cloud instance id"}
                                                    resource_name: {type: string, description:
                                                        "Instance name"}
                                                    cloud_account_id: {type: string, description:
                                                        "Cloud account id"}
                                                    cloud_account_name: {type: string, description:
                                                        "Cloud account name"}
                                                    resource_id: {type: string, description:
                                                        "Instance id"}
                                                    cloud_type: {type: string, description:
                                                        "Cloud type"}
                                                    total_cost: {type: integer, description:
                                                        "Instance lifetime cost"}
                                                    first_seen: {type: integer, description:
                                                        "Instance first appearance in timestamp format"}
                                                    last_seen: {type: integer, description:
                                                        "Instance last appearance in timestamp format"}
                                                    saving: {type: number, description:
                                                        "Savings number"}
                                        options:
                                            type: object
                                            description: >
                                                Short living instances running options
                                                if short_living_instances type specified
                                            properties:
                                                days_threshold:
                                                    type: integer
                                                    description: Days threshold
                                                excluded_pools:
                                                    type: object
                                                    description: Pools exclusion map
                                                skip_cloud_accounts:
                                                    type: array
                                                    items:
                                                        type: string
                                                        description: Cloud account id to skip
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0217: Invalid query parameter
                    - OE0460: Status should be active, dismissed or excluded
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
                    - OE0002: Item not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        try:
            await self._get_item(organization_id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        try:
            types = self.get_arg('type', str, [], repeated=True)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        status = self.get_arg('status', str)
        if types:
            if status is None:
                status = 'active'
            elif status not in ['active', 'dismissed', 'excluded']:
                raise OptHTTPError(400, Err.OE0460, [])
        elif status:
            raise OptHTTPError(400, Err.OE0212, ['status'])
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.get_optimizations,
                             organization_id, task_id, token,
                             types, status)
        self.write(json.dumps(res, cls=ModelEncoder))

    def patch(self, organization_id, task_id, **kwargs):
        self.raise405()

    def delete(self, organization_id, task_id, **kwargs):
        self.raise405()
