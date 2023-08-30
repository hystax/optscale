import json

from rest_api.rest_api_server.controllers.pool_policy import (
    PoolPolicyAsyncController, PoolPolicyOrganizationAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder


class PoolPoliciesAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                         BaseAuthHandler):

    def _get_controller_class(self):
        return PoolPolicyAsyncController

    async def post(self, pool_id, **url_params):
        """
        ---
        description: |
            Create policy for pool
            Required permission: MANAGE_POOLS
        tags: [pool_policies]
        summary: Create policy for pool
        parameters:
        -   name: pool_id
            in: path
            description: Pool id
            required: true
            type: string
        -   in: body
            name: body
            description: Policy info to add
            required: true
            schema:
                type: object
                properties:
                    limit:
                        type: integer
                        description: "violation limit"
                        required: True
                        example: 80
                    type:
                        type: string
                        required: False
                        description: "Constraint type ('ttl', 'total_expense_limit', 'daily_expense_limit')"
                        example: 'ttl'
                    active:
                        type: boolean
                        required: False
                        default: True
                        description: "active flag"
                        example: True
        responses:
            201:
                description: Created (returns created policy)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        type: ttl
                        active: True
                        limit: 300
                        created_at: 1587029026
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0004: "type" is not a valid ConditionTypes
                    - OE0216: Argument not provided
                    - OE0214: Argument should be a string
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0233: Incorrect body received
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
                    - OE0456: Duplicate path parameters in the request body
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Pool not found
            409:
                description: |
                    Conflict:
                    - OE0440: Policy with type already exists for pool
        security:
        - token: []
        """
        await self.check_permissions('MANAGE_POOLS', 'pool', pool_id)
        await super().post(pool_id=pool_id, **url_params)

    async def get(self, pool_id):
        """
        ---
        description: |
            Get list of policies for pool
            Required permission: INFO_ORGANIZATION
        tags: [pool_policies]
        summary: List of policies for pool
        parameters:
        -   in: path
            name: pool_id
            description: id of the pool
            required: true
        responses:
            200:
                description: policies list
                schema:
                    type: object
                    example:
                        policies:
                            type: array
                            items:
                                type: object
                            example:
                                -   id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                                    pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                    type: ttl
                                    active: True
                                    limit: 300
                                    created_at: 1587029026
                                    deleted_at: 0
                                -   id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                                    pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                    type: total_expense_limit
                                    active: False
                                    limit: 1000
                                    created_at: 1587029026
                                    deleted_at: 0
                                -   id: 1bca7ecb-e5e7-4982-81c3-c1a37bc921c9
                                    resource_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                    type: daily_expense_limit
                                    active: False
                                    limit: 500
                                    created_at: 1587029026
                                    deleted_at: 0
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Pool not found
        security:
        - token: []
        """
        await self.check_permissions('INFO_ORGANIZATION', 'pool', pool_id)
        res = await run_task(self.controller.list, pool_id=pool_id)
        policies = {'policies': [policy.to_dict() for policy in res]}
        self.write(json.dumps(policies, cls=ModelEncoder))


class OrganizationPoliciesAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                                 BaseAuthHandler, BaseHandler):

    def _get_controller_class(self):
        return PoolPolicyOrganizationAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of policies for organization
            Required permission: INFO_ORGANIZATION
        tags: [global_constraints]
        summary: List of policies for organization
        parameters:
        -   in: path
            name: organization_id
            description: id of the organization
            required: true
        -   name: details
            in: query
            type: boolean
            description: Pool info for policy
            required: false
        responses:
            200:
                description: Policy list
                schema:
                    type: object
                    properties:
                        resource_policies:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description:
                                        "Unique pool policy id"}
                                    created_at: {type: integer,
                                        description:
                                        "Created timestamp (service field)"}
                                    deleted_at: {type: integer,
                                        description:
                                        "Deleted timestamp (service field)"}
                                    type: {type: string,
                                        description: "Constraint type:
                                        ('TTL','DAILY_EXPENSE_LIMIT')"}
                                    limit: {type: integer,
                                        description:
                                        "Constraint limit"}
                                    active: {type: boolean,
                                        description: "Is policy active"}
                                    pool_id: {type: string,
                                        description: "Pool id"}
                                    organization_id: {type: string,
                                        description: "Organization id"}
                                    details:
                                        type: object
                                        properties:
                                            id: {type: string,
                                                description: Unique pool id}
                                            created_at: {type: integer,
                                                description: created timestamp}
                                            deleted_at: {type: integer,
                                                description: deleted timestamp}
                                            limit: {type: integer,
                                                description: pool limit}
                                            parent_id: {type: string,
                                                description: pool parent id}
                                            default_owner_id: {type: string,
                                                description: pool owner id}
                                            purpose: {type: string,
                                                description: pool purpose}
                                            name: {type: string,
                                                description: pool name}
                                            organization_id: {type: string,
                                                description: pool organization id}
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        """
        await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                     organization_id)
        pool_policy_res = await run_task(self.controller.get_pool_policies,
                                         organization_id=organization_id)
        policies = []
        pool_map = {}
        for pool, policy in pool_policy_res:
            if policy:
                policies.append(policy.to_dict())
            pool_id = pool.id
            if pool_id not in pool_map:
                pool_map[pool_id] = pool.to_dict()
        details = self.get_arg('details', bool, False)
        if details:
            for policy_dict in policies:
                pool_id = policy_dict['pool_id']
                policy_dict['details'] = pool_map.get(pool_id)
        self.write(json.dumps({'resource_policies': policies},
                              cls=ModelEncoder))


class PoolPoliciesAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):

    def _get_controller_class(self):
        return PoolPolicyAsyncController

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get policy info by ID
            Required permission: INFO_ORGANIZATION
        tags: [pool_policies]
        summary: Get pool policy
        parameters:
        -   name: id
            in: path
            description: Policy ID
            required: true
            type: string
        responses:
            200:
                description: Policy data
                schema:
                    type: object
                    example:
                        id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                        pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        type: total_expense_limit
                        active: True
                        limit: 1000
                        created_at: 1587029026
                        deleted_at: 0
            404:
                description: |
                    Not found:
                    - OE0002: Policy not found
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            404:
                description: |
                    Not found:
                    - OE0002: Policy not found
        security:
        - token: []
        """
        await self.check_permissions('INFO_ORGANIZATION', 'pool_policy', id)
        await super().get(id, **kwargs)

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing policy
            Required permission: MANAGE_POOLS
        tags: [pool_policies]
        summary: Edit policy
        parameters:
        -   name: id
            in: path
            description: policy ID
            required: True
            type: string
        -   in: body
            name: body
            description: New policy params
            required: True
            schema:
                type: object
                properties:
                    limit:
                        type: integer
                        description: "new limit for constraints"
                        required: False
                        example: 80
                    active:
                        type: boolean
                        required: False
                        description: "turn on or off constraints"
                        example: False
        responses:
            201:
                description: Created (returns created policy)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        type: total_expense_limit
                        active: True
                        limit: 1000
                        created_at: 1587029026
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0211: Parameter is immutable
                    - OE0216: Argument not provided
                    - OE0214: Argument should be a string
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0233: Incorrect body received
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
            404:
                description: |
                    Not found:
                    - OE0002: Policy not found
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
        data = self._request_body()
        data.update(kwargs)
        await self.check_permissions('MANAGE_POOLS', 'pool_policy', id)
        await super().patch(id, **data)

    async def delete(self, id, **kwargs):
        """
        ---
        description: |
            Deletes policy with specified id
            Required permission: MANAGE_POOLS
        tags: [pool_policies]
        summary: Delete policy
        parameters:
        -   name: id
            in: path
            description: Policy ID
            required: true
            type: string
        responses:
            204:
                description: Success
            404:
                description: |
                    Not found:
                    - OE0002: Policy not found
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
        await self.check_permissions('MANAGE_POOLS', 'pool_policy', id)
        await super().delete(id, **kwargs)
