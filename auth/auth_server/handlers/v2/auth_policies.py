import json

from auth.auth_server.controllers.auth_policy import (
    AuthPolicyAsyncController)
from auth.auth_server.handlers.v1.base import (
    BaseAsyncAuthCollectionHandler, BaseAsyncAuthItemHandler,
    BaseSecretHandler)
from auth.auth_server.handlers.v2.base import BaseHandler as BaseHandler_v2
from auth.auth_server.utils import ModelEncoder, run_task


class AuthPolicyAuthMixin:
    async def get_auth_args(self):
        """Cluster secret or user token: returns the controller token arg"""
        if self.secret:
            self.check_cluster_secret()
            return {'token': None}
        await self.check_token()
        return self.token


class AuthPolicyAsyncCollectionHandler(AuthPolicyAuthMixin,
                                       BaseAsyncAuthCollectionHandler,
                                       BaseSecretHandler, BaseHandler_v2):
    def _get_controller_class(self):
        return AuthPolicyAsyncController

    def prepare(self):
        pass

    async def get(self, **url_params):
        """
        ---
        description: |
            Returns the active authentication policies of a scope.
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [auth_policies]
        summary: List authentication policies
        parameters:
        -   name: scope_type
            in: query
            description: Scope type
            required: true
            type: string
            enum: [organization]
        -   name: scope_id
            in: query
            description: Scope ID (organization ID)
            required: true
            type: string
        responses:
            200:
                description: Authentication policies list
                schema:
                    type: object
                    properties:
                        auth_policies:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description: Policy ID}
                                    scope_type: {type: string,
                                        enum: [organization],
                                        description: Scope type}
                                    scope_id: {type: string,
                                        description: Scope ID}
                                    purpose: {type: string,
                                        enum: [mfa, sso],
                                        description: Policy purpose}
                                    created_at: {type: integer,
                                        description: Creation timestamp}
                                    deleted_at: {type: integer,
                                        description: Deletion timestamp}
            400:
                description: |
                    Wrong arguments:
                    - OA0022: Unexpected parameters
                    - OA0032: Parameter is not provided
                    - OA0060: Invalid parameter
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
                    - OA0028: Organization was not found
        security:
        - token: []
        - secret: []
        """
        args = await self.get_auth_args()
        args.update({k: self.get_arg(k, str) for k in self.request.arguments
                     if k != 'access_token'})
        result = await run_task(self.controller.list, **args)
        self.write(json.dumps({'auth_policies': [
            p.to_dict() for p in result]}, cls=ModelEncoder))

    async def post(self, **url_params):
        """
        ---
        description: |
            Creates an authentication policy. A policy with purpose `mfa`
            enforces MFA for all members of the organization.
            Required permission: EDIT_PARTNER or CLUSTER_SECRET
        tags: [auth_policies]
        summary: Create authentication policy
        parameters:
        -   in: body
            name: body
            required: true
            schema:
                type: object
                required: [scope_type, scope_id, purpose]
                properties:
                    scope_type: {type: string, enum: [organization],
                        description: Scope type}
                    scope_id: {type: string,
                        description: Scope ID (organization ID)}
                    purpose: {type: string, enum: [mfa, sso],
                        description: Policy purpose}
        responses:
            201:
                description: Created authentication policy
                schema:
                    type: object
                    properties:
                        id: {type: string, description: Policy ID}
                        scope_type: {type: string, enum: [organization],
                            description: Scope type}
                        scope_id: {type: string, description: Scope ID}
                        purpose: {type: string, enum: [mfa, sso],
                            description: Policy purpose}
                        created_at: {type: integer,
                            description: Creation timestamp}
                        deleted_at: {type: integer,
                            description: Deletion timestamp}
            400:
                description: |
                    Wrong arguments:
                    - OA0022: Unexpected parameters
                    - OA0032: Parameter is not provided
                    - OA0033: Parameter should be a string
                    - OA0050: Incorrect request body received
                    - OA0060: Invalid parameter
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
                    - OA0028: Organization was not found
            409:
                description: |
                    Conflict:
                    - OA0081: Authentication policy already exists
        security:
        - token: []
        - secret: []
        """
        args = await self.get_auth_args()
        data = self._request_body()
        data.pop('token', None)
        data.update(args)
        res = await run_task(self.controller.create, **data)
        self.set_status(201)
        self.write(res.to_json())


class AuthPolicyAsyncItemHandler(AuthPolicyAuthMixin,
                                 BaseAsyncAuthItemHandler,
                                 BaseSecretHandler, BaseHandler_v2):
    def _get_controller_class(self):
        return AuthPolicyAsyncController

    def prepare(self):
        pass

    async def get(self, *args, **kwargs):
        self.raise405()

    async def patch(self, *args, **kwargs):
        self.raise405()

    async def put(self, *args, **kwargs):
        self.raise405()

    async def delete(self, policy_id, **kwargs):
        """
        ---
        description: |
            Deletes an authentication policy (soft delete). Deleting the
            `mfa` policy makes MFA optional again for the organization.
            Required permission: EDIT_PARTNER or CLUSTER_SECRET
        tags: [auth_policies]
        summary: Delete authentication policy
        parameters:
        -   name: policy_id
            in: path
            description: Policy ID
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
                    - OA0003: AuthPolicy not found
        security:
        - token: []
        - secret: []
        """
        args = await self.get_auth_args()
        await run_task(self.controller.delete, policy_id, **args)
        self.set_status(204)
