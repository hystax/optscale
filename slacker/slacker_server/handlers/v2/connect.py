from tools.optscale_exceptions.http_exc import OptHTTPError

from slacker.slacker_server.controllers.connect import ConnectAsyncController
from slacker.slacker_server.exceptions import Err
from slacker.slacker_server.handlers.v2.base import BaseHandler


class ConnectHandler(BaseHandler):
    async def validate_params(self, **kwargs):
        secret = kwargs.pop('secret', None)
        if secret is None:
            raise OptHTTPError(400, Err.OS0010, ['secret'])
        if kwargs:
            raise OptHTTPError(400, Err.OS0007, [','.join(kwargs.keys())])

    async def post(self, **kwargs):
        """
        ---
        description: |
            Connect slack user to OptScale auth user
            Required permission: TOKEN
        tags: [connect]
        summary: Connect slack user to OptScale auth user
        parameters:
        -   in: body
            name: body
            description: Secret
            required: true
            schema:
                type: object
                properties:
                    secret:
                        type: string
                        description: secret to find relevant slack user
                        required: True
                        example: 59c0588c-9369-4a11-a596-fd8d3ee7b65e
        responses:
            201:
                description: Connection created
                schema:
                    type: object
                    example:
                        slack_user_id: U5CJ6SCH0
                        auth_user_id: 081dda91-d678-48b6-9e11-6a52216f1b5f
                        secret: 59c0588c-9369-4a11-a596-fd8d3ee7b65e
                        slack_channel_id: D01PZ069UD8
                        organization_id: null
                        employee_id: null
                        created_at: 1587029026
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OS0011: Invalid secret
                    - OS0009: Database error
                    - OS0012: Duplicated parameters in path and body
                    - OS0004: Incorrect request body received
                    - OS0013: Slack user already connected
                    - OS0007: Unexpected parameters
                    - OS0010: Secret is not provided
            401:
                description: |
                    Unauthorized:
                    - OS0006: This resource requires authorization
                    - OS0018: Unauthorized
        security:
        - token: []
        """
        await self.check_self_auth()
        data = self._request_body()
        data.update(kwargs)
        await self.validate_params(**data)
        user = await self.controller.connect(**data)
        self.write(user.to_json())
        self.set_status(201)

    def _get_controller_class(self):
        return ConnectAsyncController
