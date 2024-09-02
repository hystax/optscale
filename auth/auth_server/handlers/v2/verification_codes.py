import json

from auth.auth_server.controllers.verification_code import (
    VerificationCodeAsyncController)
from auth.auth_server.handlers.v1.base import (BaseAsyncCollectionHandler,
                                               BaseSecretHandler)
from auth.auth_server.utils import ModelEncoder, run_task


class VerificationCodeAsyncHandler(BaseAsyncCollectionHandler,
                                   BaseSecretHandler):
    def _get_controller_class(self):
        return VerificationCodeAsyncController

    async def post(self, **url_params):
        """
        ---
        tags: [verification_code]
        summary: Creates verification code for user
        description: |
            Creates verification code for user
            Required permission: CLUSTER_SECRET
        parameters:
        -   in: body
            name: body
            required: true
            schema:
                type: object
                properties:
                    email: {type: string, description: User email}
                    code: {type: string, description: verification code}
        responses:
            201:
                description: Success
                schema:
                    type: object
                    properties:
                        created_at: {type: string}
                        email: {type: string}
                        valid_until: {type: string}
            400:
                description: |
                    Wrong arguments:
                    - OA0021: Immutable parameters
                    - OA0022: Unexpected parameters
                    - OA0032: Argument is not provided
                    - OA0037: Email or password is invalid
                    - OA0050: Incorrect request body received
                    - OA0061: Database error
            401:
                description: |
                    Unauthorized:
                    - OA0007: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OA0006: Bad secret
                    - OA0012: Forbidden
                    - OA0072: Can be generated once in a minute
        """
        self.check_cluster_secret()
        data = self._request_body()
        await self._validate_params(**data)
        res = await run_task(self.controller.create, **data)
        self.set_status(201)
        self.write(json.dumps(res.to_dict(), cls=ModelEncoder))
