import json

from auth_server.exceptions import Err
from auth_server.utils import ModelEncoder
from auth_server.controllers.assignment import AssignmentAsyncController
from auth_server.handlers.v1.base import BaseSecretHandler
from auth_server.handlers.v1.assignments import (
    AssignmentAsyncItemHandler as AssignmentAsyncItemHandler_v1,
    AssignmentAsyncCollectionHandler as AssignmentAsyncCollectionHandler_v1
)

from optscale_exceptions.http_exc import OptHTTPError
from optscale_exceptions.common_exc import (NotFoundException,
                                            WrongArgumentsException,
                                            UnauthorizedException,
                                            ForbiddenException)


class AssignmentAsyncItemHandler(AssignmentAsyncItemHandler_v1,
                                 BaseSecretHandler):
    def prepare(self):
        pass

    async def get(self, id, **kwargs):
        """
        ---
        x-hidden: true
        tags: [assignments]
        summary: Get assignment
        description: |
            Gets assignment by id
            Required permission: LIST_ROLES and LIST_USERS
        parameters:
        -   name: user_id
            in: path
            description: User ID
            required: true
            type: string
        -   name: id
            in: path
            description: ID of assignment to return
            required: true
            type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Assignment id"}
                        scope_name: {type: string,
                            description: "Scope name"}
                        role_id: {type: integer,
                            description: "Role id"}
                        type_id: {type: integer,
                            description: "Type id"}
                        resource_id: {type: string,
                            description: "Resource id"}
                        user_id: {type: string,
                            description: "User id"}
                        created_at: {type: integer,
                            description: Created timestamp (service
                            field)}
                        deleted_at: {type: integer,
                            description: Deleted timestamp (service
                            field)}
            401:
                description: |
                    Unauthorized:
                    - OA0010: Token not found
                    - OA0011: Invalid token
                    - OA0023: Unauthorized
                    - OA0062: This resource requires an authorization token
            403:
                description: |
                    Forbidden:
                    - OA0012: Forbidden!
            404:
                description: |
                    Not found:
                    - OA0003: Item not found
                    - OA0004: User is not an owner of assignment
                    - OA0019: Assignment not found
                    - OA0024: User was not found
        security:
        - token: []
        """
        await self.check_token()
        await super().get(id, **kwargs)

    async def delete(self, id, **kwargs):
        """
        ---
        tags: [assignments]
        summary: Delete assignment
        description: |
            Deletes an assignment with specified id
            Required permission: ASSIGN_USER, ASSIGN_SELF or CLUSTER_SECRET
        parameters:
        -   name: user_id
            in: path
            description: User ID
            required: true
            type: string
        -   name: id
            in: path
            description: ID of assignment to delete
            required: true
            type: string
        responses:
            204: {description: Success}
            401:
                description: |
                    Unauthorized:
                    - OA0010: Token not found
                    - OA0011: Invalid token
                    - OA0023: Unauthorized
                    - OA0062: This resource requires an authorization token
            403:
                description: |
                    Forbidden:
                    - OA0012: Forbidden!
            404:
                description: |
                    Not found:
                    - OA0003: Item not found
                    - OA0004: User is not an owner of assignment
                    - OA0019: Assignment not found
                    - OA0024: User was not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_token()
            kwargs.update(self.token)
        item, _ = await self._get_item(id)
        self._validate_params(item, **kwargs)
        try:
            await self.controller.delete(id, **kwargs)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        self.set_status(204)


class AssignmentAsyncCollectionHandler(AssignmentAsyncCollectionHandler_v1,
                                       BaseSecretHandler):
    def prepare(self):
        pass

    async def get(self, user_id, **kwargs):
        """
        ---
        tags: [assignments]
        summary: List assignments
        description: |
            Gets a list of assignments
            Required permission: LIST_ROLES and LIST_USERS or CLUSTER_SECRET
        parameters:
        -   name: user_id
            in: path
            description: User ID
            required: true
            type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        assignments:
                            type: array
                            items:
                                type: object
                                properties:
                                    assignment_id: {type: string,
                                        description: "Assignment id"}
                                    assignment_resource: {type: string,
                                        description: "Assignment resource id"}
                                    assignment_resource_type: {type: integer,
                                        description: "Assignment resource type"}
                                    scope_name: {type: string,
                                        description: "Scope name"}
                                    role_id: {type: integer,
                                        description: "Role id"}
                                    role_name: {type: string,
                                        description: "Role name"}
                                    role_scope: {type: string,
                                        description: "Role scope id"}
                                    role_type: {type: string,
                                        description: "Role type"}
            401:
                description: |
                    Unauthorized:
                    - OA0010: Token not found
                    - OA0011: Invalid token
                    - OA0023: Unauthorized
                    - OA0062: This resource requires an authorization token
            403:
                description: |
                    Forbidden:
                    - OA0012: Forbidden!
            404:
                description: |
                    Not found:
                    - OA0005: User does not exist
                    - OA0024: User was not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_token()
            kwargs.update(self.token)
        else:
            kwargs['ignore_permissions'] = True
        await super().get(user_id, **kwargs)

    async def post(self, user_id, **url_params):
        """
        ---
        x-hidden: true
        tags: [assignments]
        summary: Add assignment
        description: |
            Adds a new assignment
            Required permission: ASSIGN_USER or ASSIGN_SELF
        parameters:
        -   name: user_id
            in: path
            description: User ID
            required: true
            type: string
        -   in: body
            name: body
            description: Assignment to add
            required: true
            schema:
                type: object
                properties:
                    role_id: {type: integer,
                        description: "Role id"}
                    type_id: {type: integer,
                        description: "Type id"}
                    resource_id: {type: string,
                        description: "Resource_id (Assignment scope_id)"}
        responses:
            201: {description: Success (returns created data)}
            400:
                description: |
                    Wrong arguments:
                    - OA0022: Unexpected parameters
                    - OA0026: Invalid type with id
                    - OA0031: Argument is required
                    - OA0049: Argument should be integer
                    - OA0050: Incorrect request body received
            401:
                description: |
                    Unauthorized:
                    - OA0010: Token not found
                    - OA0011: Invalid token
                    - OA0023: Unauthorized
                    - OA0062: This resource requires an authorization token
            403:
                description: |
                    Forbidden:
                    - OA0012: Forbidden!
                    - OA0017: Role not assignable to user
                    - OA0018: Scope of assignment should be not greater than user scope
            404:
                description: |
                    Not found:
                    - OA0020: Invalid type
                    - OA0024: User was not found
        security:
        - token: []
        """
        await super().post(user_id, **url_params)


