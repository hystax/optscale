import json

from auth.auth_server.controllers.signin import SignInAsyncController
from auth.auth_server.handlers.v1.base import BaseAsyncCollectionHandler
from auth.auth_server.utils import ModelEncoder, run_task


class SignInAsyncHandler(BaseAsyncCollectionHandler):
    def _get_controller_class(self):
        return SignInAsyncController

    async def post(self, **url_params):
        """
        ---
        tags: [sign_in]
        summary: Sign in using third party provider
        description: |
            Sign in using third party provider
            Required permission: NOT PROTECTED
        parameters:
        -   in: body
            name: body
            required: true
            schema:
                type: object
                properties:
                    provider: {type: string, enum: [google, microsoft],
                        description: "Third party provider to validate token"}
                    token: {type: string,
                        description: "Third party token"}
                    tenant_id: {type: string, required: false,
                        description: "Azure AD tenant id (only for microsoft provider)"}
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
            400:
                description: |
                    Wrong arguments:
                    - OA0022: Unexpected parameters
                    - OA0031: Argument is required
                    - OA0032: Argument is not provided
                    - OA0033: Argument should be a string
                    - OA0048: Wrong argument length
                    - OA0050: Incorrect request body received
                    - OA0061: Database error
                    - OA0065: Argument should not contain only whitespaces
                    - OA0067: Invalid provider
                    - OA0070: Registration with domain is prohibited. Please use your business email for registration
            403:
                description: |
                    Forbidden:
                    - OA0012: Forbidden
        """
        data = self._request_body()
        data.update(url_params)
        data.update({'ip': self.get_ip_addr()})
        data.update({'redirect_uri': self.request.headers.get('Origin')})
        await self._validate_params(**data)
        res = await run_task(self.controller.signin, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))
