import json

from auth.auth_server.controllers.mfa_method import MfaMethodAsyncController
from auth.auth_server.handlers.v1.base import (
    BaseAsyncAuthCollectionHandler, BaseAsyncAuthItemHandler,
    BaseSecretHandler)
from auth.auth_server.handlers.v2.base import BaseHandler as BaseHandler_v2
from auth.auth_server.utils import ModelEncoder, run_task


class MfaMethodAuthMixin:
    async def get_auth_args(self, data):
        """
        Cluster secret or owner's token: returns the controller token arg.
        With challenge_id in the body the login challenge is the credential,
        the controller checks it.
        """
        if data.get('challenge_id') is not None:
            return {'token': None}
        if self.secret:
            self.check_cluster_secret()
            return {'token': None}
        await self.check_token()
        return self.token

    def get_body(self):
        data = self._request_body()
        data.pop('token', None)
        return data


class MfaMethodAsyncCollectionHandler(MfaMethodAuthMixin,
                                      BaseAsyncAuthCollectionHandler,
                                      BaseSecretHandler, BaseHandler_v2):
    def _get_controller_class(self):
        return MfaMethodAsyncController

    def prepare(self):
        pass

    async def get(self, user_id, **url_params):
        self.raise405()

    async def post(self, user_id, **url_params):
        """
        ---
        description: |
            Starts the enrollment of an MFA method. The method is created
            pending and becomes active only after it is confirmed with a
            code. For `totp` the response includes the shared `secret` and
            the `otpauth_uri` (QR code) - this is the only time they are
            returned. For `email` a code is sent to the user's address and
            the label is set to the masked address. Restarting an
            unconfirmed enrollment replaces it.
            Required permission: TOKEN of the user, CLUSTER_SECRET or
            `challenge_id` of an `enrollment_required` login challenge of
            the user (enforced user signing in without a method)
        tags: [mfa_methods]
        summary: Start MFA method enrollment
        parameters:
        -   name: user_id
            in: path
            description: User ID
            required: true
            type: string
        -   in: body
            name: body
            required: true
            schema:
                type: object
                required: [type]
                properties:
                    type: {type: string, enum: [totp, email],
                        description: Method type}
                    label: {type: string,
                        description: Free text (device info), totp only}
                    challenge_id:
                        type: string
                        description: >-
                            enrollment_required login challenge, instead of
                            a token
        responses:
            201:
                description: Pending MFA method
                schema:
                    type: object
                    properties:
                        id: {type: string, description: Method ID}
                        user_id: {type: string, description: User ID}
                        type: {type: string, enum: [totp, email],
                            description: Method type}
                        label: {type: string, description: Method label}
                        is_default: {type: boolean,
                            description: Always false while pending}
                        confirmed: {type: boolean,
                            description: Always false while pending}
                        confirmed_at: {type: integer,
                            description: Always 0 while pending}
                        created_at: {type: integer,
                            description: Creation timestamp}
                        deleted_at: {type: integer,
                            description: Deletion timestamp}
                        secret: {type: string,
                            description: TOTP shared secret, totp only}
                        otpauth_uri: {type: string,
                            description: otpauth URI for the QR code,
                                totp only}
            400:
                description: |
                    Wrong arguments:
                    - OA0022: Unexpected parameters
                    - OA0032: Parameter is not provided
                    - OA0033: Parameter should be a string
                    - OA0048: Parameter should contain 1-256 characters
                    - OA0050: Incorrect request body received
                    - OA0060: Invalid parameter
                    - OA0065: Parameter should not contain only whitespaces
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
                    - OA0072: The verification code can be generated once
                      in a minute (email)
                    - OA0089: An authentication method is already enrolled
                      (challenge_id)
            404:
                description: |
                    Not found:
                    - OA0024: User was not found
                    - OA0085: Login challenge is invalid or expired
            409:
                description: |
                    Conflict:
                    - OA0082: Authentication method of type already exists
            503:
                description: E-mail service unavailable (email)
        security:
        - token: []
        - secret: []
        """
        data = self.get_body()
        data.update(await self.get_auth_args(data))
        res = await run_task(self.controller.create, user_id, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))


