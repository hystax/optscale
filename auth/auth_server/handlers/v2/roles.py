import json
import logging

from tornado import gen

from auth.auth_server.controllers.role import RoleAsyncController
from auth.auth_server.handlers.v1.base import BaseSecretHandler
from auth.auth_server.handlers.v1.roles import (
    RoleAsyncItemHandler as RoleAsyncItemHandler_v1,
    RoleAsyncCollectionHandler as RoleAsyncCollectionHandler_v1)
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException)
from tools.optscale_exceptions.http_exc import OptHTTPError
from auth.auth_server.utils import ModelEncoder, as_dict

LOG = logging.getLogger(__name__)


class RoleAsyncItemHandler(RoleAsyncItemHandler_v1):
    async def get(self, id, **kwargs):
        """
        ---
        x-hidden: true
        tags: [roles]
        summary: Get role
        description: |
            Gets a role by id
            Required permission: LIST_ROLES
        parameters:
        -   name: id
            in: path
            description: ID of role to return
            required: true
            type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        id: {type: integer,
                            description: "Unique role id"}
                        name: {type: string,
                            description: "Role name"}
                        type_id: {type: integer,
                            description: "Type id"}
                        lvl_id: {type: integer,
                            description: "Top level of actions"}
                        scope_id: {type: string,
                            description: "Id of resource managed by this
                            role"}
                        scope_name: {type: string,
                            description: "Name of resource managed by this
                            role"}
                        is_active: {type: boolean,
                            description: "Is role active?"}
                        description: {type: string,
                            description: "Type description"}
                        shared: {type: boolean,
                            description: "Is role shared?"}
                        actions:
                            type: object
                            properties:
                                ACTION_GROUP_NAME:
                                    type: object
                                    properties:
                                        ACTION_NAME:
                                            type: boolean
                                            description: "Is action allowed?"
            400:
                description: |
                    Wrong arguments:
                    - OA0061: Database error
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
                    - OA0024: User was not found
        security:
        - token: []
        """
        await super().get(id, **kwargs)

    async def patch(self, id, **kwargs):
        """
        ---
        x-hidden: true
        tags: [roles]
        summary: Edit role
        description: |
            Modifies a role with specified id
            Required permission: EDIT_ROLES or EDIT_OWN_ROLES or EDIT_SUBLEVEL_ROLES
        parameters:
        -   name: id
            in: path
            description: ID of role to modify
            required: true
            type: string
        -   in: body
            name: body
            description: New data
            required: true
            schema:
                type: object
                properties:
                    name: {type: string,
                        description: "Role name"}
                    is_active: {type: boolean,
                        description: "Is role active?"}
                    description: {type: string,
                        description: "Type description"}
                    shared: {type: boolean,
                        description: "Is role shared?"}
                    actions:
                        type: object
                        properties:
                            ACTION_GROUP_NAME:
                                type: object
                                properties:
                                    ACTION_NAME:
                                        type: boolean
                                        description: "Is action allowed?"
        responses:
            200: {description: Success (returns modified role data)}
            400:
                description: |
                    Wrong arguments:
                    - OA0020: Invalid type
                    - OA0022: Unexpected parameters
                    - OA0031: Argument is required
                    - OA0032: Argument is not provided
                    - OA0033: Argument should be a string
                    - OA0034: Cannot create role with given lvl
                    - OA0036: Action cannot be assigned
                    - OA0048: Wrong number of characters
                    - OA0049: Argument should be integer
                    - OA0050: Incorrect request body received
                    - OA0051: Action group cannot be assigned
                    - OA0054: Invalid scope_id
                    - OA0061: Database error
                    - OA0065: Argument should not contain only whitespaces
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
                    - OA0024: User was not found
                    - OA0030: Role was not found
        security:
        - token: []
        """
        await super().patch(id, **kwargs)

    async def delete(self, id, **kwargs):
        """
        ---
        x-hidden: true
        tags: [roles]
        summary: Delete role
        description: |
            Deletes a role with specified id
            Required permission: DELETE_ROLE
        parameters:
        -   name: id
            in: path
            description: ID of role to delete
            required: true
            type: string
        responses:
            204: {description: Success}
            400:
                description: |
                    Wrong arguments:
                    - OA0026: Invalid type with id
                    - OA0027: Resource not found
                    - OA0061: Database error
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
                    - OA0024: User was not found
                    - OA0028: Item was not found
                    - OA0030: Role was not found
        security:
        - token: []
        """
        await super().delete(id, **kwargs)


