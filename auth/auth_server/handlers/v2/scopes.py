from tornado import gen

import auth.auth_server.handlers.v1.scopes as scopes_v1


class ScopeAsyncHandler(scopes_v1.ScopeAsyncHandler):
    async def get(self, **kwargs):
        """
        ---
        x-hidden: true
        tags: [scopes]
        summary: List scopes
        description: |
            Gets available scopes for action
            Required permission: CREATE_USER or CREATE_ROLE or ASSIGN_USER
        parameters:
        -   name: action
            in: query
            description: "Possible actions: create_user, assign_user,
                create_role"
            required: true
            type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        scopes:
                            type: array
                            items:
                                type: object
                                properties:
                                    scope_id: {type: string,
                                        description: Unique scope id}
                                    scope_type: {type: string,
                                        description: Scope type}
                                    scope_type_id: {type: integer,
                                        description: Scope type id}
                                    assignable: {type: boolean,
                                        description: "Is assignable?"}
                                    scope_name: {type: string,
                                        description: Scope name}
            400:
                description: |
                    Wrong arguments:
                    - OA0009: Invalid action provided
                    - OA0008: Should provide user id and role id
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
                    - OA0024: User was not found
                    - OA0025: Role was not found
        security:
        - token: []
        """
        await super().get(**kwargs)
