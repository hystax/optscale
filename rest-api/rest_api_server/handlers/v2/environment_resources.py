import json

from rest_api_server.controllers.environment_resource import EnvironmentResourceAsyncController
from rest_api_server.handlers.v1.base_async import (BaseAsyncCollectionHandler,
                                                    BaseAsyncItemHandler)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.utils import run_task, ModelEncoder
from optscale_exceptions.http_exc import OptHTTPError
from optscale_exceptions.common_exc import NotFoundException


class EnvironmentResourceAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                                BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return EnvironmentResourceAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of organization environment resources
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [environment_resources]
        summary: List of environment resources
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Environment resources list
                schema:
                    type: object
                    properties:
                        resources:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string, description:
                                        "Unique environment resource id"}
                                    name: {type: string,
                                        description: "Resource name"}
                                    deleted_at: {type: integer,
                                        description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer,
                                        description:
                                        "Created timestamp (service field)"}
                                    cloud_account_id: {type: string,
                                        description: "Cloud account id"}
                                    cloud_resource_id: {type: string,
                                        description: "Resource id in cloud"}
                                    resource_type: {type: string,
                                        description: "Type of resource"}
                                    pool_id: {type: string,
                                        description: "Resource pool id"}
                                    employee_id: {type: string,
                                        description: "Resource owner id"}
                                    tags: {type: object,
                                        description:
                                        "Resource tags in name: value format"}
                                    region: {type: string,
                                        description: "Resource region"}
                                    cloud_console_link: {type: string,
                                        description: "Cloud console link, show link if resource is active, else None"}
                                    active: {type: boolean,
                                        description: "Resource active flag"}
                                    first_seen: {type: integer,
                                        description: "Resource first seen"}
                                    last_seen: {type: integer,
                                        description: "Resource last seen"}
                                    cluster_type_id: {type: string,
                                        description: "Cluster type id (cluster resources only)"}
                                    ssh_only: {type: boolean,
                                        description: "Booking this resource requires an ssh_key"}
                                    applied_rules:
                                        type: array
                                        items:
                                            type: object
                                            properties:
                                                id: {type: string,
                                                    description: "Assignment rule id"}
                                                name: {type: string,
                                                    description: "Assignment rule name"}
                                                pool_id: {type: string,
                                                    description: "Target pool for assignment rule"}
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
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
        resources = await run_task(self.controller.list_org_environments,
                                   organization_id=organization_id)
        self.write(json.dumps({'resources': resources}, cls=ModelEncoder))

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create environment resource for specified organization
            Required permission: MANAGE_RESOURCES or CLUSTER_SECRET
        tags: [environment_resources]
        summary: Create environment resource for specified organization
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Environment resource to add
            required: true
            schema:
                type: object
                properties:
                    name: {type: string,
                        description: "Resource name"}
                    resource_type: {type: string,
                        description: "Resource type"}
                    pool_id: {type: string,
                        description: "Resource pool id"}
                    employee_id: {type: string,
                        description: "Resource owner id"}
                    tags: {type: object,
                        description: "Resource tags in name: value format"}
                    active: {type: boolean,
                            description: "Resource active flag"}
                    ssh_only: {type: boolean,
                            description: "Booking this resource requires an ssh_key"}
        responses:
            201: {description: Success (returns created object)}
            400:
                description: |
                    Wrong arguments:
                    - OE0003: Database error
                    - OE0216: Argument is not provided
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters
                    - OE0219: Argument should be a string with valid JSON
                    - OE0456: Duplicate path parameters in the request body
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
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
                'MANAGE_RESOURCES', 'organization', organization_id)
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        res = await run_task(self.controller.create,
                             organization_id=organization_id, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))


class EnvironmentResourceAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                                          BaseHandler):
    def _get_controller_class(self):
        return EnvironmentResourceAsyncController

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get shareable resource info by id
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [environment_resources]
        summary: Get shareable resource
        parameters:
        -   name: id
            in: path
            description: Resource id
            required: true
            type: string
        -   name: details
            in: query
            description: Display additional resource info
            required: false
            type: boolean
        responses:
            200:
                description: Environment resource data
                schema:
                    type: object
                    properties:
                        active: {type: boolean,
                            description: "Resource active flag"}
                        cloud_account_id: {type: string,
                            description: "Cloud account id"}
                        cloud_console_link: {type: string,
                            description: "Cloud console link, show link if resource is active, else None"}
                        cloud_resource_id: {type: string,
                            description: "Resource id in cloud"}
                        created_at: {type: integer,
                            description: "Created timestamp (service field)"}
                        deleted_at: {type: integer,
                            description: "Deleted timestamp (service field)"}
                        employee_id: {type: string,
                            description: "Resource owner id"}
                        first_seen: {type: integer,
                            description: "Resource first seen"}
                        id: {type: string,
                            description: "Unique resource id"}
                        last_seen: {type: integer,
                            description: "Resource last seen"}
                        name: {type: string,
                            description: "Resource name"}
                        pool_id: {type: string,
                            description: "Resource pool id"}
                        region: {type: string,
                            description: "Resource region"}
                        resource_type: {type: string,
                            description: "Resource type"}
                        tags: {type: object,
                            description: "Resource tags in name: value format"}
                        cluster_type_id: {type: string,
                            description: "Cluster type id (cluster resources only)"}
                        ssh_only: {type: boolean,
                            description: "Booking this resource requires an ssh_key"}
                        applied_rules:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description: "Assignment rule id"}
                                    name: {type: string,
                                        description: "Assignment rule name"}
                                    pool_id: {type: string,
                                        description: "Target pool for assignment rule"}
                        details:
                            type: object
                            properties:
                                active: {type: boolean,
                                    description: "Resource active flag"}
                                cloud_name: {type: string,
                                    description:"Resource cloud name"}
                                cloud_type: {type: string,
                                    description:"Resource cloud type"}
                                constraints: {type: object,
                                    description: "Resource constraints"}
                                cost: {type: string,
                                    description: "This month cost"}
                                first_seen: {type: integer,
                                    description: "Resource first seen"}
                                forecast: {type: string,
                                    description: "This month forecast"}
                                last_seen: {type: integer,
                                    description: "Resource last seen"}
                                owner_name: {type: string,
                                    description: "Resource owner name"}
                                policies: {type: object,
                                    description: "Pool policies"}
                                pool_name: {type: string,
                                    description: "Resource pool name"}
                                pool_purpose: {type: string,
                                    description: "Resource pool purpose"}
                                region: {type: string,
                                    description: "Resource region"}
                                service_name: {type: string,
                                    description: "Resource service_name"}
                                total_cost: {type: integer,
                                    description: "Resource lifetime cost"}
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
                    - OE0002: Resource not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'cloud_resource', id)
        details = self.get_arg('details', bool, False)
        try:
            item = await run_task(self.controller.get, id, **kwargs)
            self._validate_params(item, **kwargs)
            if details:
                res = await run_task(
                    self.controller.get_resource_details, item, **kwargs)
                item.update({'details': res})
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.write(json.dumps(item, cls=ModelEncoder))

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing environment resource
            Required permission: MANAGE_RESOURCES or CLUSTER_SECRET
        tags: [environment_resources]
        summary: Edit environment resource
        parameters:
        -   name: id
            in: path
            description: Resource ID
            required: true
            type: string
        -   in: body
            name: body
            description: Environment resource changes
            required: false
            schema:
                type: object
                properties:
                    pool_id: {type: string,
                        description: "Resource owner id"}
                    employee_id: {type: string,
                        description: "Resource owner id"}
                    tags: {type: object,
                        description: "Resource tags in name: value format"}
                    active: {type: boolean,
                        description: "Resource active flag"}
                    ssh_only: {type: boolean,
                        description: "Booking this resource requires an ssh_key"}
        responses:
            200: {description: Success (returns modified object)}
            400:
                description: |
                    Wrong arguments:
                    - OE0002: Pool/Employee not found
                    - OE0003: Database error
                    - OE0216: Argument is not provided
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters
                    - OE0219: Argument should be a string with valid JSON
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Resource not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'MANAGE_RESOURCES', 'cloud_resource', id)
        data = self._request_body()
        res = await run_task(self.controller.edit, id, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, id, **kwargs):
        """
        ---
        description: |
            Deletes environment resource with specified id
            Required permission: MANAGE_RESOURCES or CLUSTER_SECRET
        tags: [environment_resources]
        summary: Delete environment resource
        parameters:
        -   name: id
            in: path
            description: Resource ID
            required: true
            type: string
        responses:
            204:
                description: |
                    Success
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Resource not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'MANAGE_RESOURCES', 'cloud_resource', id)
        await run_task(self.controller.delete, id, **kwargs)
        self.set_status(204)
