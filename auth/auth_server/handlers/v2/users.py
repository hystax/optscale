import json
import logging

from auth.auth_server.controllers.token import TokenAsyncController
from auth.auth_server.exceptions import Err
from auth.auth_server.handlers.v1.base import BaseSecretHandler
from auth.auth_server.handlers.v1.users import (
    UserAsyncItemHandler as UserAsyncItemHandler_v1,
    UserAsyncCollectionHandler as UserAsyncCollectionHandler_v1)
from auth.auth_server.handlers.v2.base import BaseHandler as BaseHandler_v2
from auth.auth_server.utils import ModelEncoder, run_task

from tools.optscale_exceptions.common_exc import (NotFoundException,
                                                  ForbiddenException)
from tools.optscale_exceptions.http_exc import OptHTTPError


LOG = logging.getLogger(__name__)


class UserAsyncItemHandler(UserAsyncItemHandler_v1,
                           BaseSecretHandler):

    def prepare(self):
        pass

    async def get(self, user_id, **kwargs):
        """
        ---
        tags: [users]
        summary: Get user
        description: |
            Gets user by id
            Required permission: LIST_USERS or CLUSTER_SECRET
        parameters:
        -   name: id
            in: path
            description: ID of user to return
            required: true
            type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: Unique user id}
                        email: {type: string,
                            description: User's email - used as login}
                        display_name: {type: string,
                            description: User's display name}
                        is_active: {type: boolean,
                            description: "Is user active?"}
                        type_id: {type: integer,
                            description: Type id}
                        scope_id: {type: string,
                            description: User scope id (None scope means root)}
                        scope_name: {type: string,
                            description: User scope name}
                        created_at: {type: integer,
                            description: Created timestamp (service field)}
                        deleted_at: {type: integer,
                            description: Deleted timestamp (service field)}
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
                    - OA0043: User not found
        security:
        - token: []
        - secret: []
        """
        if self.secret:
            self.check_cluster_secret()
            kwargs['ignore_permissions'] = True
        else:
            await self.check_token()
            kwargs['ignore_permissions'] = False
        await super().get(user_id, **kwargs)

    async def patch(self, user_id, **kwargs):
        """
        ---
        tags: [users]
        summary: Edit user
        description: |
            Modifies a user with specified id
            Required permission: EDIT_USER_INFO or ACTIVATE_USER or
                RESET_USER_PASSWORD
        parameters:
        -   name: id
            in: path
            description: ID of user to modify
            required: true
            type: string
        -   in: body
            name: body
            description: New data
            required: true
            schema:
                type: object
                properties:
                    display_name: {type: string,
                        description: User's display name}
                    is_active: {type: boolean,
                        description: "Is user active?"}
                    password: {type: string,
                        description: User's password}
        responses:
            201: {description: Success (returns modified user data)}
            400:
                description: |
                    Wrong arguments:
                    - OA0021: Parameter is immutable
                    - OA0022: Unexpected parameters
                    - OA0032: Argument is not provided
                    - OA0033: Argument should be a string
                    - OA0041: Password should be at least 4 characters
                    - OA0048: Wrong number of characters
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
                    - OA0024: User was not found
        security:
        - token: []
        """
        await self.check_token()
        await super().patch(user_id, **kwargs)

    async def delete(self, user_id, **kwargs):
        """
        ---
        tags: [users]
        summary: Delete user
        description: |
            Deletes a user with specified id
            Required permission: DELETE_USER or CLUSTER SECRET
        parameters:
        -   name: id
            in: path
            description: ID of user to delete
            required: true
            type: string
        responses:
            204: {description: Success}
            401:
                description: |
                    Unauthorized:
                    - OA0007: This resource requires authorization
                    - OA0010: Token not found
                    - OA0011: Invalid token
                    - OA0023: Unauthorized
                    - OA0062: This resource requires an authorization token
            403:
                description: |
                    Forbidden:
                    - OA0006: Bad secret
                    - OA0012: Forbidden!
            404:
                description: |
                    Not found:
                    - OA0003: Item not found
                    - OA0043: User not found
                    - OA0024: User was not found
        security:
        - token: []
        - secret: []
        """

        if self.secret:
            self.check_cluster_secret()
            kwargs['ignore_permissions'] = True
        else:
            await self.check_token()
            kwargs['ignore_permissions'] = False
        await super().delete(user_id, **kwargs)


