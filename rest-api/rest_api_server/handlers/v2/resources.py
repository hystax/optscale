import json
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.resources import (
    ResourcesAsyncHandler as ResourcesAsyncHandler_v1)


class ResourcesAsyncHandler(ResourcesAsyncHandler_v1, BaseHandler):
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
        description: |
            Get info for the object
            Required permission: CLUSTER SECRET
        tags: [assignments]
        summary: Internal API to get object name for AUTH
        parameters:
        -   in: query
            name: organization
            description: organization ids
            collectionFormat: multi
            type: array
            items:
                type: string
            required: true
        -   in: query
            name: pool
            description: pool ids
            collectionFormat: multi
            type: array
            items:
                type: string
            required: true
        responses:
            200: {description: Success with response}
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid parameter format
            401: {description: "Unauthorized: \n\n
                - OE0237: This resource requires authorization"}
            403: {description: "Forbidden: \n\n
                - OE0236: Bad secret"}
        security:
        - secret: []
        """
        await super().get()
