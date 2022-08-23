import json

from optscale_exceptions.common_exc import WrongArgumentsException
from optscale_exceptions.http_exc import OptHTTPError

from auth_server.controllers.user import UserAsyncController
from auth_server.handlers.v1 import tokens as tokens_v1
from auth_server.handlers.v1.base import BaseSecretHandler
from auth_server.utils import run_task, ModelEncoder


class TokenAsyncCollectionHandler(tokens_v1.TokenAsyncCollectionHandler,
                                  BaseSecretHandler):
    def prepare(self):
        pass

    async def post(self, **url_params):
        """
        ---
        tags: [tokens]
        summary: Obtain authorization token
        description: |
            Creates and returns an authorization token
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
                    user_id:
                        type: string
                        description: can only be used with cluster secret
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
            400:
                description: |
                    Wrong arguments:
                    - OA0032: Argument is not provided
                    - OA0039: Email and/or password is not provided
                    - OA0061: Database error
            403:
                description: |
                    Forbidden:
                    - OA0037: Email or password is invalid
                    - OA0038: User is inactive
            404:
                description: |
                    Not found:
                    - OA0043: User not found
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
        user_ctl = UserAsyncController(self.session(), self._config)
        user, _ = await run_task(user_ctl.get, token['user_id'])
        token['user_email'] = user.email
        self.set_status(201)
        self.write(json.dumps(token, cls=ModelEncoder))
