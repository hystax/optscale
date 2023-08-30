import json
from collections import defaultdict
from rest_api.rest_api_server.controllers.resource_constraint import (
    ResourceConstraintAsyncController,
    ResourceConstraintOrganizationAsyncController)
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import NotFoundException
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder


class ResourceConstraintsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                                BaseAuthHandler):

    def _get_controller_class(self):
        return ResourceConstraintAsyncController

    async def post(self, resource_id, **url_params):
        """
        ---
        description: |
            Create constraint for resource
            Required permission: MANAGE_RESOURCES or MANAGE_OWN_RESOURCES
        tags: [resource_constraints]
        summary: Create constraint for resource
        parameters:
        -   name: resource_id
            in: path
            description: Resource id
            required: true
            type: string
        -   in: body
            name: body
            description: Constraint info to add
            required: true
            schema:
                type: object
                properties:
                    limit:
                        type: integer
                        description: |
                            Violation limit (timestamp or expense value).
                            Set 0 for infinite
                        required: True
                        example: 80
                    type:
                        type: string
                        required: False
                        description: Constraint type
                        enum: [ttl, total_expense_limit, daily_expense_limit]
                        example: 'ttl'
        responses:
            201:
                description: Created (returns created constraint)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        resource_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        type: ttl
                        limit: 1615884970
                        created_at: 1587029026
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0004: "type" is not a valid ConditionTypes
                    - OE0216: Argument not provided
                    - OE0214: Argument should be a string
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0233: Incorrect body received
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
                    - OE0456: Duplicate path parameters in the request body
                    - OE0461: Limit can't be in past
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Resource not found
            409:
                description: |
                    Conflict:
                    - OE0441: Constraint with type already exists for resource
            424:
                description: |
                    Failed dependency:
                    - OE0443: Resource is not active
        security:
        - token: []
        """
        user_id = await self.check_self_auth()
        owner_id = await run_task(
            self.controller.get_resource_owner, resource_id)
        if user_id == owner_id:
            await self.check_permissions(
                'MANAGE_OWN_RESOURCES', 'cloud_resource', resource_id)
        else:
            await self.check_permissions(
                'MANAGE_RESOURCES', 'cloud_resource', resource_id)
        await super().post(resource_id=resource_id, **url_params)

    async def get(self, resource_id):
        """
        ---
        description: |
            Get list of constraints for resource
            Required permission: INFO_ORGANIZATION
        tags: [resource_constraints]
        summary: List of constraints for resource
        parameters:
        -   in: path
            name: resource_id
            description: id of the resource
            required: true
        responses:
            200:
                description: constraints list
                schema:
                    type: object
                    example:
                        constraints:
                            type: array
                            items:
                                type: object
                            example:
                                -   id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                                    resource_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                    type: ttl
                                    limit: 1615884970
                                    created_at: 1587029026
                                    deleted_at: 0
                                -   id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                                    resource_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                    type: total_expense_limit
                                    limit: 1000
                                    created_at: 1587029026
                                    deleted_at: 0
                                -   id: 1bca7ecb-e5e7-4982-81c3-c1a37bc921c9
                                    resource_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                    type: daily_expense_limit
                                    limit: 500
                                    created_at: 1587029026
                                    deleted_at: 0
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Resource not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'cloud_resource', resource_id)
        res = await run_task(self.controller.list, resource_id=resource_id)
        constraints = {'constraints': [
            constraint.to_dict() for constraint in res
        ]}
        self.write(json.dumps(constraints, cls=ModelEncoder))


class OrganizationConstraintsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                                    BaseAuthHandler,
                                                    BaseHandler):

    def _get_controller_class(self):
        return ResourceConstraintOrganizationAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of resource constraints for organization
            Required permission: INFO_ORGANIZATION
        tags: [global_constraints]
        summary: List of resource constraints for organization
        parameters:
        -   in: path
            name: organization_id
            description: id of the organization
            required: true
        -   name: details
            in: query
            type: boolean
            description: Resource info for constraint
            required: false
        responses:
            200:
                description: Resource constraint list
                schema:
                    type: object
                    properties:
                        resource_constraints:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description:
                                        "Unique pool policy id"}
                                    created_at: {type: integer,
                                        description:
                                        "Created timestamp (service field)"}
                                    deleted_at: {type: integer,
                                        description:
                                        "Deleted timestamp (service field)"}
                                    type: {type: string,
                                        description: "Constraint type:
                                        ('TTL','DAILY_EXPENSE_LIMIT')"}
                                    limit: {type: integer,
                                        description:
                                        "Constraint limit"}
                                    resource_id: {type: string,
                                        description: "Resource id"}
                                    organization_id: {type: string,
                                        description: "Organization id"}
                                    details:
                                        type: object
                                        properties:
                                            active: {type: boolean,
                                                description: "Resource active
                                                flag"}
                                            cloud_resource_id: {type: string,
                                                description: "Resource id in
                                                cloud"}
                                            employee_id: {type: string,
                                                description: "Cloud resource
                                                owner id"}
                                            constraint_violated: {type: boolean,
                                                description: "Is resource
                                                constraint violated"}
                                            pool:
                                                type: object
                                                properties:
                                                    id: {type: string,
                                                        description: "Unique
                                                        pool id"}
                                                    name: {type: string,
                                                        description: "Pool
                                                        name"}
                                                    purpose: {type: string,
                                                        description: "Pool
                                                        purpose"}
                                            owner:
                                                type: object
                                                properties:
                                                    id: {type: string,
                                                        description: "Unique
                                                        employee id"}
                                                    name: {type: string,
                                                        description: "Employee
                                                        name"}
                                            name: {type: string,
                                                description: "Cloud resource
                                                name"}
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        """
        await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                     organization_id)
        res = await run_task(self.controller.list,
                             organization_id=organization_id)
        constraints_map = defaultdict(list)
        for constraint in res:
            constraints_map[constraint.resource_id].append(constraint.to_dict())
        resource_res = await run_task(self.controller.get_resources,
                                      resource_ids=list(constraints_map.keys()),
                                      organization_id=organization_id)
        resource_map = {}
        for resource_info in resource_res:
            res_id = resource_info.pop('id', None)
            resource_map[res_id] = resource_info
        constraints = []
        for res_id, res_constraints in constraints_map.items():
            if res_id in resource_map:
                constraints.extend(res_constraints)
        details = self.get_arg('details', bool, False)
        if details:
            for constraint_dict in constraints:
                resource_id = constraint_dict['resource_id']
                constraint_dict['details'] = resource_map.get(resource_id)
        self.write(json.dumps({'resource_constraints': constraints},
                              cls=ModelEncoder))


