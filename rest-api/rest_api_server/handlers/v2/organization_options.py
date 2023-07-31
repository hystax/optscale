import json

from rest_api_server.exceptions import Err
from optscale_exceptions.http_exc import OptHTTPError
from rest_api_server.controllers.organization_options import OrganizationOptionsAsyncController
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import (run_task, ModelEncoder)


class OrganizationOptionsAsyncCollectionHandler(BaseAsyncItemHandler, BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return OrganizationOptionsAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
            Returns a list of options specified for organization.
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [organization_options]
        summary: List of options specified for organization
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
            required: true
            type: string
        -   name: with_values
            in: query
            description: Options with values
            required: false
            type: boolean
        responses:
            200:
                description: Organization options list
                schema:
                    type: object
                    properties:
                        options:
                            type: array
                            items:
                                type: string
                                description: option name
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        with_values = self.get_arg('with_values', bool, False)
        res = await run_task(self.controller.list, organization_id, with_values)
        option_dict = {'options': res}
        self.write(json.dumps(option_dict, cls=ModelEncoder))


class OrganizationOptionsAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return OrganizationOptionsAsyncController

    async def get(self, organization_id, option_name):
        """
        ---
        description: |
            Returns the option value for the specified organization.
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [organization_options]
        summary: Option value for the specified organization
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
            required: true
            type: string
        -   name: option_name
            in: path
            description: option name
            required: true
            type: string
        responses:
            200:
                description: Option value
                schema:
                    type: object
                    properties:
                        value:
                            type: string
                            description: Option value
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        res = await run_task(self.controller.get_by_name, organization_id, option_name)
        value_dict = {'value': res}
        self.write(json.dumps(value_dict, cls=ModelEncoder))

    async def patch(self, organization_id, option_name):
        """
        ---
        description: |
            Modifies or creates an option for an organization
            Required permission: EDIT_PARTNER or CLUSTER_SECRET
        tags: [organization_options]
        summary: Modify/create option
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
            required: true
            type: string
        -   name: option_name
            in: path
            description: Option name
            required: true
            type: string
        -   name: body
            in: body
            description: Option value
            required: true
            schema:
                type: object
                properties:
                    value:
                        type: string
                        description: Option value

        responses:
            200:
                description: Success (returns created/modified value)
                schema:
                type: object
                properties:
                    value:
                        type: string
                        description: Option value
            400:
                description: |
                    Wrong arguments:
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters
                    - OE0216: Argument is not provided
                    - OE0219: Argument should be a string with valid JSON
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        - secret: []
        """
        is_secret = True
        if not self.check_cluster_secret(raises=False):
            is_secret = False
            await self.check_permissions(
                'EDIT_PARTNER', 'organization', organization_id)
        data = self._request_body().get('value')
        if not data:
            raise OptHTTPError(400, Err.OE0216, ['value'])
        res = await run_task(self.controller.patch,
                             organization_id, option_name, data, is_secret=is_secret)
        value_dict = {'value': res}
        self.write(json.dumps(value_dict, cls=ModelEncoder))

    async def delete(self, organization_id, option_name):
        """
        ---
        description: |
            Deletes the specified option for the organization
            Required permission: EDIT_PARTNER or CLUSTER_SECRET
        tags: [organization_options]
        summary: Delete option
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
            required: true
            type: string
        -   name: option_name
            in: path
            description: Option name
            required: true
            type: string
        responses:
            204:
                description: Success
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Option not found
                    - OE0002: Organization not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'EDIT_PARTNER', 'organization', organization_id)
        await run_task(self.controller.delete, organization_id, option_name)
        self.set_status(204)
