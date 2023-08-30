from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.handlers.v1.context import (
    ContextAsyncHandler as ContextAsyncHandler_v1)


class ContextAsyncHandler(ContextAsyncHandler_v1, BaseHandler):
    def get_request_data(self):
        return {
            'type': self.get_arg('type', str),
            'uuid': self.get_arg('uuid', str)
        }

    async def get(self):
        """
        ---
        description: |
            Get context(upward hierarchy) for the object
            Required permission: CLUSTER SECRET
        tags: [assignments]
        summary: Internal API to get entity context for AUTH
        parameters:
        -   in: query
            name: type
            type: string
            enum: [organization, cloud_account, pool, employee, organization_bi,
                   webhook, rule, organization_constraint, report_import,
                   pool_alert, shareable_booking]
            required: true
        -   in: query
            name: uuid
            description: id of the object
            required: true
        responses:
            200: {description: Success with response}
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0173: Type or/and uuid is missing
                    - OE0174: Type is invalid
                    - OE0472: Object id has a removed associated organization/pool id
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
