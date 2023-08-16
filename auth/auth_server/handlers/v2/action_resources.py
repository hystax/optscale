import json
from auth.auth_server.utils import ModelEncoder
from auth.auth_server.handlers.v2.base import BaseHandler
from auth.auth_server.handlers.v1.base import BaseSecretHandler
from auth.auth_server.handlers.v1.action_resources import (
    ActionResourcesAsyncHandler as ActionResourcesAsyncHandler_v1)
from auth.auth_server.controllers.action_resource import (
    ActionResourceAsyncController)
from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  NotFoundException)
from tools.optscale_exceptions.http_exc import OptHTTPError

# url_key: (<api parameter>, <type>, <repeated: bool>)
PAYLOAD_MAP_PARAMS = {
    'action': ('actions', str, True),
    'assignable_only': ('assignable_only', bool, False)
}


class ActionResourcesAsyncHandler(ActionResourcesAsyncHandler_v1, BaseHandler):
    def get_request_data(self):
        return self.parse_url_params_into_payload(PAYLOAD_MAP_PARAMS)

    async def get(self):
        """
        ---
        tags: [action_resources]
        summary: Get action resources
        description: |
            Gets resources of specified actions
            Required permission: TOKEN
        parameters:
        -   name: action
            in: query
            description: Action name
            required: true
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: assignable_only
            in: query
            description: Include only assignable
            required: false
            type: boolean
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        action_resources:
                            type: array
                            items:
                                type: object
                                properties:
                                    ACTION:
                                        type: array
                                        items:
                                            type: array
                                            items:
                                                type: string
                                                description: "First array
                                                    element is scope type,
                                                    second is scope_id"
            400:
                description: |
                    Wrong arguments:
                    - OA0014: Actions should be non-empty list
                    - OA0046: Payload is not a valid json
                    - OA0047: Payload is malformed
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
        security:
        - token: []
        """
        await super().get()


class UserActionResourcesAsyncHandler(BaseSecretHandler, BaseHandler):
    def get_request_data(self):
        return self.parse_url_params_into_payload(PAYLOAD_MAP_PARAMS)

    def _get_controller_class(self):
        return ActionResourceAsyncController

    async def get(self, user_id):
        """
        ---
        tags: [action_resources]
        summary: Get action resources by user id
        description: |
            Gets resources of specified actions
            Required permission: CLUSTER_SECRET
        parameters:
        -   name: user_id
            in: url
            description: Specified user_id
            required: true
            type: string
        -   name: action
            in: query
            description: Action name
            required: true
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: assignable_only
            in: query
            description: Include only assignable
            required: false
            type: boolean
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        action_resources:
                            type: array
                            items:
                                type: object
                                properties:
                                    ACTION:
                                        type: array
                                        items:
                                            type: array
                                            items:
                                                type: string
                                                description: "First array
                                                    element is scope type,
                                                    second is scope_id"
            400:
                description: |
                    Wrong arguments:
                    - OA0014: Actions should be non-empty list
                    - OA0046: Payload is not a valid json
                    - OA0047: Payload is malformed
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
                    - OA0012: Forbidden!
            404:
                description: |
                    Not found:
                    - OA0024: User was not found
        security:
        - secret: []
        """
        self.check_cluster_secret()
        data = self.get_request_data()
        data.update({'user_id': user_id})
        try:
            res = await self.controller.action_resources(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        self.write(json.dumps({'action_resources': res}, cls=ModelEncoder))


class BulkActionResourcesAsyncHandler(BaseSecretHandler, BaseHandler):
    def get_request_data(self):
        return {
            'user_ids': self.get_arg('user_id', str, repeated=True),
            'actions': self.get_arg('action', str, repeated=True),
            'assignable_only': self.get_arg('assignable_only', bool,
                                            default=True),
        }

    def _get_controller_class(self):
        return ActionResourceAsyncController

    async def get(self):
        """
        ---
        tags: [action_resources]
        summary: Get action resources in bulk
        description: |
            Gets actions allowed for resources for multiple users
            Required permission: CLUSTER_SECRET
        parameters:
        -   name: user_id
            in: query
            description: User id
            required: true
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: action
            in: query
            description: Action name
            required: true
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: assignable_only
            in: query
            description: Include only assignable
            required: false
            type: boolean
        responses:
            200:
                description: Success
                schema:
                    type: object
                    example:
                        175bedaa-65cf-4802-a287-b9858588345f:
                        -   MANAGE_RESOURCES:
                            -   ['pool', 'baf1ccda-2252-4c1a-b789-525be0a8f177']
                            -   ['organization', 'a3666b42-fcc0-44a9-a184-068504b6fda4']
                        -   MANAGE_OWN_RESOURCES:
                            -   ['pool', 'baf1ccda-2252-4c1a-b789-525be0a8f177']
                            -   ['organization', 'a3666b42-fcc0-44a9-a184-068504b6fda4']
                        69ee3625-f559-4079-9aa8-8a6150051a4e:
                        -   MANAGE_RESOURCES: []
                        -   MANAGE_OWN_RESOURCES:
                            -   ['pool', 'baf1ccda-2252-4c1a-b789-525be0a8f177']
            400:
                description: |
                    Wrong arguments:
                    - OA0060: Invalid argument
                    - OA0063: Argument should be true or false
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
                    - OA0024: User not found
        security:
        - secret: []
        """
        self.check_cluster_secret()
        data = self.get_request_data()
        try:
            res = await self.controller.bulk_action_resources(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.write(json.dumps(res, cls=ModelEncoder))
