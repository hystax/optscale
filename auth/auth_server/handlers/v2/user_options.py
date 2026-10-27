import json

from auth.auth_server.handlers.v1.base import (
    BaseAsyncAuthCollectionHandler, BaseAsyncAuthItemHandler,
    BaseSecretHandler)
from auth.auth_server.handlers.v2.base import BaseHandler as BaseHandler_v2
from auth.auth_server.exceptions import Err
from auth.auth_server.controllers.user_option import UserOptionsAsyncController
from auth.auth_server.utils import ModelEncoder, run_task
from tools.optscale_exceptions.http_exc import OptHTTPError


class UserOptionsAsyncCollectionHandler(BaseAsyncAuthCollectionHandler,
                                        BaseSecretHandler, BaseHandler_v2):
    def _get_controller_class(self):
        return UserOptionsAsyncController

    def prepare(self):
        pass

    async def post(self, user_id, **url_params):
        self.raise405()

    async def get(self, user_id):
        """
        ---
        description: |
            Returns a list of options specified for user.
            Required permission: TOKEN or CLUSTER_SECRET
        tags: [user_options]
        summary: List of options specified for user
        parameters:
        -   name: user_id
            in: path
            description: User ID
            required: true
            type: string
        -   name: with_values
            in: query
            description: Options with values
            required: false
            type: boolean
        responses:
            200:
                description: User options list
                schema:
                    type: object
                    properties:
                        options:
                            type: array
                            items:
                                type: object
                                properties:
                                    name:
                                        type: string
                                        description: option name
                                    value:
                                        type: string
                                        description: option value
            400:
                description: |
                    Wrong arguments:
                    - OA0063: Parameter should be true or false
            401:
                description: |
                    Unauthorized:
                    - OA0010: Token not found
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
                    - OA0024: User was not found
        security:
        - token: []
        - secret: []
        """
        args = {}
        if self.secret:
            self.check_cluster_secret()
        else:
            await self.check_token()
            args.update(self.token)
        with_values = self.get_arg('with_values', bool, False)
        args.update({'with_values': with_values})
        result = await run_task(
            self.controller.list, user_id, **args)
        option_dict = {'options': result}
        self.write(json.dumps(option_dict, cls=ModelEncoder))


class UserOptionsAsyncItemHandler(BaseAsyncAuthItemHandler,
                                  BaseSecretHandler):
    def _get_controller_class(self):
        return UserOptionsAsyncController

    def prepare(self):
        pass

    async def put(self, **url_params):
        self.raise405()

    async def get(self, user_id, option_name):
        """
        ---
        description: |
            Returns the option value for the specified user.
            Required permission: TOKEN or CLUSTER_SECRET
        tags: [user_options]
        summary: Option value for the specified user
        parameters:
        -   name: user_id
            in: path
            description: User ID
            required: true
            type: string
        -   name: option_name
            in: path
            description: option name
            required: true
            type: string
        responses:
            200:
                description: Option value
                schema:
                    type: object
                    properties:
                        value:
                            type: string
                            description: Option value
            401:
                description: |
                    Unauthorized:
                    - OA0010: Token not found
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
                    - OA0024: User was not found
        security:
        - token: []
        - secret: []
        """
        args = {}
        if self.secret:
            self.check_cluster_secret()
        else:
            await self.check_token()
            args.update(self.token)
        result = await run_task(
            self.controller.get_by_name, user_id, option_name, **args)
        value_dict = {'value': result}
        self.write(json.dumps(value_dict, cls=ModelEncoder))

    async def patch(self, user_id, option_name):
        """
        ---
        description: |
            Modifies or creates an option for a user
            Required permission: TOKEN or CLUSTER_SECRET
        tags: [user_options]
        summary: Modify/create option
        parameters:
        -   name: user_id
            in: path
            description: User ID
            required: true
            type: string
        -   name: option_name
            in: path
            description: Option name
            required: true
            type: string
        -   name: body
            in: body
            description: Option value
            required: true
            schema:
                type: object
                properties:
                    value:
                        type: string
                        description: Option value

        responses:
            200:
                description: Success (returns created/modified value)
                schema:
                type: object
                properties:
                    value:
                        type: string
                        description: Option value
            400:
                description: |
                    Wrong arguments:
                    - OA0032: Parameter is not provided
                    - OA0046: Value is not a valid json
                    - OA0048: Parameter should contain 1-256 characters
            401:
                description: |
                    Unauthorized:
                    - OA0010: Token not found
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
                    - OA0024: User was not found
        security:
        - token: []
        - secret: []
        """
        args = {}
        if self.secret:
            self.check_cluster_secret()
        else:
            await self.check_token()
            args.update(self.token)
        value_data = self._request_body().get('value')
        if not value_data:
            raise OptHTTPError(400, Err.OA0032, ['value'])
        result = await run_task(
            self.controller.patch, user_id, option_name, value_data, **args)
        value_dict = {'value': result}
        self.write(json.dumps(value_dict, cls=ModelEncoder))

    async def delete(self, user_id, option_name):
        """
        ---
        description: |
            Deletes the specified option for the user
            Required permission: TOKEN or CLUSTER_SECRET
        tags: [user_options]
        summary: Delete option
        parameters:
        -   name: user_id
            in: path
            description: User ID
            required: true
            type: string
        -   name: option_name
            in: path
            description: Option name
            required: true
            type: string
        responses:
            204:
                description: Success
            401:
                description: |
                    Unauthorized:
                    - OA0010: Token not found
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
                    - OA0003: UserOption not found
                    - OA0024: User was not found
        security:
        - token: []
        - secret: []
        """
        args = {}
        if self.secret:
            self.check_cluster_secret()
        else:
            await self.check_token()
            args.update(self.token)
        await run_task(
            self.controller.delete, user_id, option_name, **args)
        self.set_status(204)
