from auth_server.handlers.v1.digests import (
    DigestAsyncHandler as DigestAsyncHandler_v1)
from auth_server.handlers.v2.base import BaseHandler

# url_key: (<api parameter>, <type>, <repeated: bool>)
PAYLOAD_MAP_PARAMS = {
    'digest': ('digests', str, True)
}


class DigestAsyncHandler(DigestAsyncHandler_v1, BaseHandler):
    def get_request_data(self):
        return self.parse_url_params_into_payload(PAYLOAD_MAP_PARAMS)

    async def get(self):
        """
        ---
        tags: [digests]
        summary: Get token metadata
        description: |
            Gets token metadata by token digests (digest is md5(token))
            Required permission: CLUSTER SECRET
        parameters:
        -   name: digest
            in: query
            description: Token digest to get metadata from
            required: true
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
                        "DIGEST":
                            type: object
                            properties:
                                user_name: {type: string,
                                    description: "User name"}
                                ip: {type: string,
                                    description: "IP"}
                                token_created: {type: string,
                                    description: "Created time in
                                    datetime format"}
                                user_display_name: {type: string,
                                    description: "User display name"}
                                user_id: {type: string,
                                    description: "User id"}
                                valid_until: {type: integer,
                                    description: "Valid until timestamp"}
            400:
                description: |
                    Wrong arguments:
                    - OA0022: Unexpected parameters
                    - OA0046: Payload is not a valid json
                    - OA0047: Payload is malformed
                    - OA0050: Incorrect request body received
                    - OA0060: Invalid argument
            401:
                description: |
                    Unauthorized:
                    - OA0007: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OA0006: Bad secret
        security:
        - secret: []
        """
        await super().get()
