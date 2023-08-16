import auth.auth_server.handlers.v1.authorization_userlist as userlist_v1


class AuthorizationUserlistAsyncHandler(userlist_v1.AuthorizationUserlistAsyncHandler):

    async def post(self):
        """
        ---
        tags: [authorization]
        summary: Check permissions for users
        description: |
            Checks permissions by user ids
            Required permission: CLUSTER SECRET
        parameters:
        -   in: body
            name: body
            description: Data
            required: true
            schema:
                type: object
                properties:
                    users:
                        type: array
                        description: User id list
                        items: {type: string}
                    actions:
                        type: array
                        description: Action name list
                        items: {type: string}
                    scope_type: {type: string,
                        description: "Scope type"}
                    scope_id: {type: string,
                        description: "Scope id"}
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        USER_ID:
                            type: array
                            items:
                                type: string
                                description: Action name
            400:
                description: |
                    Wrong arguments:
                    - OA0050: Incorrect request body received
                    - OA0031: Argument is required
                    - OA0055: Argument should be list
                    - OA0054: Invalid scope_id
                    - OA0022: Unexpected parameters
                    - OA0020: Invalid type
            401:
                description: |
                    Unauthorized:
                    - OA0007: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OA0006: Bad secret
            404:
                description: |
                    Not found:
                    - OA0003: Resource not found
        security:
        - secret: []
        """
        await super().post()
