import json

from optscale_exceptions.common_exc import ForbiddenException
from optscale_exceptions.http_exc import OptHTTPError
from rest_api_server.controllers.cloud_account import CloudAccountAsyncController
from rest_api_server.handlers.v1.base_async import (BaseAsyncCollectionHandler)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task


class CloudAccountVerifyHandler(BaseAsyncCollectionHandler,
                                BaseAuthHandler):
    def _get_controller_class(self):
        return CloudAccountAsyncController

    async def post(self, **url_params):
        """
        ---
        description: |
            Check cloud account
            Required permission: TOKEN
        tags: [cloud_account_verify]
        summary: Check cloud account config
        parameters:
        -   in: body
            name: body
            description: Cloud account to validate
            required: true
            schema:
                type: object
                properties:
                    type:
                        type: string
                        enum: [aws_cnr, azure_cnr]
                        description: cloud account type
                    config:
                        type: string
                        description: >
                            Json encoded string with credentials to access cloud
        responses:
            201:
                description: Success
            400:
                description: |
                    Wrong arguments:
                    - OE0216: Argument is not provided
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong number of characters
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer value
                    - OE0226: Wrong boolean value
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            503:
                description: |
                    Not found:
                    - OE0455: Cloud connection error: Could not connect to cloud by subscription: connection timed out.
        security:
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        try:
            await run_task(self.controller.verify, data)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        self.set_status(200)
        self.write(json.dumps({'status': 'ok'}))
