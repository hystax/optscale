import json
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler)
from rest_api.rest_api_server.controllers.restore_password import (
    RestorePasswordAsyncController)
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.utils import (
    check_string_attribute, is_email_format)
from rest_api.rest_api_server.utils import run_task


class RestorePasswordAsyncCollectionHandler(BaseAsyncCollectionHandler):

    def _get_controller_class(self):
        return RestorePasswordAsyncController

    def _validate_params(self, **kwargs):
        expected_params = ['email']
        unexpected = list(
            filter(lambda x: x not in expected_params, kwargs.keys()))
        if unexpected:
            message = ', '.join(unexpected)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            email = kwargs.get('email')
            check_string_attribute('email', email)
            if not is_email_format(email):
                raise WrongArgumentsException(Err.OE0218, ['Email', email])
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        super()._validate_params(**kwargs)

    async def post(self):
        """
        ---
        description: Initialize password restore flow
        tags: [restore_password]
        summary: Initialize password restore flow
        parameters:
        -   in: body
            name: body
            description: restore password parameters
            required: true
            schema:
                type: object
                properties:
                    email:
                        type: string
                        description: Contact email
                        required: true
                        example: example@mail.com
        responses:
            201:
                description: Flow initialized and email sent
                schema:
                    type: object
                    example:
                        status: ok
                        email: example@email.com
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument is not provided
                    - OE0218: Argument has incorrect format
                    - OE0416: Argument should not contain only whitespaces
        """
        data = self._request_body()
        self._validate_params(**data)
        email = data['email']
        await run_task(self.controller.restore_password, email=email)
        self.set_status(201)
        self.write(json.dumps({'status': 'ok', 'email': email}))
