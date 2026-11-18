import json

from tools.optscale_exceptions.common_exc import WrongArgumentsException
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_telemetry import get_trace_headers

from auth.auth_server.controllers.user import UserAsyncController
from auth.auth_server.handlers.v1 import tokens as tokens_v1
from auth.auth_server.handlers.v1.base import BaseSecretHandler
from auth.auth_server.utils import run_task, ModelEncoder


class TokenAsyncCollectionHandler(tokens_v1.TokenAsyncCollectionHandler,
                                  BaseSecretHandler):
    def prepare(self):
        for name, value in get_trace_headers().items():
            self.set_header(name, value)

    async def post(self, **url_params):
        """
        ---
        tags: [tokens]
        summary: Obtain authorization token
        description: |
            Creates and returns an authorization token.
            When the user has a confirmed MFA method, or belongs to an
            organization that enforces MFA, the credentials check returns
            `202` with a login challenge instead. The challenge is completed
            by calling this endpoint again with `challenge_id` and `code`
            (`mfa_required`), or by enrolling a method with the challenge
            (`enrollment_required`).
            Required permission: NOT PROTECTED or CLUSTER SECRET
        parameters:
        -   in: body
            name: body
            description: User credentials
            required: true
            schema:
                properties:
                    password: {type: string, description: User password}
                    email: {type: string, description: User email}
                    verification_code:
                        type: integer
                        description: verification code from email
                    user_id:
                        type: string
                        description: can only be used with cluster secret
                    challenge_id:
                        type: string
                        description: |
                            login challenge to complete (with code)
                    code:
                        type: string
                        description: 6-digit MFA code (with challenge_id)
                    method_id:
                        type: string
                        description: |
                            MFA method the code belongs to, the default
                            method if not set (with challenge_id)
                type: object
        responses:
            201:
                description: Success
                schema:
                    type: object
                    properties:
                        created_at: {type: string}
                        user_id: {type: string}
                        user_email: {type: string}
                        valid_until: {type: string}
                        ip: {type: string}
                        digest: {type: string}
                        token: {type: string}
            202:
                description: Second factor required, login challenge
                schema:
                    type: object
                    properties:
                        challenge_id: {type: string}
                        user_id:
                            type: string
                            description: >-
                                needed to enroll a method
                                (enrollment_required)
                        state: {type: string,
                            enum: [mfa_required, enrollment_required]}
                        expires_at: {type: integer}
                        user_email: {type: string}
                        methods:
                            type: array
                            description: confirmed methods (empty for
                                enrollment_required)
                            items:
                                type: object
                                properties:
                                    id: {type: string}
                                    type: {type: string,
                                        enum: [totp, email]}
                                    label: {type: string}
                                    is_default: {type: boolean}
                                    confirmed: {type: boolean}
                        default_method_id: {type: string}
                        code_sent:
                            type: boolean
                            description: >-
                                true if the default method is email and the
                                code was sent with this response
                        attempts_left: {type: integer}
            400:
                description: |
                    Wrong arguments:
                    - OA0032: Argument is not provided
                    - OA0033: Argument should be a string
                    - OA0039: Email and/or password is not provided
                    - OA0061: Database error
            403:
                description: |
                    Forbidden:
                    - OA0037: Email or password is invalid
                    - OA0038: User is inactive
                    - OA0071: Email or verification_code is invalid
                    - OA0086: Verification code is invalid, attempts left
                    - OA0087: Too many failed attempts
                    - OA0088: An authentication method must be enrolled
                      first
                    - OA0090: Too many failed attempts, try again later
            404:
                description: |
                    Not found:
                    - OA0003: MFA method not found
                    - OA0043: User not found
                    - OA0085: Login challenge is invalid or expired
        security:
        - secret: []
        """
        data = self._request_body()
        data.update(url_params)
        data.update({'ip': self.get_ip_addr()})

        if self._check_secret(self.cluster_secret, raises=False):
            token = await run_task(
                self.controller.create_token_by_user_id, **data)
        else:
            try:
                await self._validate_params(**self._request_body())
            except WrongArgumentsException as ex:
                raise OptHTTPError.from_opt_exception(400, ex)
            token = await run_task(self.controller.create, **data)
            if 'challenge_id' in token:
                # a second factor is needed, no token issued yet
                self.set_status(202)
                self.write(json.dumps(token, cls=ModelEncoder))
                return
        user_ctl = UserAsyncController(self.session(), self._config)
        user, _ = await run_task(user_ctl.get, token['user_id'])
        token['user_email'] = user.email
        self.set_status(201)
        self.write(json.dumps(token, cls=ModelEncoder))