class UserAsyncCollectionHandler(UserAsyncCollectionHandler_v1,
                                 BaseSecretHandler,
                                 BaseHandler_v2):

    def prepare(self):
        pass

    async def post(self, **url_params):
        """
        ---
        tags: [users]
        summary: Create user
        description: |
            Adds a new user
            Required permission: NOT PROTECTED
        parameters:
        -   in: body
            name: body
            description: User to add
            required: true
            schema:
                type: object
                properties:
                    email: {type: string,
                        description: User's email - used as login}
                    display_name: {type: string,
                        description: User's display name}
                    is_active: {type: boolean,
                        description: "Is user active?"}
                    password: {type: string,
                        description: User's password}
                    type_id: {type: integer,
                        description: Type id}
                    scope_id: {type: string,
                        description: User scope id (None scope means root)}
                    token: {type: string, description: Token}
        responses:
            201: {description: Success (returns created user data)}
            400:
                description: |
                    Wrong arguments:
                    - OA0021: Parameter is immutable
                    - OA0022: Unexpected parameters
                    - OA0026: Invalid type with id
                    - OA0031: Argument is required
                    - OA0032: Argument is not provided
                    - OA0033: Argument should be a string
                    - OA0039: Email and/or password is not provided
                    - OA0041: Password should be at least 4 characters
                    - OA0044: Email has invalid format
                    - OA0048: Wrong number of characters
                    - OA0049: Argument should be integer
                    - OA0061: Database error
                    - OA0065: Argument should not contain only whitespaces
                    - OA0070: Registration with domain is prohibited. Please
                        use your business email for registration
            401:
                description: |
                    Unauthorized:
                    - OA0007: This resource requires authorization
                    - OA0023: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OA0006: Bad secret
                    - OA0012: Forbidden!
            404:
                description: |
                    Not found:
                    - OA0024: User was not found
                    - OA0064: No one root type is found
            409:
                description: |
                    Conflict:
                    - OA0042: User already exists
        """
        body = self._request_body()
        for field in ['scope_id', 'type_id', 'self_registration',
                      'is_password_autogenerated']:
            if body.get(field) is not None:
                raise OptHTTPError(400, Err.OA0021, [field])
        duplicates = list(filter(lambda x: x in url_params, body.keys()))
        if duplicates:
            unexpected_string = ', '.join(duplicates)
            raise OptHTTPError(400, Err.OA0022, [unexpected_string])
        body.update(url_params)
        self._validate_params(**body)
        res = await run_task(
            self.controller.create, **body, **self.token,
            self_registration=True)
        user = res.to_dict()
        token_ctl = TokenAsyncController(self.session(), self._config)
        try:
            res = await token_ctl.create_token_by_user_id(
                user_id=user['id'], ip=self.get_ip_addr(), register=True)
            user['token'] = res.get('token')
        except (NotFoundException, ForbiddenException):
            user['token'] = None
        self.set_status(201)
        self.write(json.dumps(user, cls=ModelEncoder))

    async def get(self, **kwargs):
        """
        ---
        tags: [users]
        summary: List users
        description: |
            Gets a list of users
            Required permission: LIST_USERS or CLUSTER SECRET
        parameters:
        -   name: user_id
            in: query
            description: Get users for user_id bulk (for CLUSTER_SECRET only)
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        users:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description: Unique user id}
                                    email: {type: string,
                                        description: User's email - used as
                                        login}
                                    display_name: {type: string,
                                        description: User's display name}
                                    is_active: {type: boolean,
                                        description: "Is user active?"}
                                    type_id: {type: integer,
                                        description: Unique user id}
                                    scope_id: {type: string,
                                        description: User scope id (None scope
                                        means root)}
                                    created_at: {type: integer,
                                        description: Created timestamp (service
                                        field)}
                                    deleted_at: {type: integer,
                                        description: Deleted timestamp (service
                                        field)}
                                    last_login: {type: integer,
                                        description: Last token created
                                        timestamp}
            400:
                description: |
                    Wrong arguments:
                    - OA0060: Invalid argument
            401:
                description: |
                    Unauthorized:
                    - OA0007: This resource requires authorization
                    - OA0010: Token not found
                    - OA0011: Invalid token
                    - OA0023: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OA0006: Bad secret
            404:
                description: |
                    Not found:
                    - OA0024: User was not found
        security:
        - token: []
        - secret: []
        """
        users_ids = self.get_arg('user_id', str, repeated=True)
        if not users_ids:
            await self.check_token()
            await super().get(**kwargs)
        else:
            if not self.secret:
                raise OptHTTPError(401, Err.OA0007, [])
            self.check_cluster_secret()
            res = await self.controller.get_bulk_users(users_ids, **kwargs)
            users = [user for user in res]
            result = {
                'users': users
            }
            self.write(json.dumps(result, cls=ModelEncoder))


class CheckUserExistenceHandler(UserAsyncCollectionHandler):
    def prepare(self):
        if not self.secret:
            raise OptHTTPError(401, Err.OA0007, [])

    async def get(self, **url_params):
        """
        ---
        tags: [users]
        summary: Check existence of the user by email
        description: |
            Check existence of the user by email
            Required permission: CLUSTER SECRET
        parameters:
        -   name: email
            in: query
            description: user email
            required: false
            type: string
        -   name: user_info
            in: query
            description: include user info? default - false
            required: false
            type: boolean
        responses:
            200:
                description: Success
                schema:
                    type: object
                    example:
                        exists: True
                        user_info:
                            type_id: 0
                            email: test@email.com
                            id: 1bede1cf-4000-4bca-b3dc-bf378bd508f3
                            display_name: Test user
                            created_at: 1594964175
                            is_active: True
                            deleted_at: 0
                            scope_id: None
            400:
                description: |
                    Wrong arguments:
                    - OA0063: Argument should be true or false
                    - OA0060: Invalid argument
            401:
                description: |
                    Unauthorized:
                    - OA0007: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OA0006: Bad secret
        security:
        - token: []
        - secret: []
        """
        self.check_cluster_secret()
        email = self.get_arg('email', str)
        user_info = self.get_arg('user_info', bool, default=False)
        user = await self.controller.get_user_by_email(email)
        result = {'exists': True if user else False}
        if user and user_info:
            result.update({'user_info': user.to_dict()})
        self.write(json.dumps(result, cls=ModelEncoder))

    async def post(self, *args, **kwargs):
        self.raise405()
