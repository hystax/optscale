import json

from rest_api_server.controllers.organization_limit_hit import OrganizationLimitHitAsyncController
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.base_async import (BaseAsyncCollectionHandler,
                                                    BaseAsyncItemHandler)
from rest_api_server.utils import run_task, ModelEncoder


class OrganizationLimitHitsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                                  BaseAuthHandler, BaseHandler):

    def _get_controller_class(self):
        return OrganizationLimitHitAsyncController

    async def post(self, organization_id):
        """
        ---
        description: |
            Create organization limit hit
            Required permission: CLUSTER_SECRET
        tags: [organization_limit_hits]
        summary: Create organization limit hit
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: body
            description: organization limit hit info to add
            required: true
            schema:
                type: object
                properties:
                    constraint_id:
                        type: string
                        description: Violated organization constraint id
                        required: true
                        example: db39e3ac-94a7-44cd-b7dc-4be5d3213aa8
                    constraint_limit:
                        type: number
                        description: |
                            Organization constraint limit that was violated
                        required: true
                        example: 31.11
                    value:
                        type: number
                        description: Violated value
                        required: true
                        example: 93.33
                    created_at:
                        type: integer
                        description: Created timestamp (service field)
                        required: false
                    run_result:
                        type: object
                        description: |
                            Constraint run result on hit
                            (constraint type specific)
                        required: false
                        example:
                            average: 29
                            today: 79
                            breakdown:
                                1643709325: 28
                                1643809325: 28
                                1643909325: 28
                                1644009325: 30
                                1644109325: 30
        responses:
            201:
                description: Created (returns created object)
                schema:
                    type: object
                    example:
                        id: a3c6b152-f2ff-4eee-b534-3157f3cb2d9e
                        constraint_id: db39e3ac-94a7-44cd-b7dc-4be5d3213aa8
                        organization_id: 08704f0b-9226-452f-8834-47978d4409a6
                        constraint_limit: 31.11
                        value: 93.33
                        deleted_at: 0
                        created_at: 0
                        run_result: {}
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0216: Argument is not provided
                    - OE0466: Argument should be number
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Organization/OrganizationConstraint not found
            409:
                description: |
                    Conflict:
                    - OE0516: Organization limit hit for constraint already exists in organization
        security:
        - secret: []
        """
        self.check_cluster_secret()
        await super().post(organization_id=organization_id)

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of organization limit hits
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [organization_limit_hits]
        summary: List of organization limit hits
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: constraint_id
            in: query
            description: Organization constraint id
            required: false
            type: string
        responses:
            200:
                description: Organization limit hits list
                schema:
                    type: object
                    properties:
                        organization_limit_hits:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: |
                                            Unique organization limit hit id
                                    deleted_at:
                                        type: integer
                                        description: |
                                            Deleted timestamp (service field)
                                    created_at:
                                        type: integer
                                        description: |
                                            Created timestamp (service field)
                                    organization_id:
                                        type: integer
                                        description: Organization id
                                    constraint_id:
                                        type: string
                                        description: |
                                            Id of violated organization constraint
                                    constraint_limit:
                                        type: number
                                        description: Limit that was violated
                                    value:
                                        type: number
                                        description: |
                                            Constraint violated value
                                    run_result:
                                        type: object
                                        description: |
                                            Constraint run result on hit
                                            (constraint type specific)

            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Organization/OrganizationConstraint not found
        security:
        - secret: []
        - token: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        constraint_id = self.get_arg('constraint_id', str)
        params = {}
        if constraint_id:
            params['constraint_id'] = constraint_id
        res = await run_task(self.controller.list,
                             organization_id=organization_id, **params)
        hits = {'organization_limit_hits': res}
        self.write(json.dumps(hits, cls=ModelEncoder))


class OrganizationLimitHitsAsyncItemHandler(BaseAsyncItemHandler,
                                            BaseAuthHandler):

    def _get_controller_class(self):
        return OrganizationLimitHitAsyncController

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing organization limit hit
            Required permission: CLUSTER_SECRET
        tags: [organization_limit_hits]
        summary: Edit organization limit hit
        parameters:
        -   name: id
            in: path
            description: Organization limit hit ID
            required: true
            type: string
        -   in: body
            name: body
            description: Organization limit hit changes
            required: true
            schema:
                type: object
                properties:
                    constraint_limit:
                        type: number
                        description: |
                            Organization constraint limit that was violated
                        required: false
                        example: 31.11
                    value:
                        type: number
                        description: Violated value
                        required: false
                        example: 93.33
                    run_result:
                        type: object
                        description: |
                            Constraint run result on hit
                            (constraint type specific)
                        required: false
                        example:
                            average: 29
                            today: 79
                            breakdown:
                                1643709325: 28
                                1643809325: 28
                                1643909325: 28
                                1644009325: 30
                                1644109325: 30
        responses:
            200:
                description: Success (returns modified object)
                type: object
                example:
                    id: a3c6b152-f2ff-4eee-b534-3157f3cb2d9e
                    constraint_id: db39e3ac-94a7-44cd-b7dc-4be5d3213aa8
                    organization_id: 08704f0b-9226-452f-8834-47978d4409a6
                    constraint_limit: 31.11
                    value: 93.33
                    deleted_at: 0
                    created_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0211: Parameter is immutable
                    - OE0212: Unexpected parameters
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Organization/OrganizationLimitHit not found
        security:
        - secret: []
        """
        data = self._request_body()
        data.update(kwargs)
        self.check_cluster_secret()
        await super().patch(id, **data)

    def get(self, id, **kwargs):
        self.raise405()

    def delete(self, id, **kwargs):
        self.raise405()
