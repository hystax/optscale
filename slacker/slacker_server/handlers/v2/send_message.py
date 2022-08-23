import json

from optscale_exceptions.http_exc import OptHTTPError

from slacker_server.controllers.send_message import SendMessageAsyncController
from slacker_server.exceptions import Err
from slacker_server.handlers.v2.base import BaseHandler


class SendMessageHandler(BaseHandler):
    async def validate_params(self, **kwargs):
        type_ = kwargs.pop('type', None)
        if type_ is None:
            raise OptHTTPError(400, Err.OS0010, ['type'])
        channel_id = kwargs.pop('channel_id', None)
        team_id = kwargs.pop('team_id', None)
        auth_user_id = kwargs.pop('auth_user_id', None)
        warning = kwargs.pop('warning', None)
        warning_params = kwargs.pop('warning_params', None)
        if channel_id is None and auth_user_id is None and team_id is None:
            raise OptHTTPError(400, Err.OS0014, [
                'channel_id with team_id', 'auth_user_id'])
        if channel_id and auth_user_id:
            raise OptHTTPError(400, Err.OS0015, ['channel_id', 'auth_user_id'])
        if team_id and auth_user_id:
            raise OptHTTPError(400, Err.OS0015, ['team_id', 'auth_user_id'])
        if (team_id and not channel_id) or (channel_id and not team_id):
            raise OptHTTPError(400, Err.OS0017, ['channel_id', 'team_id'])
        if warning and warning not in ['is_archived']:
            raise OptHTTPError(400, Err.OS0011, ['warning'])
        parameters = kwargs.pop('parameters', None)
        if not parameters or parameters and not isinstance(parameters, dict):
            raise OptHTTPError(400, Err.OS0011, ['parameters'])
        if kwargs:
            raise OptHTTPError(400, Err.OS0007, [','.join(kwargs.keys())])

    async def post(self, **kwargs):
        """
        ---
        description: |
            Send message to slack channel
            Required permission: CLUSTER_SECRET
        tags: [message]
        summary: Send message to slack channel
        parameters:
        -   in: body
            name: body
            description: message parameters
            required: true
            schema:
                type: object
                properties:
                    type:
                        type: string
                        enum: [alert, alert_added, alert_removed,
                               constraint_violated_alert,
                               constraint_alert_archived, env_acquired,
                               env_released, env_property_updated,
                               env_active_state_changed,
                               ]
                        description: type of message to pick template
                        required: True
                        example: alert
                    parameters:
                        type: object
                        description: >
                            set of fields differs from template to template
                        required: True
                        example: {
                            "pool_name": "Pool",
                            "pool_id": "eaa49639-a420-4e21-b3e3-1823f8e886d7",
                            "limit": 50,
                            "public_ip": "192.168.11.11",
                            "organization_id": "0243ff15-5d25-47b3-b9c9-332585292df8",
                            "organization_name": "Sunflower",
                            "threshold": "50",
                            "threshold_type": "percentage",
                            "based": "cost",
                            "cost": 121.11,
                            "currency": "USD"
                            }
                    warning:
                        type: string
                        enum: [is_archived]
                        required: False
                    warning_params:
                        type: object
                        description: >
                            set of fields for warning
                        required: False
                    channel_id:
                        type: string
                        description: target channel id
                        required: False
                        example: D01QNQHESM6
                    team_id:
                        type: string
                        description: target team id
                        required: False
                        example: T5CJ5JMH8
                    auth_user_id:
                        type: string
                        description: target auth user id
                        required: False
                        example: 02430e6b-6975-4535-8bc6-7a7b52938014
                example: {
                    parameters: {
                        "pool_name": "Pool",
                        "pool_id": "eaa49639-a420-4e21-b3e3-1823f8e886d7",
                        "limit": 50,
                        "public_ip": "192.168.11.11",
                        "organization_id": "0243ff15-5d25-47b3-b9c9-332585292df8",
                        "organization_name": "Sunflower",
                        "threshold": "50",
                        "threshold_type": "percentage",
                        "based": "cost",
                        "cost": 121.11,
                        "currency": "USD"
                        },
                    auth_user_id: 02430e6b-6975-4535-8bc6-7a7b52938014,
                    type: alert
                    }
        responses:
            201:
                description: Message sent
            400:
                description: |
                    Wrong arguments:
                    - OS0004: Incorrect request body received
                    - OS0007: Unexpected parameters
                    - OS0009: Database error
                    - OS0010: Argument not provided
                    - OS0011: Invalid parameters value
                    - OS0012: Duplicated parameters in path and body
                    - OS0014: channel_id with team_id or auth_user_id should be provided
                    - OS0015: channel_id and auth_user_id could not be provided at the same time
                    - OS0016: User not found
                    - OS0017: channel_id should provide only with team_id
                    - OS0019: Target slack channel is archived
            401:
                description: |
                    Unauthorized:
                    - OS0006: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OS0005: Bad secret
        security:
        - secret: []
        """
        self.check_cluster_secret()
        data = self._request_body()
        data.update(kwargs)
        await self.validate_params(**data)
        await self.controller.send_message(**data)
        self.write(json.dumps({}))
        self.set_status(201)

    def _get_controller_class(self):
        return SendMessageAsyncController
