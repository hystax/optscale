import json

import auth.auth_server.handlers.v1.types as types_v1
from auth.auth_server.controllers.type import TypeAsyncController
from auth.auth_server.handlers.v1.base import BaseSecretHandler
from auth.auth_server.utils import as_dict, ModelEncoder


class TypeAsyncItemHandler(types_v1.TypeAsyncItemHandler):

    async def get(self, id, **kwargs):
        """
        ---
        x-hidden: true
        tags: [types]
        summary: Get type
        description: |
            Gets type by id
            Required permission: TOKEN
        parameters:
        -   name: id
            in: path
            description: ID of type to return
            required: true
            type: string
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        id: {type: integer,
                            description: "Unique identifier of the
                            Type"}
                        name: {type: string,
                            description: "Name of Type"}
                        parent_id: {type: integer,
                            description: "Parent (recursive) unique
                            identifier of the
                            type"}
                        assignable: {type: boolean,
                            description: "This type could be
                            assigned as user scope"}
                        created_at: {type: integer,
                            description: "Created timestamp
                            (service field)"}
                        deleted_at: {type: integer,
                            description: "Deleted timestamp
                            (service field)"}
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
                    - OA0056: Type with id not found
        security:
        - token: []
        """
        await super().get(id, **kwargs)


class TypeAsyncCollectionHandler(BaseSecretHandler):
    def _get_controller_class(self):
        return TypeAsyncController

    async def get(self, **kwargs):
        """
        ---
        x-hidden: true
        tags: [types]
        summary: List types
        description: |
            Gets a list of types
            Required permission: CLUSTER_SECRET
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        types:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: integer,
                                        description: "Unique identifier of the
                                        Type"}
                                    name: {type: string,
                                        description: "Name of Type"}
                                    parent_id: {type: integer,
                                        description: "Parent (recursive) unique
                                        identifier of the
                                        type"}
                                    assignable: {type: boolean,
                                        description: "This type could be
                                        assigned as user scope"}
                                    created_at: {type: integer,
                                        description: "Created timestamp
                                        (service field)"}
                                    deleted_at: {type: integer,
                                        description: "Deleted timestamp
                                        (service field)"}
            401:
                description: |
                    Unauthorized:
                    - OA0007: This resource requires authorization
                    - OA0023: Unauthorized
                    - OA0062: This resource requires an authorization token
            403:
                description: |
                    Forbidden:
                    - OA0006: Bad secret
        security:
        - secret: []
        """
        self.check_cluster_secret()
        types = await self.controller.list(by_secret=True, **kwargs)
        types_dict = {'types': [
            as_dict(type_) for type_ in types]}
        self.write(json.dumps(types_dict, cls=ModelEncoder))
