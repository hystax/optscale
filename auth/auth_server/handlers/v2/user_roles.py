from auth_server.handlers.v2.base import BaseHandler
import json
from auth_server.handlers.v1.base import BaseSecretHandler
from auth_server.controllers.user_role import UserRoleAsyncController
from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            NotFoundException)
from optscale_exceptions.http_exc import OptHTTPError
from auth_server.utils import ModelEncoder

# url_key: (<api parameter>, <type>, <repeated: bool>)
PAYLOAD_MAP_PARAMS = {
    'user_ids': ('user_ids', str, True),
    'role_purposes': ('role_purposes', str, True),
    'scope_ids': ('scope_ids', str, True)
}


class UserRolesAsyncHandler(BaseSecretHandler, BaseHandler):

    def _get_controller_class(self):
        return UserRoleAsyncController

    def get_request_data(self):
        return self.parse_url_params_into_payload(PAYLOAD_MAP_PARAMS)

    async def get(self):
        """
        ---
        tags: [user_roles]
        summary: Get user roles
        description: |
            Gets assigned user roles
            Required permission: CLUSTER SECRET
        parameters:
        -   name: user_ids
            in: query
            description: list of user ids
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: role_purposes
            in: query
            description: list of role purposes
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: scope_ids
            in: query
            description: list of scope ids
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        responses:
            200:
                description: Success
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            assignment_id: {type: string,
                                description: "Id of assignment"}
                            assignment_resource_id: {type: string,
                                description: "Id of resource"}
                            assignment_type_id: {type: integer,
                                description: "Type of the assignment"}
                            user_id: {type: string,
                                description: "User Id"}
                            role_name: {type: string,
                                description: "Name of Role"}
                            role_scope_id: {type: string,
                                description: "Role scope"}
                            role_id: {type: integer,
                                description: "Id of Role"}
                            user_email: {type: string,
                                description: "User email"}
                            user_display_name: {type: string,
                                description: "User display name"}
                            role_purpose: {type: string,
                                description: "User RolePurpose type"}
            400:
                description: |
                    Wrong arguments:
                    - OA0022: Unexpected parameters
                    - OA0046: Payload is not a valid json
                    - OA0047: Payload is malformed
                    - OA0055: Argument should be list
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
        self.check_cluster_secret()
        data = self.get_request_data()
        try:
            res = await self.controller.get(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.write(json.dumps(res, cls=ModelEncoder))
