import json

from optscale_exceptions.common_exc import NotFoundException, WrongArgumentsException
from optscale_exceptions.http_exc import OptHTTPError
from rest_api_server.controllers.my_tasks import MyTasksAsyncController
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler

from rest_api_server.utils import (run_task, ModelEncoder)


class MyTasksAsyncHandler(BaseAsyncItemHandler, BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return MyTasksAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
            Get organization tasks for the user
            Only tasks with non-zero count returned
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [my_tasks]
        summary: Get organization tasks for the user
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
            required: true
            type: string
        -   name: type
            type: array
            in: query
            items:
                type: string
            collectionFormat: multi
            description: types for which details must be returned
            required: false
        responses:
            200:
                description: My Tasks
                schema:
                    type: object
                    properties:
                        incoming_assignment_requests:
                            type: object
                            properties:
                                count:
                                    type: integer
                                    description: >
                                        count of active assignment requests with
                                        current user as an approver
                                tasks:
                                    description: >
                                        info about assignment requests where
                                        approver_id is an employee of the user
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            assignment_request_id:
                                                type: string
                                                description: id of the request
                                            resource_id:
                                                type: string
                                                description: id of the resource
                                            source_pool_id:
                                                type: string
                                                description: >
                                                    current resource pool
                                            requester_id:
                                                type: string
                                                description: >
                                                    employee id of person who
                                                    created request
                                            message:
                                                type: string
                                                description: >
                                                    message from request
                                            resource_type:
                                                type: string
                                                description: >
                                                    type of the resource
                                            source_pool_name:
                                                type: string
                                                description: >
                                                    name of the current resource
                                                    pool
                                            source_pool_purpose:
                                                type: string
                                                description: >
                                                    purpose of the current
                                                    resource pool
                                            requester_name:
                                                type: string
                                                description: >
                                                    name of the employee who
                                                    created request
                                            resource_name:
                                                type: string
                                                description: resource name
                                            cluster_type_id:
                                                type: string
                                                description: id of the cluster type (only for cluster resource)
                        outgoing_assignment_requests:
                            type: object
                            properties:
                                count:
                                    type: integer
                                    description: >
                                        count of active assignment requests
                                        created by current user
                                tasks:
                                    description: >
                                        info about assignment requests where
                                        requester_id is an employee of the user
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            assignment_request_id:
                                                type: string
                                                description: id of the request
                                            resource_id:
                                                type: string
                                                description: id of the resource
                                            source_pool_id:
                                                type: string
                                                description: >
                                                    current resource pool
                                            approver_id:
                                                type: string
                                                description: >
                                                    employee id of the person
                                                    who will approve the request
                                            message:
                                                type: string
                                                description: >
                                                    message from request
                                            resource_type:
                                                type: string
                                                description: >
                                                    type of the resource
                                            source_pool_name:
                                                type: string
                                                description: >
                                                    name of the current resource
                                                    pool
                                            source_pool_purpose:
                                                type: string
                                                description: >
                                                    purpose of the current
                                                    resource pool
                                            approver_name:
                                                type: string
                                                description: >
                                                    name of the person
                                                    who will approve the request
                                            resource_name:
                                                type: string
                                                description: resource name
                                            cluster_type_id:
                                                type: string
                                                description: id of the cluster type (only for cluster resource)
                        exceeded_pools:
                            type: object
                            properties:
                                count:
                                    type: integer
                                    description: >
                                        count of pools that exceed limit
                                        value
                                tasks:
                                    description: >
                                        info about exceeded pools
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            pool_id:
                                                type: string
                                                description: pool id
                                            pool_name:
                                                type: string
                                                description: pool name
                                            pool_purpose:
                                                type: string
                                                description: pool purpose
                                            limit:
                                                type: integer
                                                description: pool limit value
                                            total_expenses:
                                                type: number
                                                description: >
                                                    total amount of expenses
                                                    calculated for the pool limit
                                                    in current month
                                            forecast:
                                                type: number
                                                description: >
                                                    pool limit forecast for current
                                                    month
                        exceeded_pool_forecasts:
                            type: object
                            properties:
                                count:
                                    type: integer
                                    description: >
                                        count of pools that exceed forecast
                                        value
                                tasks:
                                    description: >
                                        info about exceeded pools
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            pool_id:
                                                type: string
                                                description: pool id
                                            pool_name:
                                                type: string
                                                description: pool name
                                            pool_purpose:
                                                type: string
                                                description: pool purpose
                                            limit:
                                                type: integer
                                                description: pool limit value
                                            total_expenses:
                                                type: number
                                                description: >
                                                    total amount of expenses
                                                    calculated for the pool
                                                    in current month
                                            forecast:
                                                type: number
                                                description: >
                                                    pool limit forecast for current
                                                    month
                        violated_constraints:
                            type: object
                            properties:
                                count:
                                    type: integer
                                    description: >
                                        amount of violated constraints
                                tasks:
                                    description: >
                                        info about violated constraints
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            id:
                                                type: string
                                                description: >
                                                    constraint id
                                            resource_id:
                                                type: string
                                                description: >
                                                    resource id of constraint
                                            pool_id:
                                                type: string
                                                description: >
                                                    pool id of resource
                                            type:
                                                type: string
                                                description: >
                                                    constraint type
                                            constraint_limit:
                                                type: string
                                                description: >
                                                    constraint limit
                                            time:
                                                type: string
                                                description: >
                                                    constraint limit hit time
                                            ttl_value:
                                                type: integer
                                                description: |
                                                    Timestamp that violated
                                                    constraint (only for TTL
                                                    constraint)
                                            expense_value:
                                                type: float
                                                description: |
                                                    Value that violated
                                                    constraint (only for expense
                                                    constraint)
                                            pool_name:
                                                type: string
                                                description: >
                                                    name of the pool
                                            resource_name:
                                                type: string
                                                description: resource name
                                            cloud_resource_id:
                                                type: string
                                                description: >
                                                    id of the resource in cloud
                                            resource_type:
                                                type: string
                                                description: >
                                                    type of the resource
                                            owner_id:
                                                type: string
                                                description: >
                                                    owner id of resource
                                            owner_name:
                                                type: string
                                                description: >
                                                    owner name of resource
                        differ_constraints:
                            type: object
                            properties:
                                count:
                                    type: integer
                                    description: >
                                        amount of differ constraints
                                tasks:
                                    description: >
                                        info about differ constraints
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            id:
                                                type: string
                                                description: >
                                                    constraint id
                                            type:
                                                type: string
                                                description: >
                                                    constraint type
                                            limit:
                                                type: string
                                                description: >
                                                    constraint limit
                                            resource_id:
                                                type: string
                                                description: >
                                                    resource id of constraint
                                            resource_name:
                                                type: string
                                                description: resource name
                                            cloud_resource_id:
                                                type: string
                                                description: >
                                                    id of the resource in cloud
                                            resource_type:
                                                type: string
                                                description: >
                                                    type of the resource
                                            owner_id:
                                                type: string
                                                description: >
                                                    owner id of resource
                                            owner_name:
                                                type: string
                                                description: >
                                                    owner name of resource
                                            pool_id:
                                                type: string
                                                description: >
                                                    pool id of resource
                                            pool_name:
                                                type: string
                                                description: >
                                                    pool name of resource
                                            policy:
                                                description: >
                                                    info about pool policy
                                                type: array
                                                items:
                                                    type: object
                                                    properties:
                                                        id:
                                                            type: string
                                                            description: >
                                                                policy id
                                                        type:
                                                            type: string
                                                            description: >
                                                                policy type
                                                        limit:
                                                            type: string
                                                            description: >
                                                                policy limit
                                                        pool_id:
                                                            type: string
                                                            description: >
                                                                pool id
                                                        pool_name:
                                                            type: string
                                                            description: >
                                                                name of the pool
                                                        active:
                                                            type: boolean
                                                            description: >
                                                                is policy active
                        violated_organization_constraints:
                            type: object
                            properties:
                                count:
                                    type: integer
                                    description: >
                                        count of violated organization
                                        constraints
                                tasks:
                                    description: >
                                        info about violated organization
                                        constraints
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            id:
                                                type: string
                                                description: limit hit id
                                            constraint_id:
                                                type: string
                                                description: >
                                                    organization constraint id
                                            organization_id:
                                                type: string
                                                description: organization id
                                            deleted_at:
                                                type: integer
                                                description: >
                                                    deleted timestamp (service
                                                    field)
                                            created_at:
                                                type: integer
                                                description: >
                                                    timestamp of limit hit
                                                    creation
                                            constraint_limit:
                                                type: float
                                                description: >
                                                    constraint limit that was
                                                    violated
                                            value:
                                                type: float
                                                description: violated value
                                            name:
                                                type: string
                                                description: constraint name
                                            type:
                                                type: string
                                                description: >
                                                    Organization constraint type
                                                enum: [expense_anomaly, resource_count_anomaly]
                                            definition:
                                                type: object
                                                properties:
                                                    threshold:
                                                        type: integer
                                                        description: threshold value
                                                    threshold_days:
                                                        type: integer
                                                        description: >
                                                            number of days for
                                                            average calculating
                                            filters:
                                                type: object
                                                description: >
                                                    set of filters for dataset
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0216: Argument is not provided
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer value
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
                    - OE0378: User is not a member of organization
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        - secret: []
        """
        user_id = self.get_arg('user_id', str, None)
        if user_id:
            self.check_cluster_secret()
        else:
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
            user_id = await self.check_self_auth()
        try:
            org = await self._get_item(organization_id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        try:
            types = self.get_arg('type', str, [], repeated=True)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)

        res = await run_task(self.controller.get_tasks, user_id, org, types)
        self.write(json.dumps(res, cls=ModelEncoder))
