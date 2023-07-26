import json
from optscale_exceptions.common_exc import (NotFoundException,
                                            UnauthorizedException)
from optscale_exceptions.http_exc import OptHTTPError
from rest_api_server.exceptions import Err
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.organizations import (
    OrganizationAsyncCollectionHandler as OrganizationAsyncCollectionHandler_v1)
from rest_api_server.controllers.organization import OrganizationAsyncController
from rest_api_server.handlers.v1.organizations import (
    OrganizationAsyncItemHandler as OrganizationAsyncItemHandler_v1)
from rest_api_server.controllers.register import RegisterAsyncController
from rest_api_server.utils import ModelEncoder, run_task


class OrganizationAsyncCollectionHandler(OrganizationAsyncCollectionHandler_v1, BaseHandler):
    def _get_controller_class(self):
        return OrganizationAsyncController

    async def post(self, **url_params):
        """
        ---
        description: |
            Create new organization
            Required permission: TOKEN
        summary: Create organization
        tags: [organizations]
        parameters:
        -   in: body
            name: body
            description: Organization to add
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: Organization name
                        required: True
                        example: test name
                    currency:
                        type: string
                        example: USD
                        description: Organization currency
                        required: False
                        default: USD
        responses:
            201:
                description: Success (returns created object)
                schema:
                    type: object
                    example:
                        id: 64a7424c-0745-4926-bb6d-2125b16c91f9
                        pool_id: f9c65ff7-fa7a-4d91-b2ca-60dcac5422da
                        name: test name
                        created_at: 1585680056
                        deleted_at: 0
                        is_demo: False
                        currency: USD
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0211: Immutable parameters
                    - OE0216: Argument not provided
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
            401: {description: "Unauthorized: \n\n
                - OE0235: Unauthorized\n\n
                - OE0237: This resource requires authorization"}
            403: {description: "Forbidden: \n\n
                - OE0234: Forbidden"}
        security:
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        user_id = await self.check_self_auth()
        register_ctrl = RegisterAsyncController(
            self.session(), self._config, self.token
        )
        data.update({'user_id': user_id, 'token': self.token})
        res = await run_task(register_ctrl.register_new_organization, **data)
        self.set_status(201)
        self.write(res.to_json())

    async def _get_item(self, item_id, **kwargs):
        res = await run_task(self.controller.get, item_id, **kwargs)
        type_name = self.controller.model_type.__name__
        if res is None:
            raise OptHTTPError(404, Err.OE0002, [type_name, item_id])
        return res

    async def get(self):
        """
        ---
        description: |
            Gets a list of organizations.
            When called using token, returned only organizations in which user has
            assignments.
            With cluster secret returns complete list of organizations.
            Required permission: CLUSTER_SECRET or TOKEN
        tags: [organizations]
        summary: List of organizations
        parameters:
        -   name: is_demo
            in: query
            description: |
                List only demo organizations or not
                (applicable only with CLUSTER_SECRET)
            required: false
            type: boolean
        -   name: with_shareable_bookings
            in: query
            description: |
                List of organizations with existing shareable bookings
            required: false
            type: boolean
        -   name: with_connected_accounts
            in: query
            description: |
                List of organizations with connected cloud accounts
            required: false
            type: boolean
        responses:
            200:
                description: Organization list
                schema:
                    type: object
                    properties:
                        organizations:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description: "Unique organization id"}
                                    name: {type: string,
                                        description: "Organization display name"}
                                    deleted_at: {type: string,
                                        description: "Deleted timestamp
                                        (service field)"}
                                    created_at: {type: integer,
                                        description: "Creation timestamp
                                        (service field)"}
                                    pool_id: {type: string,
                                        description: "Organization pool id"}
                                    is_demo: {type: boolean,
                                        description: "Is demo organization or not"}
                                    currency: {type: string,
                                        description: "Organization currency"}
            400: {description: "Unauthorized: \n\n
                - OE0212: Unexpected parameters\n\n
                - OE0536: Invalid currency"}
            401: {description: "Unauthorized: \n\n
                - OE0235: Unauthorized\n\n
                - OE0237: This resource requires authorization"}
            403: {description: "Forbidden: \n\n
                - OE0236: Bad secret"}
            404: {description: "Not found: \n\n
                - OE0002: Organization not found"}
        security:
        - token: []
        - secret: []
        """
        is_by_user = False
        if not self.check_cluster_secret(raises=False):
            is_by_user = True

        args = self.get_org_arguments(is_by_user)
        if is_by_user:
            try:
                res = await run_task(self.controller.root_organizations_list,
                                     self.token)
            except UnauthorizedException as ex:
                raise OptHTTPError.from_opt_exception(401, ex)
        else:
            res = await run_task(self.controller.get_org_list, **args)

        organizations_dict = {'organizations': [
            organization.to_dict() for organization in res]}
        self.write(json.dumps(organizations_dict, cls=ModelEncoder))

    def get_org_arguments(self, is_by_user):
        args = {}
        if not is_by_user:
            args.update({k: self.get_arg(k, bool, False) for k in [
                'is_demo', 'with_shareable_bookings', 'with_connected_accounts'
            ]})
        unexpected_args = list(filter(
            lambda x: x not in args.keys(), self.request.arguments.keys()))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])
        return args


class OrganizationAsyncItemHandler(OrganizationAsyncItemHandler_v1, BaseHandler):
    def _get_controller_class(self):
        return OrganizationAsyncController

    async def get(self, id, **kwargs):
        """
        ---
        description: >
            Gets organization info by ID\n\n
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [organizations]
        summary: Get organization
        parameters:
        -   name: id
            in: path
            description: Organization ID
            required: true
            type: string
        responses:
            200:
                description: Organization data
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique organization id"}
                        name: {type: string,
                            description: "Organization display name"}
                        deleted_at: {type: string,
                            description: "Deleted timestamp (service field)"}
                        pool_id: {type: string,
                            description: "organization pool id"}
                        is_demo: {type: boolean,
                            description: "Is demo organization or not"}
                        currency: {type: string,
                            description: "Organization currency"}
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
            401: {description: "Unauthorized: \n\n
                - OE0235: Unauthorized\n\n
                - OE0237: This resource requires authorization"}
            403: {description: "Forbidden: \n\n
                - OE0234: Forbidden\n\n
                - OE0236: Bad secret"}
            404: {description: "Not found: \n\n
                - OE0002: Organization not found"}
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('INFO_ORGANIZATION', 'organization', id)
        try:
            item = await self._get_item(id, **kwargs)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        organization = item.to_dict()
        self.write(json.dumps(organization, cls=ModelEncoder))

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing organization
            Required permission: EDIT_PARTNER or CLUSTER_SECRET
        tags: [organizations]
        summary: Edit organization
        parameters:
        -   name: id
            in: path
            description: Organization ID
            required: true
            type: string
        -   in: body
            name: body
            description: Organization to modify
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        example: new name
                        description: new organization display name
                        required: False
                    currency:
                        type: string
                        example: USD
                        description: new organization currency
                        required: False
        responses:
            200:
                description: Modified organization
                schema:
                    type: object
                    example:
                        id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                        pool_id: 3d5a56e1-6e48-4d65-945a-a46f3a48e6e3
                        created_at: 1585680056
                        deleted_at: 0
                        name: test company
                        is_demo: False
                        currency: USD
            400: {description: "Wrong arguments: \n\n
                - OE0212: Unexpected parameters \n\n
                - OE0211: Immutable parameters \n\n
                - OE0223: Argument should be integer \n\n
                - OE0224: Wrong int argument value \n\n
                - OE0214: Argument should be a string \n\n
                - OE0215: Wrong argument's length \n\n
                - OE0536: Invalid currency"}
            404: {description: "Not found: \n\n
                - OE0002: Organization not found"}
            403:
                description: |
                    Forbidden:
                    - OE0379: Target owner doesn't have enough permissions for target pool
                    - OE0234: Forbidden
            401: {description: "Unauthorized: \n\n
                - OE0235: Unauthorized\n\n
                - OE0237: This resource requires authorization"}
            424:
                description: |
                    Failed dependency:
                    - OE0500: currency cannot be changed while organization has
                     connected cloud accounts
        security:
        - token: []
        - secret: []
        """
        await super().patch(id, **kwargs)

    async def delete(self, id, **kwargs):
        """
        ---
        description: >
            Deletes a organization with specified id\n\n
            Required permission: DELETE_PARTNER or CLUSTER_SECRET
        tags: [organizations]
        summary: Delete organization
        parameters:
        -   name: id
            in: path
            description: Organization ID
            required: true
            type: string
        responses:
            204: {description: Success}
            401: {description: "Unauthorized: \n\n
                - OE0235: Unauthorized\n\n
                - OE0237: This resource requires authorization"}
            403: {description: "Forbidden: \n\n
                - OE0234: Forbidden"}
            404: {description: "Not found: \n\n
                - OE0002: Organization not found"}
        security:
        - token: []
        - secret: []
        """
        await super().delete(id, **kwargs)
