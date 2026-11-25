from auth.auth_server.controllers.login_challenge import (
    LoginChallengeAsyncController)
from auth.auth_server.exceptions import Err
from auth.auth_server.handlers.v1.base import BaseAsyncCollectionHandler
from auth.auth_server.utils import run_task
from tools.optscale_exceptions.http_exc import OptHTTPError

# the only keys the body may contain: anything else is rejected here, before
# the body is expanded into keyword arguments (a key named like a positional
# argument of the controller or of run_task would raise a TypeError)
BODY_KEYS = ('challenge_id', 'method_id')


class LoginChallengeCodesAsyncHandler(BaseAsyncCollectionHandler):
    def _get_controller_class(self):
        return LoginChallengeAsyncController

    def _code_request(self):
        data = self._request_body()
        unexpected = [k for k in data if k not in BODY_KEYS]
        if unexpected:
            raise OptHTTPError(400, Err.OA0022, [', '.join(unexpected)])
        return data

    async def post(self, **url_params):
        """
        ---
        tags: [login_challenges]
        summary: Send the e-mail code of a login challenge
        description: |
            Sends (again) the e-mail code during the MFA step: the user asks
            for the code again ("Resend") or switches to the e-mail method
            when the default one is an authenticator app. The login
            challenge is the credential, no token is needed; it is sent in
            the body, never in the URL. A code can be sent once a minute per
            user, the previous code is invalidated. Sending a code does not
            use an attempt of the challenge.
            Required permission: NOT PROTECTED (valid `mfa_required` login
            challenge)
        parameters:
        -   in: body
            name: body
            required: true
            schema:
                type: object
                required: [challenge_id]
                properties:
                    challenge_id:
                        type: string
                        description: Login challenge ID (state mfa_required)
                    method_id:
                        type: string
                        description: >-
                            confirmed e-mail method of the user; optional,
                            a user has a single e-mail method
        responses:
            204:
                description: Code sent
            400:
                description: |
                    Wrong arguments:
                    - OA0022: Unexpected parameters
                    - OA0032: challenge_id is not provided
                    - OA0033: Parameter should be a string
                    - OA0050: Incorrect request body received
                    - OA0060: Invalid method_id (not a confirmed e-mail
                      method of the user)
            403:
                description: |
                    Forbidden:
                    - OA0072: The verification code can be generated once
                      in a minute
            404:
                description: |
                    Not found:
                    - OA0085: Login challenge is invalid or expired (also
                      consumed, locked or enrollment_required)
            503:
                description: E-mail service unavailable
        """
        data = self._code_request()
        await run_task(self.controller.send_code,
                       challenge_id=data.get('challenge_id'),
                       method_id=data.get('method_id'))
        self.set_status(204)
