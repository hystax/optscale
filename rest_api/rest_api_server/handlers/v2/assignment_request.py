import json

from tools.optscale_exceptions.common_exc import ForbiddenException

from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.controllers.assignment_request import (
    AssignmentRequestAsyncController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder


class AssignmentRequestAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                              BaseAuthHandler,
                                              BaseHandler):
    def _get_controller_class(self):
        return AssignmentRequestAsyncController

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create assignment request
            Required permission: TOKEN
        tags: [assignments]
        summary: Create resource assignment requests
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
                    message:
                        type: string
                        description: "Info message for approver"
                        required: False
                        example: Release this VM for QA team to use
                    approver_id:
                        type: string
                        description: "Approver id"
                        required: True
                        example: 68e5c9d5-310b-460f-922c-a1d27d6085d7
        responses:
            201:
                description: Created (returns created objects)
                schema:
                    type: object
                    example:
                        id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                        resource_id: 3d5a56e1-6e48-4d65-945a-a46f3a48e6e3
                        source_pool_id: a91ad80b-d969-490f-bf22-070652678073
                        message: Release this VM for QA team to use
                        created_at: 1585680056
                        deleted_at: 0
                        approver_id: 68e5c9d5-310b-460f-922c-a1d27d6085d7
                        status: PENDING
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
                    - OE0381: Not enough permissions for target resource
                    - OE0378: User is not a member of organization
                    - OE0424: Can't create assignment request for the same user
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
            res = await run_task(self.controller.create_assignment_request,
                                 user_id, organization_id, self.token, **data)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        self.set_status(201)
        self.write(res.to_json())

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of assignment requests for current user by token
            Required permission: TOKEN
        tags: [assignments]
        summary: List of assignment requests for current user by token
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   name: type
            in: query
            description: "filter returned requests by type"
            required: false
            type: str
        responses:
            200:
                description: assignment list
                schema:
                    type: object
                    properties:
                        assignment_requests:
                            type: array
                            items:
                                type: object
                            example:
                                incoming:
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
                                outgoing:
                                    -   id: 4c4204e8-4661-47eb-9f0e-eef50562c001
                                        resource_id: 2af0a771-71fa-466b-86a6-c5c9849be14f
                                        source_pool_id: 5a2b9b8c-c64e-4da5-81b4-30d5efb1c503
                                        message: Release this VM for QA team to use
                                        created_at: 1585680056
                                        deleted_at: 0
                                        approver_id: 72bce001-1d12-4e09-b05f-64f5c840dc9c
                                        requester_id: 68e5c9d5-310b-460f-922c-a1d27d6085d7
                                        status: PENDING
                                    -   id: 5339b51b-55f9-4666-a63e-97c4c5f97e7b
                                        resource_id: 750a6d28-76d1-40a3-8657-ea7b41187dda
                                        source_pool_id: null
                                        message: Not needed anymore
                                        created_at: 1585680056
                                        deleted_at: 0
                                        approver_id: 72bce001-1d12-4e09-b05f-64f5c840dc9c
                                        requester_id: 68e5c9d5-310b-460f-922c-a1d27d6085d7
                                        status: PENDING
            400:
                description: |
                    Wrong arguments
                    - OE0217: Invalid query parameter
            401:
                description: |
                    Unauthorized
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden
                    - OE0378: User is not a member of organization
                    - OE0234: Forbidden
        security:
        - token: []
        """
        user_id = await self.check_self_auth()
        req_type = self.get_arg('type', str, None)
        requests = await run_task(self.controller.list_assignment_requests,
                                  user_id, organization_id, req_type=req_type)
        dict_result = {}
        for key in requests:
            dict_result.update({key: [request.to_dict()
                                      for request in requests[key]]})
        requests = {'assignment_requests': dict_result}
        self.write(json.dumps(requests, cls=ModelEncoder))


class AssignmentRequestAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return AssignmentRequestAsyncController

    def _validate_action(self, action):
        if not action:
            raise OptHTTPError(400, Err.OE0216, ['action'])
        if not isinstance(action, str):
            raise OptHTTPError(400, Err.OE0214, ['action'])
        if action not in ['accept', 'decline', 'cancel']:
            raise OptHTTPError(400, Err.OE0166, [action])

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Accept or decline assignment request
            Required permission: TOKEN
        tags: [assignments]
        summary: Edit assignment request
        parameters:
        -   name: id
            in: path
            description: Assignment request ID
            required: true
            type: string
        -   in: body
            name: body
            description: request action
            required: true
            schema:
                type: object
                properties:
                    action:
                        type: string
                        example: accept
                        description: "accept,decline or cancel assignment request"
                        required: True
                    pool_id:
                        type: string
                        example: a91ad80b-d969-490f-bf22-070652678073
                        description: "Target pool id for resource"
                        required: False
                    owner_id:
                        type: string
                        example: 72bce001-1d12-4e09-b05f-64f5c840dc9c
                        description: "New owner for this resource"
                        required: False
                    created_at:
                        type: integer
                        description: "Timestamp for created assignment"
                        required: False
                        example: 1587029026
        responses:
            204:
                description: Accepted / declined and deleted
            400:
                description: |
                    Wrong arguments:
                    - OE0166: Action is not supported
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument is not provided
                    - OE0233: Incorrect body received
            404:
                description: |
                    Not found:
                    - OE0002: Request not found
            403:
                description: |
                    Forbidden:
                    - OE0378: User is not a member of organization
                    - OE0379: Target owner doesn't have enough permissions for target pool
                    - OE0380: Current user doesn't have enough permissions for target pool
                    - OE0381: Current user has no permissions for target resource
                    - OE0391: Current user can't accept/decline this request
                    - OE0419: Current user can't cancel this request
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
        security:
        - token: []
        """
        data = self._request_body()
        action = data.get('action')
        self._validate_action(action)
        user_id = await self.check_self_auth()
        action_map = {
            'accept': self.controller.accept_assignment_request,
            'decline': self.controller.decline_assignment_request,
            'cancel': self.controller.cancel_assignment_request
        }
        await run_task(action_map[action], id, user_id,
                       self.token, **data)
        self.set_status(204)
