from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.auth_hierarchy import (
    AuthHierarchyAsyncHandler as AuthHierarchyAsyncHandler_v1)


class AuthHierarchyAsyncHandler(AuthHierarchyAsyncHandler_v1, BaseHandler):
    async def get(self):
        """
        ---
        description: |
            Get downward(auth hierarchy) for the object
            Required permission: CLUSTER SECRET
        tags: [assignments]
        summary: Internal API to get auth hierarchy for AUTH
        parameters:
        -   in: query
            name: type
            description: type of the object (root|organization|pool)
            required: true
        -   in: query
            name: scope_id
            description: id of the object
            required: false
        responses:
            200:
                description: Success with response
            400:
                description: |
                    Wrong arguments:
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0173: Type or/and uuid is missing
                    - OE0174: Type is invalid
                    - OE0456: Duplicate path parameters in the request body
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
        security:
        - secret: []
        """
        await super().get()
