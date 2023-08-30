import json

from tools.optscale_exceptions.http_exc import OptHTTPError

from tools.optscale_exceptions.common_exc import ForbiddenException
from rest_api.rest_api_server.controllers.assignment import AssignmentAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder


class AssignmentAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                       BaseAuthHandler):
    def _get_controller_class(self):
        return AssignmentAsyncController

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Assign resource to owner and pool
            Required permission: TOKEN
        tags: [assignments]
        summary: Create resource assignment
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: body
            description: resource assignment info to add
            required: true
            schema:
                type: object
                properties:
                    resource_id:
                        type: string
                        description: "Resource id"
                        required: True
                        example: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                    owner_id:
                        type: string
                        description: "Employee id for resource ownership"
                        required: False
                        example: bd782b9c-3616-4496-99ae-220743eacd55
                    pool_id:
                        type: string
                        description: "Pool id"
                        required: True
                        example: 68e5c9d5-310b-460f-922c-a1d27d6085d7
                    created_at:
                        type: integer
                        description: >
                            Timestamp for created assignment. Default is curr ts.
                        required: False
                        example: 1587029026
        responses:
            201:
                description: Created (returns created object)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c"
                        owner_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d"
                        resource_id: d7a8a215-2a61-404c-b4e3-5f1267ea3d0d"
                        deleted_at: 0
                        created_at: 1587029026
                        pool_id: 3d7c7c68-8d3b-4fb9-b12a-2c74bafe2429
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0216: Argument not provided
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0233: Incorrect body received
                    - OE0456: Duplicate path parameters in the request body
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0379: Target owner doesn't have enough permissions for target pool
                    - OE0380: Current user doesn't have enough permissions for target pool
                    - OE0381: Curr user has no permissions for target resource
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
        security:
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        user_id = await self.check_self_auth()
        try:
            res = await run_task(self.controller.create_assignment,
                                 user_id, organization_id, self.token, **data)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        self.set_status(201)
        self.write(res)

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of assignments for current user by token
            Required permission: TOKEN
        tags: [assignments]
        summary: List of assignments for current user by token
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        responses:
            200:
                description: assignments list
                schema:
                    type: object
                    properties:
                        assignments:
                            type: array
                            items:
                                type: object
                            example:
                                -   id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                                    resource_id: 3d5a56e1-6e48-4d65-945a-a46f3a48e6e3
                                    source_pool_id: a91ad80b-d969-490f-bf22-070652678073
                                    message: Release this VM for QA team to use
                                    created_at: 1585680056
                                    deleted_at: 0
                                    approver_id: 68e5c9d5-310b-460f-922c-a1d27d6085d7
                                    requester_id: 72bce001-1d12-4e09-b05f-64f5c840dc9c
                                    status: PENDING
                                -   id: b99a2fb5-06a4-47a5-80fe-64d7dd9995de
                                    resource_id: 108f2039-f089-4cd8-8639-479269eb4d08
                                    source_pool_id: null
                                    message: Not needed anymore
                                    created_at: 1585680056
                                    deleted_at: 0
                                    approver_id: 68e5c9d5-310b-460f-922c-a1d27d6085d7
                                    requester_id: 72bce001-1d12-4e09-b05f-64f5c840dc9c
                                    status: PENDING
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0378: User is not a member of organization
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        """
        user_id = await self.check_self_auth()
        res = await run_task(self.controller.get_assignments,
                             user_id, organization_id)
        requests = {'assignments': res}
        self.write(json.dumps(requests, cls=ModelEncoder))
