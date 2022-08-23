import json

from auth_server.handlers.v2.base import BaseHandler
from auth_server.handlers.v1.actions import (
    ActionAsyncHandler as ActionAsyncHandler_v1)


class ActionAsyncHandler(ActionAsyncHandler_v1, BaseHandler):
    def get_request_data(self):
        payload = []
        for k, v in self.request.arguments.items():
            items = self.get_arg(k, str, repeated=True)
            for item in items:
                payload.append((k, item))
        return {
            "payload": json.dumps(payload)
        }

    async def get(self):
        """
        ---
        tags: [actions]
        summary: Get actions
        description: |
            Gets allowed actions for current user
            Required permission: TOKEN
        parameters:
        -   name: organization
            in: query
            description: organization id for which actions must be returned
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: cloud_account
            in: query
            description: cloud_account id for which actions must be returned
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: employee
            in: query
            description: employee id for which actions must be returned
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: pool
            in: query
            description: pool id for which actions must be returned
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: report_import
            in: query
            description: report_import id for which actions must be returned
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: cloud_resource
            in: query
            description: cloud_resource id for which actions must be returned
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: pool_alert
            in: query
            description: pool_alert id for which actions must be returned
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: pool_policy
            in: query
            description: pool_policy id for which actions must be returned
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: resource_constraint
            in: query
            description: resource_constraint id for which actions must be returned
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: rule
            in: query
            description: rule id for which actions must be returned
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        allowed_actions:
                            type: object
                            properties:
                                SCOPE_UUID:
                                    type: array
                                    items:
                                        type: string
                                        description: Action name
            400:
                description: |
                    Wrong arguments:
                    - OA0013: Malformed payload
                    - OA0014: Actions should be non-empty list
                    - OA0020: Invalid type
                    - OA0022: Unexpected parameters
                    - OA0050: Incorrect request body received
                    - OA0066: Object id has a removed associated organization/pool id
            401:
                description: |
                    Unauthorized:
                    - OA0010: Token not found
                    - OA0011: Invalid token
                    - OA0023: Unauthorized
                    - OA0062: This resource requires an authorization token
            404:
                description: |
                    Not found:
                    - OA0028: Item with id not found
        security:
        - token: []
        """
        await super().get()
