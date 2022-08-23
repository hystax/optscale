import json

from rest_api_server.controllers.limit_hit import LimitHitsAsyncController
from rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.models.enums import LimitHitsSelector
from rest_api_server.utils import run_task, ModelEncoder


class LimitHitsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                      BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return LimitHitsAsyncController

    def _get_selection_type(self):
        raise NotImplementedError()

    async def get(self, object_id):
        res = await run_task(self.controller.list, object_id,
                             selection_type=self._get_selection_type())
        limit_hits_dict = {'limit_hits': [limit_hit.to_dict()
                                          for limit_hit in res]}
        self.write(json.dumps(limit_hits_dict, cls=ModelEncoder))


class PoolLimitHitsAsyncCollectionHandler(LimitHitsAsyncCollectionHandler):
    def _get_controller_class(self):
        return LimitHitsAsyncController

    def _get_selection_type(self):
        return LimitHitsSelector.pool_id

    async def get(self, pool_id):
        """
        ---
        description: |
            Get list of constraint limit hits of pool resources
            Required permission: MANAGE_POOLS
        tags: [constraint_limit_hits]
        summary: List of constraint limit hits
        parameters:
        -   name: pool_id
            in: path
            description: Pool id
            required: true
            type: string
        responses:
            200:
                description: Constraint limit hits list
                schema:
                    type: object
                    properties:
                        limit_hits:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string, description:
                                        "Unique limit hit id"}
                                    deleted_at: {type: integer, description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer, description:
                                        "Created timestamp (service field)"}
                                    pool_id: {type: string, description:
                                        "Resource pool at the moment of hit"}
                                    resource_id: {type: string,
                                        description: "Id of violated resource"}
                                    type: {type: string, description:
                                        "Constraint type"}
                                    time: {type: integer, description:
                                        "Violation time timestamp"}
                                    constraint_limit: {type: integer, description:
                                        "Violated value"}
                                    ttl_value: {type: integer, description:
                                        "Timestamp that violated constraint (only for TTL constraint)"}
                                    expense_value: {type: float, description:
                                        "Value that violated constraint (only for expense constraint)"}
                                    state: {type: string, description:
                                        "Constraint current state"}
            404:
                description: |
                    Not found:
                    - OE0002: Pool not found
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
        security:
        - token: []
        """
        await self.check_permissions('MANAGE_POOLS', 'pool', pool_id)
        await super().get(pool_id)


class RecourceLimitHitsAsyncItemHandler(LimitHitsAsyncCollectionHandler):
    def _get_controller_class(self):
        return LimitHitsAsyncController

    def _get_selection_type(self):
        return LimitHitsSelector.resource_id

    async def get(self, resource_id):
        """
        ---
        description: |
            Get list of constraint limit hits of resource
            Required permission: INFO_ORGANIZATION
        tags: [constraint_limit_hits]
        summary: List of constraint limit hits
        parameters:
        -   name: resource_id
            in: path
            description: Resource id
            required: true
            type: string
        responses:
            200:
                description: Constraint limit hits list
                schema:
                    type: object
                    properties:
                        limit_hits:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string, description:
                                        "Unique limit hit id"}
                                    deleted_at: {type: integer, description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer, description:
                                        "Created timestamp (service field)"}
                                    pool_id: {type: string, description:
                                        "Resource pool at the moment of hit"}
                                    resource_id: {type: string,
                                        description: "Id of violated resource"}
                                    type: {type: string, description:
                                        "Constraint type"}
                                    time: {type: integer, description:
                                        "Violation time timestamp"}
                                    constraint_limit: {type: integer, description:
                                        "Violated value"}
                                    ttl_value: {type: integer, description:
                                        "Timestamp that violated constraint (only for TTL constraint)"}
                                    expense_value: {type: float, description:
                                        "Value that violated constraint (only for expense constraint)"}
                                    state: {type: string, description:
                                        "Constraint current state"}
            404:
                description: |
                    Not found:
                    - OE0002: Resource not found
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
        security:
        - token: []
        """
        await self.check_permissions(
                'INFO_ORGANIZATION', 'cloud_resource', resource_id)
        await super().get(resource_id)