class MfaMethodConfirmAsyncHandler(MfaMethodAuthMixin,
                                   BaseAsyncAuthItemHandler,
                                   BaseSecretHandler, BaseHandler_v2):
    def _get_controller_class(self):
        return MfaMethodAsyncController

    def prepare(self):
        pass

    async def get(self, *args, **kwargs):
        self.raise405()

    async def patch(self, *args, **kwargs):
        self.raise405()

    async def delete(self, *args, **kwargs):
        self.raise405()

    async def post(self, user_id, method_id, **url_params):
        """
        ---
        description: |
            Confirms a pending MFA method with a code from the authenticator
            app (totp) or from the e-mail (email). The first confirmed
            method becomes the default one. A TOTP code is accepted only
            once.
            Required permission: TOKEN of the user, CLUSTER_SECRET or
            `challenge_id` of an `enrollment_required` login challenge of
            the user (enforced user signing in without a method)
        tags: [mfa_methods]
        summary: Confirm MFA method enrollment
        parameters:
        -   name: user_id
            in: path
            description: User ID
            required: true
            type: string
        -   name: method_id
            in: path
            description: MFA method ID
            required: true
            type: string
        -   in: body
            name: body
            required: true
            schema:
                type: object
                required: [code]
                properties:
                    code: {type: string, description: 6-digit code}
                    challenge_id:
                        type: string
                        description: >-
                            enrollment_required login challenge, instead of
                            a token; the challenge is consumed and a token
                            is returned
        responses:
            200:
                description: Confirmed MFA method
                schema:
                    type: object
                    properties:
                        id: {type: string, description: Method ID}
                        user_id: {type: string, description: User ID}
                        type: {type: string, enum: [totp, email],
                            description: Method type}
                        label: {type: string, description: Method label}
                        is_default: {type: boolean,
                            description: true if it is the first method}
                        confirmed: {type: boolean, description: true}
                        confirmed_at: {type: integer,
                            description: Confirmation timestamp}
                        created_at: {type: integer,
                            description: Creation timestamp}
                        deleted_at: {type: integer,
                            description: Deletion timestamp}
            201:
                description: |
                    Challenge mode: confirmed method and authorization token
                schema:
                    type: object
                    properties:
                        method: {type: object,
                            description: Confirmed MFA method}
                        token:
                            type: object
                            properties:
                                created_at: {type: string}
                                user_id: {type: string}
                                user_email: {type: string}
                                valid_until: {type: string}
                                ip: {type: string}
                                digest: {type: string}
                                token: {type: string}
            400:
                description: |
                    Wrong arguments:
                    - OA0022: Unexpected parameters
                    - OA0032: Parameter is not provided
                    - OA0033: Parameter should be a string
                    - OA0050: Incorrect request body received
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
                    - OA0083: Invalid authentication code (token or
                      secret)
                    - OA0086: Verification code is invalid, attempts left
                      (challenge_id)
                    - OA0087: Too many failed attempts, sign in again
                      (challenge_id)
                    - OA0089: An authentication method is already enrolled
                      (challenge_id)
                    - OA0090: Too many failed attempts, try again later
                      (challenge_id)
            404:
                description: |
                    Not found:
                    - OA0003: MFA method not found (or enrollment expired)
                    - OA0024: User was not found
                    - OA0085: Login challenge is invalid or expired
            409:
                description: |
                    Conflict:
                    - OA0084: Authentication method is already confirmed
        security:
        - token: []
        - secret: []
        """
        data = self.get_body()
        data.update(await self.get_auth_args(data))
        if data.get('challenge_id') is not None:
            data['ip'] = self.get_ip_addr()
        res = await run_task(self.controller.confirm, user_id, method_id,
                             **data)
        if isinstance(res, dict):
            # challenge mode: method confirmed and token issued
            self.set_status(201)
            self.write(json.dumps(res, cls=ModelEncoder))
        else:
            self.write(res.to_json())
