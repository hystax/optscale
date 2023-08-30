import json

from rest_api.rest_api_server.controllers.optimization import OptimizationAsyncController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_int_attribute, check_string_attribute,
    object_to_xlsx)

from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException, FailedDependency)


class OptimizationAsyncCollectionHandler(BaseAsyncItemHandler,
                                         BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return OptimizationAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of optimizations
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [optimizations]
        summary: List of organization optimizations
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: type
            type: array
            in: query
            items:
                type: string
            collectionFormat: multi
            description: Types for which details must be returned
            required: false
        -   name: cloud_account_id
            type: array
            in: query
            items:
                type: string
            collectionFormat: multi
            description: Cloud accounts for which details must be returned
            required: false
        -   name: limit
            in: query
            description: |
                Limit amount of optimizations details returned. Details will
                be sorted by saving (desc) before limiting. Applicable
                together with type parameter. Must be >0
            required: false
            type: integer
        -   name: status
            in: query
            description: |
                Return active, dismissed or excluded recommendations details.
                Required together with type parameter
            required: false
            type: string
            default: active
            enum: [active, dismissed, excluded]
        -   name: overview
            in: query
            description: Return optimizations in overview format
            required: false
            type: boolean
            default: false
        responses:
            200:
                description: Optimizations
                schema:
                    type: object
                    properties:
                        id: {type: string, description:
                            "Unique checklist id"}
                        deleted_at: {type: integer, description:
                            "Deleted timestamp (service field)"}
                        created_at: {type: integer, description:
                            "Created timestamp (service field)"}
                        organization_id: {type: string, description:
                            "Organization id"}
                        last_run: {type: integer, description:
                            "Last run start timestamp"}
                        next_run: {type: integer, description:
                            "Next run start timestamp"}
                        last_completed: {type: integer, description:
                            "Last completed run timestamp"}
                        total_saving: {type: number, description:
                            "Saving value"}
                        optimizations:
                            type: object
                            properties:
                                short_living_instances:
                                    type: object
                                    properties:
                                        count: {type: integer, description:
                                            "Optimization objects count"}
                                        saving: {type: number, description:
                                            "Optimization saving"}
                                        limit: {type: integer, description:
                                            "Max objects amount (limit applied)"}
                                        items:
                                            type: array
                                            description: >
                                                Short living instances objects
                                                if short_living_instances type specified
                                            items:
                                                type: object
                                                properties:
                                                    cloud_resource_id: {type: string, description:
                                                        "Cloud instance id"}
                                                    resource_name: {type: string, description:
                                                        "Instance name"}
                                                    cloud_account_id: {type: string, description:
                                                        "Cloud account id"}
                                                    cloud_account_name: {type: string, description:
                                                        "Cloud account name"}
                                                    resource_id: {type: string, description:
                                                        "Instance id"}
                                                    cloud_type: {type: string, description:
                                                        "Cloud type"}
                                                    total_cost: {type: integer, description:
                                                        "Instance lifetime cost"}
                                                    first_seen: {type: integer, description:
                                                        "Instance first appearance in timestamp format"}
                                                    last_seen: {type: integer, description:
                                                        "Instance last appearance in timestamp format"}
                                                    saving: {type: number, description:
                                                        "Savings number"}
                                        options:
                                            type: object
                                            description: >
                                                Short living instances running options
                                                if short_living_instances type specified
                                            properties:
                                                days_threshold:
                                                    type: integer
                                                    description: Days threshold
                                                excluded_pools:
                                                    type: object
                                                    description: Pools exclusion map
                                                skip_cloud_accounts:
                                                    type: array
                                                    items:
                                                        type: string
                                                        description: Cloud account id to skip
                        dismissed_optimizations:
                            type: object
                            properties:
                                volumes_not_attached_for_a_long_time:
                                    type: object
                                    properties:
                                        count: {type: integer, description:
                                            "Optimization suppressed objects count"}
                                        saving: {type: number, description:
                                            "Optimization suppressed saving"}
                                        limit: {type: integer, description:
                                            "Max objects amount (limit applied)"}
                                        items:
                                            type: array
                                            description: >
                                                Optimization objects
                                                if volumes_not_attached_for_a_long_time type specified
                                            items:
                                                type: object
                                                properties:
                                                    cloud_resource_id: {type: string, description:
                                                        "Cloud volume id"}
                                                    resource_name: {type: string, description:
                                                        "Volume name"}
                                                    cloud_account_id: {type: string, description:
                                                        "Cloud account id"}
                                                    cloud_account_name: {type: string, description:
                                                        "Cloud account name"}
                                                    resource_id: {type: string, description:
                                                        "Volume id"}
                                                    cloud_type: {type: string, description:
                                                        "Cloud type"}
                                                    cost_in_detached_state: {type: integer, description:
                                                        "Volume cost in detached state"}
                                                    last_seen_in_attached_state: {type: integer, description:
                                                        "Volume last appearance in attached state in timestamp format"}
                                                    saving: {type: number, description:
                                                        "Savings number"}
                                        options:
                                            type: object
                                            description: >
                                                Short living instances running options
                                                if short_living_instances type specified
                                            properties:
                                                days_threshold:
                                                    type: integer
                                                    description: Days threshold
                                                excluded_pools:
                                                    type: object
                                                    description: Pools exclusion map
                                                skip_cloud_accounts:
                                                    type: array
                                                    items:
                                                        type: string
                                                        description: Cloud account id to skip
                        excluded_optimizations:
                            type: object
                            properties:
                                volumes_not_attached_for_a_long_time:
                                    type: object
                                    properties:
                                        count: {type: integer, description:
                                            "Optimization suppressed objects count"}
                                        saving: {type: number, description:
                                            "Optimization suppressed saving"}
                                        limit: {type: integer, description:
                                            "Max objects amount (limit applied)"}
                                        items:
                                            type: array
                                            description: >
                                                Optimization objects
                                                if volumes_not_attached_for_a_long_time type specified
                                            items:
                                                type: object
                                                properties:
                                                    cloud_resource_id: {type: string, description:
                                                        "Cloud volume id"}
                                                    resource_name: {type: string, description:
                                                        "Volume name"}
                                                    cloud_account_id: {type: string, description:
                                                        "Cloud account id"}
                                                    cloud_account_name: {type: string, description:
                                                        "Cloud account name"}
                                                    resource_id: {type: string, description:
                                                        "Volume id"}
                                                    cloud_type: {type: string, description:
                                                        "Cloud type"}
                                                    cost_in_detached_state: {type: integer, description:
                                                        "Volume cost in detached state"}
                                                    last_seen_in_attached_state: {type: integer, description:
                                                        "Volume last appearance in attached state in timestamp format"}
                                                    saving: {type: number, description:
                                                        "Savings number"}
                                        options:
                                            type: object
                                            description: >
                                                Optimization running options
                                                if volumes_not_attached_for_a_long_time type specified
                                            properties:
                                                days_threshold:
                                                    type: integer
                                                    description: Days threshold
                                                excluded_pools:
                                                    type: object
                                                    description: Pools exclusion map
                                                skip_cloud_accounts:
                                                    type: array
                                                    items:
                                                        type: string
                                                        description: Cloud account id to skip
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0217: Invalid type
                    - OE0216 Parameter is not provided
                    - OE0224: Wrong integer value
                    - OE0460: Status should be active, dismissed or excluded
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
                    - OE0002: Object not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        try:
            item = await self._get_item(organization_id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        try:
            types = self.get_arg('type', str, [], repeated=True)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        try:
            cloud_account_ids = self.get_arg(
                'cloud_account_id', str, [], repeated=True)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        limit = self.get_arg('limit', int, None)
        status = self.get_arg('status', str)
        overview = self.get_arg('overview', bool, False)
        if overview:
            if limit is not None:
                try:
                    check_int_attribute('limit', limit, min_length=1)
                except WrongArgumentsException as ex:
                    raise OptHTTPError.from_opt_exception(400, ex)
            for k, v in [('types', types), ('status', status)]:
                if v:
                    raise OptHTTPError(400, Err.OE0212, [k])
            status = 'active'
        elif types:
            if limit is not None:
                try:
                    check_int_attribute('limit', limit, min_length=1)
                except WrongArgumentsException as ex:
                    raise OptHTTPError.from_opt_exception(400, ex)
            if status is None:
                status = 'active'
            elif status not in ['active', 'dismissed', 'excluded']:
                raise OptHTTPError(400, Err.OE0460, [])
        elif limit:
            raise OptHTTPError(400, Err.OE0212, ['limit'])
        elif status:
            raise OptHTTPError(400, Err.OE0212, ['status'])
        res = await run_task(
            self.controller.get_optimizations,
            item, types, cloud_account_ids, limit, status, overview)
        self.write(json.dumps(res, cls=ModelEncoder))


class OptimizationDataAsyncCollectionHandler(BaseAsyncItemHandler,
                                             BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return OptimizationAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
            Get optimization data for specified type
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [optimization_data]
        summary: Optimization data for specified type
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: type
            type: string
            in: query
            description: Type for which optimization data must be returned
            required: true
        -   name: cloud_account_id
            type: array
            in: query
            items:
                type: string
            collectionFormat: multi
            description: Cloud accounts for which optimization data must be returned
            required: false
        -   name: status
            in: query
            description: Optimization data status
            required: false
            type: string
            default: active
            enum: [active, dismissed, excluded]
        -   name: limit
            in: query
            description: Limits amount of optimizations returned
            required: false
            type: integer
        -   name: format
            in: query
            description: Output format
            required: false
            type: string
            default: json
            enum: [json, xlsx]
        responses:
            200:
                description: Optimizations
                schema:
                    type: array
                    description: >
                        Short living instances objects
                        if short_living_instances type specified
                    items:
                        type: object
                        properties:
                            cloud_resource_id: {type: string, description:
                                "Cloud instance id"}
                            resource_name: {type: string, description:
                                "Instance name"}
                            cloud_account_id: {type: string, description:
                                "Cloud account id"}
                            cloud_account_name: {type: string, description:
                                "Cloud account name"}
                            resource_id: {type: string, description:
                                "Instance id"}
                            cloud_type: {type: string, description:
                                "Cloud type"}
                            total_cost: {type: integer, description:
                                "Instance lifetime cost"}
                            first_seen: {type: integer, description:
                                "Instance first appearance in timestamp format"}
                            last_seen: {type: integer, description:
                                "Instance last appearance in timestamp format"}
                            saving: {type: number, description:
                                "Savings number"}
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0216: Argument is not provided
                    - OE0217: Invalid type/limit
                    - OE0224: Wrong integer value
                    - OE0460: Status should be active, dismissed or excluded
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
        try:
            item = await self._get_item(organization_id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        opt_type = self.get_arg('type', str)
        try:
            check_string_attribute('type', opt_type)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        try:
            cloud_account_ids = self.get_arg(
                'cloud_account_id', str, [], repeated=True)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        opt_status = self.get_arg('status', str, 'active')
        if opt_status not in ['active', 'dismissed', 'excluded']:
            raise OptHTTPError(400, Err.OE0460, [])
        limit = self.get_arg('limit', int, 0)
        try:
            check_int_attribute('limit', limit)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        opt_format = self.get_arg('format', str, 'json')
        res = await run_task(
            self.controller.get_optimization_data,
            item, opt_type, cloud_account_ids, opt_status, limit)
        if opt_format == 'json':
            self.set_content_type('application/json; charset="utf-8"')
            self.write(json.dumps(res, cls=ModelEncoder, indent=4,
                                  sort_keys=True))
        elif opt_format == 'xlsx':
            self.set_content_type('application/vnd.openxmlformats-'
                                  'officedocument.spreadsheetml.sheet')
            self.write(object_to_xlsx(res))
        else:
            raise OptHTTPError(400, Err.OE0473, [opt_format])


class OptimizationDataAsyncItemHandler(BaseAsyncItemHandler,
                                       BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return OptimizationAsyncController

    def _validate_params(self, item, **kwargs):
        params = ['action', 'recommendation']
        unexpected = list(filter(lambda x: x not in params, kwargs.keys()))
        if unexpected:
            message = ', '.join(unexpected)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            for param in params:
                val = kwargs.get(param)
                check_string_attribute(param, val)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        if kwargs.get('action') not in ['activate', 'dismiss']:
            raise OptHTTPError(400, Err.OE0217, ['action'])
        if kwargs.get('recommendation') in ['obsolete_images',
                                            'short_living_instances']:
            raise OptHTTPError(400, Err.OE0217, ['recommendation'])
        super()._validate_params(item, **kwargs)

    async def patch(self, resource_id, **kwargs):
        """
        ---
        description: |
            Enable/disable recommendation for resource
            Required permission |
                MANAGE_RESOURCES or MANAGE_OWN_RESOURCES
        tags: [optimization_data]
        summary: Enable/disable recommendation for resource
        parameters:
        -   name: resource_id
            in: path
            description: resource ID
            required: True
            type: string
        -   in: body
            name: body
            description: body with action
            required: True
            schema:
                type: object
                properties:
                    action:
                        type: string
                        description: "activate or dismiss recommendation"
                        required: True
                        enum: [activate, dismiss]
                        example: activate
                    recommendation:
                        type: integer
                        description: "recommendation name"
                        required: True
                        example: instance_migration
        responses:
            200:
                description: Cloud resource data
                schema:
                    type: object
                    example:
                        deleted_at: 0
                        tags:
                            purpose: testing
                        cloud_console_link: cloud_console_link
                        created_at: 1614607531
                        resource_type: Instance'
                        cloud_account_id: a3eab0c0-e4ff-42e6-942a-cce5990cda38
                        pool_id: None
                        first_seen: 1612137600
                        region: us-west-1
                        employee_id: None
                        cloud_resource_id: i-0436ee72bb653bfca
                        organization_id: 5be74ae0-fe96-40b0-b65d-d76d974f6913
                        dismissed_recommendations:
                            -   run_timestamp: 1614675706
                                modules:
                                    average_saving: 3.519333333333333
                                    saving: 2.016
                                    flavor: t2.micro
                                    name: reserved_instances
                                    cloud_account_name: cloud_account_name
                                    resource_name: instance_name
                                    resource_id: 3b009a44-3290-4a09-9f12-dede6890acb7
                                    cloud_account_id: a3eab0c0-e4ff-42e6-942a-cce5990cda38
                                    cloud_resource_id: i-0436ee72bb653bfca
                                    cloud_type: aws_cnr
                                    region: us-west-1
                                    is_dismissed: True
                        recommendations:
                            -   run_timestamp: 1614675706
                                modules:
                                    saving: 0.5760000000000005
                                    flavor: t2.micro
                                    current_region: us-west-1
                                    recommended_region: us-east-2
                                    cloud_resource_id: i-0436ee72bb653bfca
                                    resource_name: instance_name
                                    resource_id: 3b009a44-3290-4a09-9f12-dede6890acb7
                                    cloud_account_id: a3eab0c0-e4ff-42e6-942a-cce5990cda38
                                    cloud_account_name: cloud_account_name
                                    cloud_type: azure_cnr
                                    name: instance_migration
                        dismissed:
                            -   reserved_instances
                        last_seen_not_stopped: 0
                        flavor: t2.micro
                        meta:
                            stopped_allocated: False
                            spotted: False
                            last_seen_not_stopped: 0
                        id: 3b009a44-3290-4a09-9f12-dede6890acb7
                        name: instance_name
                        last_seen: 1614684351
                        active: True
                        image_id: ami-021809d9177640a20
            400:
                description: |
                    Wrong arguments:
                    - OE0177: Non unique parameters in get request
                    - OE0216: Argument not provided
                    - OE0214: Argument should be a string
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0217: Invalid query parameter
                    - OE0233: Incorrect body received
                    - OE0416: Argument should not contain only whitespaces
            404:
                description: |
                    Not found:
                    - OE0002: Resource not found
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
        security:
        - token: []
        """
        data = self._request_body()
        try:
            resource = await run_task(
                self.controller.get_resource, resource_id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except FailedDependency as ex:
            raise OptHTTPError.from_opt_exception(424, ex)
        self._validate_params(resource, **data)
        user_id = await self.check_self_auth()
        owner_id = await run_task(
            self.controller.get_resource_owner, resource_id)
        if user_id == owner_id:
            await self.check_permissions(
                'MANAGE_OWN_RESOURCES', 'cloud_resource', resource_id)
        else:
            await self.check_permissions(
                'MANAGE_RESOURCES', 'cloud_resource', resource_id)
        res = await run_task(self.controller.process_resource_recommendation, resource, **data)
        self.write(json.dumps(res, cls=ModelEncoder))
