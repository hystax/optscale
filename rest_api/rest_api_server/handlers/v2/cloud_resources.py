import json

from rest_api.rest_api_server.controllers.cloud_resource import CloudResourceAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import NotFoundException


class CloudResourceAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                          BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return CloudResourceAsyncController

    async def get(self, cloud_account_id):
        """
        ---
        description: |
            Get list of cloud resources for cloud account
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [cloud_resources]
        summary: List of cloud resources
        parameters:
        -   name: cloud_account_id
            in: path
            description: cloud account id
            required: true
            type: string
        -   name: cloud_resource_id
            in: query
            description: Cloud resource id
            required: false
            type: string
        -   name: assignment_history
            in: query
            description: Include resource assignment history into response
            required: false
            type: boolean
        responses:
            200:
                description: Cloud resources list
                schema:
                    type: object
                    properties:
                        resources:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description:
                                        "Unique cloud resource id"}
                                    name: {type: string,
                                        description: "Cloud resource name"}
                                    deleted_at: {type: integer,
                                        description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer,
                                        description:
                                        "Created timestamp (service field)"}
                                    cloud_account_id: {type: string,
                                        description: "cloud account id"}
                                    cloud_resource_id: {type: string,
                                        description: "Resource id in cloud"}
                                    resource_type: {type: string,
                                        description: "Type of cloud resource"}
                                    pool_id: {type: string,
                                        description: "Pool for resource"}
                                    employee_id: {type: string,
                                        description: "Cloud resource owner id"}
                                    tags: {type: object,
                                        description:
                                        "Cloud resource tags in name: value format"}
                                    region: {type: string,
                                        description: "Cloud resource region"}
                                    cloud_console_link: {type: string,
                                        description: "Cloud console link, show link if resource is active, else None"}
                                    assignment_history:
                                        type: array
                                        description: >
                                            present when assignment_history set
                                            to True
                                        items:
                                            type: object
                                            properties:
                                                id:
                                                    type: string
                                                    description: >
                                                        assignment history id
                                                resource_id:
                                                    type: string
                                                    description: resource id
                                                created_at:
                                                    type: integer
                                                    description: >
                                                        time of assignment
                                                pool_id:
                                                    type: string
                                                    description: >
                                                        pool to which resource
                                                        is assigned
                                                owner_id:
                                                    type: string
                                                    description: >
                                                        employee to which
                                                        resource is assigned
                                                deleted_at:
                                                    type: integer
                                                    description: >
                                                        Deleted timestamp
                                                        (service field)
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
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
                    - OE0002: Cloud account not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'cloud_account', cloud_account_id)
        list_kwargs = dict(
            cloud_account_id=cloud_account_id, check_cloud_account=True)
        cloud_resource_id = self.get_arg('cloud_resource_id', str, None)
        if cloud_resource_id:
            list_kwargs['cloud_resource_id'] = cloud_resource_id
        resources = await run_task(self.controller.list, **list_kwargs)
        self.write(json.dumps({'resources': resources}, cls=ModelEncoder))

    async def post(self, cloud_account_id, **url_params):
        """
        ---
        description: |
            Create cloud resource for specified cloud account
            Required permission: CLUSTER_SECRET
        tags: [cloud_resources]
        summary: Create cloud resource for specified cloud account
        parameters:
        -   name: cloud_account_id
            in: path
            description: cloud account id
            required: true
            type: string
        -   in: body
            name: body
            description: Cloud resource to add
            required: true
            schema:
                type: object
                properties:
                    name: {type: string,
                        description: "Cloud resource name"}
                    cloud_resource_id: {type: string,
                        description: "Resource id in cloud"}
                    cloud_resource_hash: {type: string,
                        description: "Resource hash in cloud"}
                    resource_type: {type: string,
                        description: "Type of cloud resource"}
                    pool_id: {type: string,
                        description: "Pool for resource"}
                    employee_id: {type: string,
                        description: "Cloud resource owner id"}
                    tags: {type: object,
                        description: "Cloud resource tags in name: value format"}
                    region: {type: string,
                        description: "Cloud resource region"}
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
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Cloud account not found
        security:
        - secret: []
        """
        self.check_cluster_secret()
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        res = await run_task(self.controller.create,
                             cloud_account_id=cloud_account_id, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))


class CloudResourceAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                                    BaseHandler):
    def _get_controller_class(self):
        return CloudResourceAsyncController

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get cloud resource info by ID
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [cloud_resources]
        summary: Get cloud resource
        parameters:
        -   name: id
            in: path
            description: Cloud resource ID
            required: true
            type: string
        -   name: details
            in: query
            description: "display additional resource info"
            required: false
            type: boolean
        responses:
            200:
                description: Cloud resource data
                schema:
                    type: object
                    properties:
                        active: {type: boolean,
                            description: "Resource active flag"}
                        attached: {type: boolean,
                            description: "Volume attachment flag (only for volume)"}
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
                        description: {type: string,
                            description: "Resource description (only for snapshot)"}
                        employee_id: {type: string,
                            description: "Cloud resource owner id"}
                        first_seen: {type: integer,
                            description: "Resource first seen"}
                        flavor: {type:string,
                            description: "Instance flavor (only for instance)"}
                        id: {type: string,
                            description: "Unique cloud resource id"}
                        image_id: {type:string,
                            description: "ID of the instance image"}
                        last_attached: {type: integer,
                            description: "Timestamp of the last attachment (only for volume)"}
                        last_seen: {type: integer,
                            description: "Resource last seen"}
                        last_seen_not_stopped: {type: integer,
                            description: "Instance was last seen not stopped (only for instance)"}
                        name: {type: string,
                            description: "Cloud resource name"}
                        organization_id: {type: string,
                            description: "Organization for resource"}
                        pool_id: {type: string,
                            description: "Pool for resource"}
                        region: {type: string,
                            description: "Resource region"}
                        resource_type: {type: string,
                            description: "Type of cloud resource"}
                        size: {type: integer,
                            description: "Resource size (only for volume, snapshot)"}
                        state: {type: string,
                            description: "Snapshot state (only for snapshot)"}
                        snapshot_id: {type: string,
                            description: "ID of the snapshot to which the volume is attached (only for volume)"}
                        tags: {type: object,
                            description: "Cloud resource tags in name: value format"}
                        volume_id: {type: object,
                            description: "ID of the attached volume (optional)"}
                        volume_type: {type: string,
                            description: "Volume type (only for volume)"}
                        cluster_id: {type: string,
                            description: "Cluster id (dependent resources only)"}
                        cluster_type_id: {type: string,
                            description: "Cluster type id (cluster resources only)"}
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
                        sub_resources:
                            type: array
                            description: "Sub resources"
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description: "Unique cloud resource id"}
                                    name: {type: string,
                                        description: "Cloud resource name"}
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
                                        description: "Type of cloud resource"}
                                    pool_id: {type: string,
                                        description: "Pool for resource"}
                                    employee_id: {type: string,
                                        description: "Cloud resource owner id"}
                                    tags: {type: object,
                                        description: "Cloud resource tags in name: value format"}
                                    region: {type: string,
                                        description: "Cloud resource region"}
                                    cloud_console_link: {type: string,
                                        description: "Cloud console link, show link if resource is active, else None"}
                                    cluster_id: {type: string,
                                        description: "Cluster id"}
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
                                env_properties_collector_link: {type: string,
                                    description:
                                    "env_properties collector link, show link if resource is shareable, else None"}
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
                                total_traffic_expenses: {type: integer,
                                    description: "resource traffic cost"}
                                total_traffic_usage: {type: integer,
                                    description: "resource traffic usage"}
                        dismissed:
                            type: array
                            items:
                                type: string
                                description: "Names of dismissed recommendations"
                        dismissed_recommendations:
                            type: object
                            properties:
                                run_timestamp: {type: integer,
                                    description: "Recommendation update timestamp"}
                                modules:
                                    type: object
                                    properties:
                                        avg_saving: {type: number,
                                            description:
                                            "Total cost after reserved with upfront (only for reserved_instances)"}
                                        cloud_account_id: {type: string,
                                            description: "ID of the cloud account recommendation"}
                                        cloud_account_name: {type: string,
                                            description: "Name of the cloud account recommendation"}
                                        cloud_resource_id: {type: string,
                                            description: "ID of the recommendation resource in the cloud"}
                                        cloud_type: {type: string,
                                            description: "Resource cloud type"}
                                        cost_in_detached_state: {type: number,
                                            description:
                                            "Cost of volume after detaching (only for volumes_not_attached)"}
                                        cost_in_stopped_state: {type: number,
                                            description:
                                            "Cost of instance after stop (only for instances_in_stopped_state)"}
                                        current_region: {type: string,
                                            description: "Current resource region (only for instance_migration)"}
                                        first_seen: {type: integer,
                                            description: "Recommendation first seen (optional)"}
                                        flavor: {type: string,
                                            description: "Resource flavor (optional)"}
                                        is_dismissed: {type: string,
                                            description: "Recommendation is dismissed (optional)"}
                                        last_seen: {type: integer,
                                            description: "Recommendation last seen (optional)"}
                                        last_seen_in_active: {type: integer,
                                            description:
                                            "Last seen instance in active state (only for instances_in_stopped_state)"}
                                        last_seen_in_attached_state: {type: integer,
                                            description:
                                            "Last seen volume in attached state (only for volumes_not_attached)"}
                                        last_used: {type: integer,
                                            description: "Image last used (only for obsolete_images)"}
                                        name: {type: string,
                                            description: "Recommendation name"}
                                        recommended_region: {type: string,
                                            description: "Recommended resource region (only for instance_migration)"}
                                        region: {type: string,
                                            description: "Resource region (optional)"}
                                        resource_id: {type: string,
                                            description: "Recommendation resource id (except obsolete_images)"}
                                        resource_name: {type: string,
                                            description: "Recommendation resource name"}
                                        saving: {type: number,
                                            description:
                                            "Total cost after applying the recommendation (except obsolete_images)"}
                                        total_cost: {type: number,
                                            description: "Current total cost (only for short_living_instances)"}
                        meta:
                            type: object
                            properties:
                                attached: {type: boolean,
                                    description: "Volume attachment flag (only for volume)"}
                                last_attached: {type: string,
                                    description: "Timestamp of the last attachment (only for volume)"}
                                last_seen_not_stopped: {type: integer,
                                    description: "Instance was last seen not stopped (only for instance)"}
                                spotted: {type: boolean,
                                    description: "This is a spot instance"}
                                stopped_allocated: {type: boolean,
                                    description: "Stopped allocation for a spot instance flag (only for instance)"}
                        recommendations:
                            type: object
                            properties:
                                run_timestamp: {type: integer,
                                    description: "Recommendation update timestamp"}
                                modules:
                                    type: object
                                    properties:
                                        avg_saving: {type: number,
                                            description:
                                            "Total cost after reserved with upfront (only for reserved_instances)"}
                                        cloud_account_id: {type: string,
                                            description: "ID of the cloud account recommendation"}
                                        cloud_account_name: {type: string,
                                            description: "Name of the cloud account recommendation"}
                                        cloud_resource_id: {type: string,
                                            description: "ID of the recommendation resource in the cloud"}
                                        cloud_type: {type: string,
                                            description: "Resource cloud type"}
                                        cost_in_detached_state: {type: number,
                                            description:
                                            "Cost of volume after detaching (only for volumes_not_attached)"}
                                        cost_in_stopped_state: {type: number,
                                            description:
                                            "Cost of instance after stop (only for instances_in_stopped_state)"}
                                        current_region: {type: string,
                                            description: "Current resource region (only for instance_migration)"}
                                        first_seen: {type: integer,
                                            description: "Recommendation first seen (optional)"}
                                        flavor: {type: string,
                                            description: "Resource flavor (optional)"}
                                        is_dismissed: {type: string,
                                            description: "Recommendation is dismissed (optional)"}
                                        last_seen: {type: integer,
                                            description: "Recommendation last seen (optional)"}
                                        last_seen_in_active: {type: integer,
                                            description:
                                            "Last seen instance in active state (only for instances_in_stopped_state)"}
                                        last_seen_in_attached_state: {type: integer,
                                            description:
                                            "Last seen volume in attached state (only for volumes_not_attached)"}
                                        last_used: {type: integer,
                                            description: "Image last used (only for obsolete_images)"}
                                        name: {type: string,
                                            description: "Recommendation name"}
                                        recommended_region: {type: string,
                                            description: "Recommended resource region (only for instance_migration)"}
                                        region: {type: string,
                                            description: "Resource region (optional)"}
                                        resource_id: {type: string,
                                            description: "Recommendation resource id (except obsolete_images)"}
                                        resource_name: {type: string,
                                            description: "Recommendation resource name"}
                                        saving: {type: number,
                                            description:
                                            "Total cost after applying the recommendation (except obsolete_images)"}
                                        total_cost: {type: number,
                                            description: "Current total cost (only for short_living_instances)"}
                        security_groups:
                            type: array
                            items:
                                type: object
                                properties:
                                    GroupId: {type: string,
                                        description: "Security group id"}
                                    GroupName: {type: string,
                                        description: "Security group name"}
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
                for sub_item in item.get('sub_resources', []):
                    res = await run_task(
                        self.controller.get_resource_details, sub_item, **kwargs)
                    sub_item.update({'details': res})
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.write(json.dumps(item, cls=ModelEncoder))

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing cloud resource
            Required permission: MANAGE_RESOURCES or CLUSTER_SECRET
        tags: [cloud_resources]
        summary: Edit cloud resource
        parameters:
        -   name: id
            in: path
            description: Cloud resource ID
            required: true
            type: string
        -   in: body
            name: body
            description: Cloud resource changes
            required: false
            schema:
                type: object
                properties:
                    name: {type: string,
                        description: "Cloud resource name"}
                    resource_type: {type: string,
                        description: "Type of cloud resource"}
                    pool_id: {type: string,
                        description: "Pool for resource"}
                    employee_id: {type: string,
                        description: "Cloud resource owner id"}
                    tags: {type: object,
                        description: "Cloud resource tags in name: value format"}
                    region: {type: string,
                        description: "Cloud resource region"}
                    shareable: {type: bool, enum: [false],
                        description: "Make resource not shareable"}
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
                    - OE0479: shareable should be False
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
            Deletes cloud resource with specified id
            Required permission: CLUSTER_SECRET
        tags: [cloud_resources]
        summary: Delete cloud resource
        parameters:
        -   name: id
            in: path
            description: Cloud resource ID
            required: true
            type: string
        responses:
            204:
                description: |
                    Success
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
        - secret: []
        """
        self.check_cluster_secret()
        await run_task(self.controller.delete, id, **kwargs)
        self.set_status(204)