class RoleAsyncCollectionHandler(RoleAsyncCollectionHandler_v1):
    async def get(self, **kwargs):
        """
        ---
        x-hidden: true
        tags: [roles]
        summary: List roles
        description: |
            Gets a list of roles
            Required permission: LIST_ROLES or LIST_USERS
        parameters:
        -   name: assignable
            in: query
            description: Get roles assignable to user with given user_id
            required: false
            type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        roles:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: integer,
                                        description: "Unique role id"}
                                    name: {type: string,
                                        description: "Role name"}
                                    type_id: {type: integer,
                                        description: "Type id"}
                                    lvl_id: {type: integer,
                                        description: "Top level of actions"}
                                    scope_name: {type: string,
                                        description: "Name for resource,
                                        managed by this role"}
                                    scope_id: {type: string,
                                        description: "Id for resource, managed
                                        by this role"}
                                    is_active: {type: boolean,
                                        description: "Is role active?"}
                                    description: {type: string,
                                        description: "Type description"}
                                    shared: {type: boolean,
                                        description: "Is role shared?"}
                                    created_at: {type: integer,
                                        description: "Created timestamp
                                        (service field)"}
                                    deleted_at: {type: integer,
                                        description: "Deleted timestamp
                                        (service field)"}
                                    purpose: {type: string,
                                        description: "Purpose of the role"}
            400:
                description: |
                    Wrong arguments:
                    - OA0061: Database error
                    - OA0027: Resource not found
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
                    - OA0024: User was not found
        security:
        - token: []
        """
        await super().get(**kwargs)

    async def post(self, **url_params):
        """
        ---
        x-hidden: true
        tags: [roles]
        summary: Create role
        description: |
            Adds a new role
            Required permission: CREATE_ROLE
        parameters:
        -   in: body
            name: body
            description: Role to add
            required: true
            schema:
                type: object
                properties:
                    name: {type: string,
                        description: "Role name"}
                    type_id: {type: integer,
                        description: "Type id"}
                    lvl_id: {type: integer,
                        description: "Top level of actions"}
                    scope_id: {type: string,
                        description: "Id for resource, managed by this role"}
                    is_active: {type: boolean,
                        description: "Is role active?"}
                    description: {type: string,
                        description: "Type description"}
                    shared: {type: boolean,
                        description: "Is role shared?"}
        responses:
            201: {description: Success (returns created role data)}
            400:
                description: |
                    Wrong arguments:
                    - OA0020: Invalid type
                    - OA0021: Parameter is immutable
                    - OA0022: Unexpected parameters
                    - OA0026: Invalid type with id
                    - OA0027: Resource not found
                    - OA0031: Argument is required
                    - OA0032: Argument is not provided
                    - OA0033: Argument should be a string
                    - OA0034: Cannot create role with given lvl
                    - OA0036: Action cannot be assigned
                    - OA0048: Wrong number of characters
                    - OA0049: Argument should be integer
                    - OA0050: Incorrect request body received
                    - OA0051: Action group cannot be assigned
                    - OA0054: Invalid scope_id
                    - OA0061: Database error
                    - OA0065: Argument should not contain only whitespaces
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
            409:
                description: |
                    Conflict:
                    - OA0035: Role already exists
        security:
        - token: []
        """
        await super().post(**url_params)


class PurposedRoleCollectionHandler(BaseSecretHandler):
    def _get_controller_class(self):
        return RoleAsyncController

    async def get(self, **kwargs):
        """
        ---
        x-hidden: true
        tags: [roles]
        summary: Get role by purpose
        description: |
            Get role by purpose
            Required permission: CLUSTER SECRET
        parameters:
        -   name: purpose
            in: query
            description: purpose of the role
            required: true
            type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        id: {type: integer,
                            description: "Unique role id"}
                        name: {type: string,
                            description: "Role name"}
                        type_id: {type: integer,
                            description: "Type id"}
                        lvl_id: {type: integer,
                            description: "Top level of actions"}
                        scope_id: {type: string,
                            description: "Id of resource managed by this
                            role"}
                        is_active: {type: boolean,
                            description: "Is role active?"}
                        description: {type: string,
                            description: "Type description"}
                        shared: {type: boolean,
                            description: "Is role shared?"}
                        purpose: {type: string,
                            description: "purpose of the role"}
                        created_at: {type: integer,
                            description: "Created timestamp (service field)"}
                        deleted_at: {type: integer,
                            description: "Deleted timestamp (service field)"}
            400:
                description: |
                    Wrong arguments:
                    - OA0031: Argument is required
                    - OA0058: Is not a valid purpose
            401:
                description: |
                    Unauthorized:
                    - OA0007: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OA0006: Bad secret
            404:
                description: |
                    Not found:
                    - OA0057: Role with purpose not found
        security:
        - secret: []
        """
        self.check_cluster_secret()
        purpose = self.get_argument('purpose')
        try:
            res = await self.controller.get_purposed_role(purpose=purpose)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.write(json.dumps(as_dict(res), cls=ModelEncoder))
