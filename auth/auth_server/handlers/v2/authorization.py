from tornado import gen

import auth_server.handlers.v1.authorization as authorization_v1


class AuthorizationAsyncHandler(authorization_v1.AuthorizationAsyncHandler):
    async def post(self, **url_params):
        """
        ---
        tags: [authorization]
        summary: Check permission
        description: |
            Checks for permission
            Required permission: TOKEN
        parameters:
        -   in: body
            name: body
            description: Permission to check
            required: true
            schema:
                type: object
                properties:
                    action: {type: string,
                        description: "Action (e.g. MANAGE_POOLS)"}
                    resource_type: {type: string,
                        description: "Resource type (e.g. organization)"}
                    uuid: {type: string,
                        description: "Scope unique id"}
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        assignments:
                            type: array
                            items:
                                type: object
                                properties:
                                    resource: {type: string,
                                        description: "Scope id"}
                                    id: {type: string,
                                        description: "Assignment id"}
                                    user: {type: string,
                                        description: "User name"}
                                    type: {type: string,
                                        description: "User type (scope of the
                                        user) (Possible types: root,
                                        organization, pool)"}
                                    role: {type: string,
                                        description: "User role"}
                        status: {type: string,
                            description: "Always ok, otherwise error 403 will
                            be raised"}
            400:
                description: |
                    Wrong arguments:
                    - OA0050: Incorrect request body received
                    - OA0031: Argument is required
                    - OA0054: Invalid scope_id
                    - OA0022: Unexpected parameters
                    - OA0061: Database error
                    - OA0027: Resource not found
            401:
                description: |
                    Unauthorized:
                    - OA0010: Token not found
                    - OA0011: Invalid token
                    - OA0023: Unauthorized
                    - OA0062: This resource requires an authorization token
            403:
                description: |
                    Forbidden:
                    - OA0012: Forbidden!
            404:
                description: |
                    Not found:
                    - OA0028: Item was not found
        security:
        - token: []
        """
        await super().post(**url_params)
