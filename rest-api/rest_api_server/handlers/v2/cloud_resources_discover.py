import json

from optscale_exceptions.http_exc import OptHTTPError
from rest_api_server.controllers.cloud_resource_discover import (
    CloudResourceDiscoverAsyncController)
from rest_api_server.exceptions import Err
from rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.utils import run_task, ModelEncoder


class CloudResourceDiscoverAsyncCollectionHandler(
        BaseAsyncCollectionHandler, BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return CloudResourceDiscoverAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
            Discovers cloud resources
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [cloud_resources]
        summary: List of cloud resources from Cloud. Output depends on type
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
            required: true
            type: string
        -   name: type
            in: query
            enum:
                - instance
                - snapshot
                - volume
                - bucket
                - k8s_pod
                - snapshot_chain
                - rds_instance
                - ip_address
                - cluster type id (uuid)
            description: type of the resources gathered
            required: true
            type: string
        -   name: cloud_type
            in: query
            description: |
                discover resources only for clouds with specified cloud type
            enum:
                - aws_cnr
                - azure_cnr
                - kubernetes_cnr
                - alibaba_cnr
            required: false
            type: string
        -   name: cached
            in: query
            description: return cached resources. Only True is supported
            required: false
            default: true
            type: boolean
        -   name: filters
            in: query
            description: |
                Filters conditions (dict {filter1: [value1, value2], filter2: [value3]})
                Supported filters:
                    - region
                    - pool_id
                    - owner_id
                    - cloud_account_id
            content:
                application/json:
                    type: string
            required: false
            type: string
        -   name: sort
            in: query
            type: string
            required: false
            description: |
                Sort condition (1-element dict {field: order}).
                Supported field values:
                    - id
                    - name
                    - cloud_account_id
                    - cloud_account_name
                    - region
                    - pool_id
                    - pool_name
                    - owner_id
                    - owner_name
                    - flavor (instances type only)
                    - volume_type (volume type only)
                    - size (volume or snapshot types only)
                    - description (snapshot type only)
                    - state (snapshot type only)
                    - tags
                Order values (asc | desc)
            content:
                application/json:
                    type: string
        responses:
            200:
                description: Cloud resources list
                schema:
                    type: object
                    properties:
                        data:
                            type: array
                            items:
                                type: object
                                properties:
                                    resource_id:
                                        type: string
                                        description: Resource id
                                    name:
                                        type: string
                                        description: Cloud resource name
                                    cloud_account_id:
                                        type: string
                                        description: Cloud account id
                                    cloud_account_name:
                                        type: string
                                        description: Cloud account name
                                    region:
                                        type: string
                                        description: Cloud region
                                    pool_id:
                                        type: string
                                        description: Pool id
                                    pool_name:
                                        type: string
                                        description: Pool name
                                    pool_purpose:
                                        type: string
                                        description: Pool purpose
                                    owner_id:
                                        type: string
                                        description: Owner id
                                    owner_name:
                                        type: string
                                        description: Owner name
                                    organization_id:
                                        type: string
                                        description: Organization id
                                    meta:
                                        type: object
                                        properties:
                                            flavor:
                                                type: string
                                                description: Flavor (instances type)
                                            volume_type:
                                                type: string
                                                description: Volume type (volume type)
                                            size:
                                                type: integer
                                                description: >
                                                    Volume size (volume or snapshot types)
                                            description:
                                                type: string
                                                description: Description (snapshot type)
                                            state:
                                                type: string
                                                description: >
                                                    State of the resource (snapshot type)
                                            cloud_console_link:
                                                type: string,
                                                description: Cloud console link
                                    tags:
                                        type: object
                                        description: >
                                            Cloud resource tags in name: value format
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0384: Invalid resource type
                    - OE0388: Invalid region for resources discovery
                    - OE0389: Invalid sort condition for resource type
                    - OE0390: Invalid filter name
                    - OE0392: Filters should be a dict
                    - OE0393: Value for filter should be a list
                    - OE0394: Sort condition must be a dict
                    - OE0395: Sort condition should be one
                    - OE0397: Resource type is required
                    - OE0398: Condition should be a json string
                    - OE0399: Sort order should be asc or desc
                    - OE0453: Invalid cached value
                    - OE0467: Invalid cluster type id
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
            await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                         organization_id)
        list_kwargs = dict()
        resource_type = self.get_arg('type', str, None)
        filters = self.get_arg('filters', str, "{}")
        sort = self.get_arg('sort', str, "{}")
        cached = self.get_arg('cached', bool, True)
        cloud_type = self.get_arg('cloud_type', str, None)
        if not cached:
            raise OptHTTPError(400, Err.OE0453, [cached])
        if resource_type:
            list_kwargs['type'] = resource_type
            list_kwargs['filters'] = filters
            list_kwargs['sort'] = sort
            list_kwargs['cloud_type'] = cloud_type
        res = await run_task(self.controller.list, organization_id,
                             **list_kwargs)
        self.write(json.dumps(res, cls=ModelEncoder))