class MyAssignmentCollectionHandler(AssignmentAsyncCollectionHandler_v1):
    async def post(self, user_id, **url_params):
        self.raise405()

    async def get(self, **kwargs):
        """
        ---
        tags: [assignments]
        summary: List of self assignments
        description: >
            Gets a list of self assignments  \n\n
            Required permission: TOKEN
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        assignments:
                            type: array
                            items:
                                type: object
                                properties:
                                    assignment_id: {type: string,
                                        description: "Assignment id"}
                                    assignment_resource: {type: string,
                                        description: "Assignment resource id"}
                                    assignment_resource_type: {type: integer,
                                        description: "Assignment resource type"}
                                    role_id: {type: integer,
                                        description: "Role id"}
                                    role_name: {type: string,
                                        description: "Role name"}
                                    role_scope: {type: string,
                                        description: "Role scope id"}
            401:
                description: |
                    Unauthorized:
                    - OA0010: Token not found
                    - OA0011: Invalid token
                    - OA0023: Unauthorized
                    - OA0062: This resource requires an authorization token
        security:
        - token: []
        """
        kwargs.update(self.token)
        try:
            assignments = await self.controller.my_assignments(**kwargs)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        assignments_dict = {'assignments': assignments}
        self.write(json.dumps(assignments_dict, cls=ModelEncoder))


class RegisterAssignmentCollectionHandler(BaseSecretHandler):

    def _get_controller_class(self):
        return AssignmentAsyncController

    async def post(self, user_id, **kwargs):
        """
        ---
        tags: [assignments]
        summary: Register new assignment
        description: |
            Adds a new assignment
            Required permission: CLUSTER_SECRET
        parameters:
        -   name: user_id
            in: path
            description: User ID
            required: true
            type: string
            example: 2ac3f1b0-3a7e-4d77-ad6c-7663d7699fcf
        -   in: body
            name: body
            description: Assignment to add
            required: true
            schema:
                type: object
                properties:
                    role_id:
                        type: integer
                        description: Role id
                        example: 3
                    type_id:
                        type: integer
                        description: Type id
                        example: 3
                    resource_id:
                        type: string
                        description: Resource_id (Assignment scope_id)
                        example: bf76ea20-b491-4d82-a785-2f2d554baa9d
        responses:
            201:
                description: Success (returns created data)
            400:
                description: |
                    Wrong arguments:
                    - OA0022: Unexpected parameters
                    - OA0026: Invalid type with id
                    - OA0031: Argument is required
                    - OA0049: Argument should be integer
                    - OA0050: Incorrect request body received
            401:
                description: |
                    Unauthorized:
                    - OA0007: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OA0012: Forbidden!
                    - OA0006: Bad secret
            404:
                description: |
                    Not found:
                    - OA0024: User was not found
                    - OA0020: Invalid type
        security:
        - secret: []
        """
        self.check_cluster_secret()
        data = self._request_body()
        kwargs.update({'user_id': user_id})
        duplicates = list(filter(lambda x: x in kwargs.keys(),
                                 data.keys()))
        if duplicates:
            unexpected_string = ', '.join(duplicates)
            raise OptHTTPError(400, Err.OA0022, [unexpected_string])
        data.update(kwargs)
        try:
            item = await self.controller.register(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.set_status(201)
        self.write(item.to_json())
