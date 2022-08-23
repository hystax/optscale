import json

from cloud_adapter.model import ResourceTypes
from rest_api_server.controllers.discovery_info import (
    DiscoveryInfoAsyncController)
from rest_api_server.exceptions import Err
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v1.base_async import (
    BaseAsyncItemHandler, BaseAsyncCollectionHandler)
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.utils import (run_task, ModelEncoder, check_int_attribute,
                                   check_string_attribute)

from optscale_exceptions.common_exc import WrongArgumentsException
from optscale_exceptions.http_exc import OptHTTPError


class DiscoveryInfosAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                           BaseAuthHandler,
                                           BaseHandler):
    def _get_controller_class(self):
        return DiscoveryInfoAsyncController

    async def get(self, cloud_account_id):
        """
        ---
        description: |
            Get list of discovery information
            Required permission: CLUSTER_SECRET
        tags: [discovery_info]
        summary: List of cloud account discovery information
        parameters:
        -   name: cloud_account_id
            in: path
            description: Cloud account id
            required: true
            type: string
        -   name: resource_type
            in: query
            description: Discovery resource type
            required: false
            type: string
        responses:
            200:
                description: Discovery information list
                schema:
                    type: object
                    properties:
                        discovery_info:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string, description:
                                        "Unique discovery info id"}
                                    deleted_at: {type: integer, description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer, description:
                                        "Created timestamp (service field)"}
                                    cloud_account_id: {type: string, description:
                                        "Cloud account id id"}
                                    last_discovery_at: {type: integer, description:
                                        "Last completed discovery start timestamp"}
                                    resource_type: {type: string, description:
                                        "discovery resource type"}
                                    last_error_at: {type: integer, description:
                                        "UTC timestamp of last error"}
                                    last_error: {type: string, description:
                                        "Error message of last error, null if no error"}
                                    enabled: {type: boolean, description:
                                        "discovery enabled flag"}
            400:
                description: |
                    Wrong arguments:
                    - OE0384: Invalid resource type
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
                    - OE0002: Organization/CloudAccount not found
        security:
        - secret: []
        """
        self.check_cluster_secret()
        resource_type = self.get_arg('resource_type', str)
        res = await run_task(self.controller.list, cloud_account_id,
                             resource_type=resource_type)
        discovery_info = {
            'discovery_info': [info.to_dict() for info in res]}
        self.write(json.dumps(discovery_info, cls=ModelEncoder))

    def post(self, **kwargs):
        self.raise405()


class DiscoveryInfosAsyncItemHandler(BaseAsyncItemHandler,
                                     BaseAuthHandler):
    def _get_controller_class(self):
        return DiscoveryInfoAsyncController

    def _validate_params(self, item, **kwargs):
        string_param = ['last_error']
        int_params = ['last_discovery_at', 'last_error_at', 'observe_time']
        all_params = int_params + string_param
        unexpected = list(filter(lambda x: x not in all_params, kwargs.keys()))
        if unexpected:
            message = ', '.join(unexpected)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            for param in all_params:
                val = kwargs.get(param)
                if val is not None:
                    if param in string_param:
                        check_string_attribute(param, val)
                    else:
                        check_int_attribute(param, val)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        super()._validate_params(item, **kwargs)

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing discovery information
            Required permission: CLUSTER_SECRET
        tags: [discovery_info]
        summary: Edit discovery information
        parameters:
        -   name: id
            in: path
            description: Discovery information ID
            required: true
            type: string
        -   in: body
            name: body
            description: Discovery information to modify
            required: true
            schema:
                type: object
                properties:
                    last_discovery_at:
                        type: integer
                        description: Last completed discovery start timestamp
                        required: False
        responses:
            200:
                description: Discovery info object
                schema:
                    type: object
                    properties:
                        id: {type: string, description:
                            "Unique discovery information id"}
                        deleted_at: {type: integer, description:
                            "Deleted timestamp (service field)"}
                        created_at: {type: integer, description:
                            "Created timestamp (service field)"}
                        cloud_account_id: {type: string, description:
                            "Cloud account id"}
                        last_discovery_at: {type: integer, description:
                            "Last completed discovery start timestamp"}
                        resource_type: {type: string, description:
                                        "discovery resource type"}
                        last_error_at: {type: integer, description:
                                        "UTC timestamp of last error"}
                        last_error: {type: string, description:
                                        "Error message of last error, null if no error"}
                        enabled: {type: boolean, description:
                            "discovery enabled flag"}
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0223: Parameter should be integer
                    - OE0224: Value should be between 0 and 2147483647
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
        self.check_cluster_secret(raises=True)
        data = self._request_body()
        item = await self._get_item(id)
        self._validate_params(item, **data)
        res = await run_task(self.controller.edit, id, **data)
        self.write(res.to_json())

    def get(self, id, **kwargs):
        self.raise405()

    def delete(self, id, **kwargs):
        self.raise405()


class DiscoveryInfosAsyncSwitchEnableHandler(BaseAsyncItemHandler,
                                             BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return DiscoveryInfoAsyncController

    async def patch(self, cloud_account_id, **kwargs):
        """
        ---
        description: |
            Switch enable or disable discovery for resource type
            Required permission: MANAGE_CLOUD_CREDENTIALS
        tags: [discovery_info]
        summary: Edit discovery information
        parameters:
        -   name: cloud_account_id
            in: path
            description: Cloud account id
            required: true
            type: string
        -   in: body
            name: body
            description: Discovery information to set resource enable
            required: true
            schema:
                type: object
                properties:
                    resource_type:
                        type: string
                        description: Discovery resource type
                        required: True
                    enabled:
                        type: boolean
                        description: Discovery enabled flag
                        required: True
        responses:
            200:
                description: Discovery info object
                schema:
                    type: object
                    properties:
                        id: {type: string, description:
                            "Unique discovery information id"}
                        deleted_at: {type: integer, description:
                            "Deleted timestamp (service field)"}
                        created_at: {type: integer, description:
                            "Created timestamp (service field)"}
                        cloud_account_id: {type: string, description:
                            "Cloud account id"}
                        last_discovery_at: {type: integer, description:
                            "Last completed discovery start timestamp"}
                        resource_type: {type: string, description:
                                        "discovery resource type"}
                        last_error_at: {type: integer, description:
                                        "UTC timestamp of last error"}
                        last_error: {type: string, description:
                                        "Error message of last error, null if no error"}
                        enabled: {type: boolean, description:
                            "discovery enabled flag"}
            400:
                description: |
                    Wrong arguments:
                    - OE0177: Non unique parameters in get request
                    - OE0212: Unexpected parameters
                    - OE0216: Argument not provided
                    - OE0226: Argument should be True or False
                    - OE0384: Invalid resource type
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
        - token: []
        """
        await self.check_permissions('MANAGE_CLOUD_CREDENTIALS',
                                     'cloud_account', cloud_account_id)
        data = self._request_body()
        resource_type = data.pop('resource_type', None)
        enabled = data.pop('enabled', None)
        if resource_type is None:
            raise OptHTTPError(400, Err.OE0216, ['resource_type'])
        if enabled is None:
            raise OptHTTPError(400, Err.OE0216, ['enabled'])
        if resource_type not in ResourceTypes.__members__:
            raise OptHTTPError(400, Err.OE0384, [resource_type])
        if not isinstance(enabled, bool):
            raise OptHTTPError(400, Err.OE0226, ['enabled'])
        if data:
            raise OptHTTPError(400, Err.OE0212, [', '.join(data)])
        res = await run_task(self.controller.switch_enable, cloud_account_id,
                             resource_type, enabled)
        self.write(res.to_json())
