import json

from auth.auth_server.controllers.login_options import (
    LoginOptionsAsyncController,
)
from auth.auth_server.handlers.v1.base import BaseAsyncCollectionHandler
from auth.auth_server.utils import run_task


class LoginOptionsAsyncHandler(BaseAsyncCollectionHandler):
    def _get_controller_class(self):
        return LoginOptionsAsyncController

    async def post(self, **url_params):
        """
        ---
        tags: [login_options]
        summary: Resolves login options
        description: |
            Resolves login options
            Required permission: NOT PROTECTED
        parameters:
        -   in: body
            name: body
            required: true
            schema:
                type: object
                properties:
                    email: {type: string, description: User email}
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        methods:
                            type: array
                            items:
                                type: string
                                enum: [password]
                                description: Methods offered to log in
                        sso:
                            type: object
                            properties:
                                state:
                                    type: string
                                    enum: [not_configured]
                                    description: State of SSO login
            400:
                description: |
                    Wrong arguments:
                    - OA0022: Unexpected parameters
                    - OA0032: Argument is not provided
                    - OA0033: Argument should be a string
        """
        data = self._request_body()
        res = await run_task(self.controller.resolve, **data)
        self.write(json.dumps(res))