class ResourceConstraintsAsyncItemHandler(BaseAsyncItemHandler,
                                          BaseAuthHandler):

    def _get_controller_class(self):
        return ResourceConstraintAsyncController

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get constraint info by ID
            Required permission: INFO_ORGANIZATION
        tags: [resource_constraints]
        summary: Get resource constraint
        parameters:
        -   name: id
            in: path
            description: Constraint ID
            required: true
            type: string
        responses:
            200:
                description: Constraint data
                schema:
                    type: object
                    example:
                        id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                        resource_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        type: total_expense_limit
                        limit: 1000
                        created_at: 1587029026
                        deleted_at: 0
            404:
                description: |
                    Not found:
                    - OE0002: Constraint not found
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            404:
                description: |
                    Not found:
                    - OE0002: Resource constraint not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'resource_constraint', id)
        await super().get(id, **kwargs)

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing constraint

            Required permissions: MANAGE_RESOURCES or MANAGE_OWN_RESOURCES
        tags: [resource_constraints]
        summary: Edit constraint
        parameters:
        -   name: id
            in: path
            description: constraint ID
            required: True
            type: string
        -   in: body
            name: body
            description: New constraint params
            required: True
            schema:
                type: object
                properties:
                    limit:
                        type: integer
                        description:  |
                            Violation limit (timestamp or expense value).
                            Set 0 for infinite
                        required: False
                        example: 80
        responses:
            201:
                description: Created (returns modified constraint)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        resource_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        type: total_expense_limit
                        limit: 1000
                        created_at: 1587029026
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0211: Parameter is immutable
                    - OE0216: Argument not provided
                    - OE0214: Argument should be a string
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0233: Incorrect body received
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
            404:
                description: |
                    Not found:
                    - OE0002: Constraint not found
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
        data.update(kwargs)
        try:
            resource_constraint = await self._get_item(id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        resource_id = resource_constraint.resource_id
        user_id = await self.check_self_auth()
        owner_id = await run_task(
            self.controller.get_resource_owner, resource_id)
        if user_id == owner_id:
            await self.check_permissions(
                'MANAGE_OWN_RESOURCES', 'resource_constraint', id)
        else:
            await self.check_permissions(
                'MANAGE_RESOURCES', 'resource_constraint', id)
        await super().patch(id, **data)

    async def delete(self, id, **kwargs):
        """
        ---
        description: |
            Deletes constraint with specified id
            Required permission: MANAGE_RESOURCES or MANAGE_OWN_RESOURCES
        tags: [resource_constraints]
        summary: Delete resource constraint
        parameters:
        -   name: id
            in: path
            description: Constraint ID
            required: true
            type: string
        responses:
            204:
                description: Success
            404:
                description: |
                    Not found:
                    - OE0002: Constraint not found
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
        try:
            resource_constraint = await self._get_item(id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        resource_id = resource_constraint.resource_id
        user_id = await self.check_self_auth()
        owner_id = await run_task(
            self.controller.get_resource_owner, resource_id)
        if user_id == owner_id:
            await self.check_permissions(
                'MANAGE_OWN_RESOURCES', 'resource_constraint', id)
        else:
            await self.check_permissions(
                'MANAGE_RESOURCES', 'resource_constraint', id)
        await super().delete(id, **kwargs)
