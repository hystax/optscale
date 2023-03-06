import json

from rest_api_server.exceptions import Err
from rest_api_server.models.models import Organization
from rest_api_server.utils import run_task, ModelEncoder, check_bool_attribute
from rest_api_server.controllers.pool import PoolAsyncController
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.base_async import (BaseAsyncCollectionHandler,
                                                    BaseAsyncItemHandler)
from rest_api_server.handlers.v1.base import BaseAuthHandler

from optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException)
from optscale_exceptions.http_exc import OptHTTPError


class PoolAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                 BaseAuthHandler,
                                 BaseHandler):
    def _get_controller_class(self):
        return PoolAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of pools where current user has specified permissions.
            Required permission: MANAGE_OWN_RESOURCES or MANAGE_RESOURCES
        tags: [organizations]
        summary: "List of pools where current user has specified permissions"
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   name: permission
            in: query
            description: >
                permission to check. Defaults to
                [MANAGE_RESOURCES, MANAGE_OWN_RESOURCES]
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: condition
            in: query
            description: >
                Condition to use when multiple permission specify. If "and"
                condition used, user must have all specified permission, if "or"
                - at least one of them. Defaults to "or"
            required: false
            type: string
            enum: [or, and]
        responses:
            200:
                description: pool list
                schema:
                    type: object
                    properties:
                        pools:
                            type: array
                            items:
                                type: object
                            example:
                                - organization_id: 99843c5d-462e-4f1b-8774-661cd108c8a7
                                  id: e1a3bb04-d513-42d2-b9b7-019d24097dec
                                  name: Frontend
                                  full_name: Development->OptScale->Frontend
                                  pool_purpose: team
                                  limit: 0
                                  parent_id: 8ec4bf2e-6e89-4f97-b6a2-c6d3675934f3
                                  default_owner_id: 3d5a56e1-6e48-4d65-945a-a46f3a48e6e3
                                  default_owner_name: name
                                - organization_id: f0234a8e-cb83-4dd2-951e-b34fe288bc4b
                                  id: aea929ab-3103-4932-a77c-ca0a758a992b
                                  name: DevOps
                                  full_name: DevOps
                                  pool_purpose: team
                                  limit: 0
                                  parent_id: 24ce5db0-ad17-48ca-91de-9a3f703568bb
                                  default_owner_id: 3d5a56e1-6e48-4d65-945a-a46f3a48e6e3
                                  default_owner_name: name
                                - organization_id: 75d0c441-2a3e-47f4-a651-493325a87ae8
                                  id: 7cf3f859-7282-467a-bcd8-c7c2f766f7ba
                                  name: AnyCloud
                                  full_name: Development->OptScale->AnyCloud
                                  pool_purpose: pool
                                  limit: 0
                                  parent_id: d6f8fd73-a8f3-402a-9c37-b9cf65c6e94f
                                  default_owner_id: 3d5a56e1-6e48-4d65-945a-a46f3a48e6e3
                                  default_owner_name: name
                                - organization_id: f0234a8e-cb83-4dd2-951e-b34fe288bc4b
                                  id: f4f3c965-0ac4-4d8e-a0e2-79aac8ba00d8
                                  name: Max K
                                  full_name: DevOps->Max K
                                  pool_purpose: pool
                                  limit: 0
                                  parent_id: c5fb0a06-b5d7-489d-9c59-2cc03ba8664f
                                  default_owner_id: 3d5a56e1-6e48-4d65-945a-a46f3a48e6e3
                                  default_owner_name: name
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0378: User is not a member of organization
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        """
        user_id = await self.check_self_auth()
        permissions = self.get_arg('permission', str, repeated=True,
                                   default=['MANAGE_RESOURCES',
                                            'MANAGE_OWN_RESOURCES'])
        condition = self.get_arg('condition', str, default='or')
        res = await run_task(self.controller.get_all_available_pools,
                             user_id, organization_id, self.token,
                             permissions, condition)
        self.write(json.dumps({'pools': res}, cls=ModelEncoder))

    async def post(self, organization_id):
        """
        ---
        description: |
            Create sub pool for organization
            Required permission: MANAGE_POOLS
        tags: [organizations]
        summary: "Create sub pool for the organization"
        parameters:
        -   in: path
            name: organization_id
            description: Organization id
            required: true
        -   in: body
            name: body
            description: Pool to add
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: Pool name
                        required: True
                        example: Development
                    limit:
                        type: integer
                        description: Pool limit value
                        required: False
                        default: 0
                        example: 300
                    parent_id:
                        type: string
                        description: Parent pool id
                        required: False
                        example: 08f280c0-3703-45c5-b4c0-de8fddecce19
                    purpose:
                        type: string
                        description: Pool purpose
                        required: False
                        example: team
                    auto_extension:
                        type: boolean
                        description: Automatic extension of parent pools if needed
                        required: False
        responses:
            200:
                description: Success (returns created object)
                schema:
                    type: object
                    example:
                        id: 64a7424c-0745-4926-bb6d-2125b16c91f9
                        organization_id: 08704f0b-9226-452f-8834-47978d4409a6
                        limit: 0
                        default_owner_id: 996f6ed5-e847-429a-91c2-ac43018cf7cf
                        parent_id: "97df7dd7-b675-4373-add2-cc2b9716b307"
                        default_owner_id: a201ff8c-691b-4d51-8885-cbccdec05027
                        default_owner_name: John Doe
                        name: test name
                        purpose: team
                        created_at: 1585680056
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0003: Database error
                    - OE0217: Invalid query parameter
                    - OE0226: Should be True or False
                    - OE0407: Child pool limit value exceeds parent limit
                    - OE0414: Parent pool limit less than the limit of the child pools
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
                    - OE0378: User is not a member of organization
                    - OE0471: Not enough permissions to extend the pool limit
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        """
        data = self._request_body()

        org = await run_task(self.controller.get_org_by_id, organization_id)
        if org is None:
            raise OptHTTPError(404, Err.OE0002, [Organization.__name__,
                                                 organization_id])
        if not data.get('parent_id'):
            data['parent_id'] = org.pool_id
        await self.check_permissions('MANAGE_POOLS', 'pool',
                                     data.get('parent_id'))

        auto_extension = data.pop('auto_extension', False)
        try:
            check_bool_attribute('auto_extension', auto_extension)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        res = await run_task(self.controller.create,
                             organization_id=organization_id,
                             auto_extension=auto_extension, **data)
        self.set_status(201)
        self.write(json.dumps(res.to_dict(), cls=ModelEncoder))


class PoolAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                           BaseHandler):
    def _get_controller_class(self):
        return PoolAsyncController

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get pool info by ID
            Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
        tags: [pools]
        summary: Get pool
        parameters:
        -   name: id
            in: path
            description: Pool ID
            required: true
            type: string
        -   name: details
            in: query
            description: display pool details (policies,recommendation,expenses)
            required: false
            type: boolean
        -   name: children
            in: query
            description: display also children info
            required: false
            type: boolean
        responses:
            200:
                description: Pool data
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Unique pool id
                        parent_id:
                            type: string
                            description: Parent pool id
                        name:
                            type: string
                            description: pool name
                        organization_id:
                            type: string
                            description: organization id
                        limit:
                            type: integer
                            description: Allocated pool limit
                        deleted_at:
                            type: integer
                            description: Deleted timestamp (service field)
                        created_at:
                            type: integer
                            description: Created timestamp (service field)
                        default_owner_id:
                            type: string
                            description: default owner id
                        default_owner_name:
                            type: string
                            description: default owner name
                        cost:
                            type: integer
                            description: "expenses for this month"
                        forecast:
                            type: integer
                            description: "expense forecast for current month"
                        children:
                            type: array
                            description: pool children (when children is true)
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description: "Unique pool id"}
                                    name: {type: string,
                                        description: "Pool display name"}
                                    deleted_at: {type: string,
                                        description:
                                        "Deleted timestamp (service field)"}
                                    parent_id: {type: string,
                                        description: "Pool's parent id"}
                                    limit: {type: integer,
                                        description: "pool limit value"}
                                    cost: {type: integer,
                                        description: "expenses for this month"}
                                    forecast: {type: integer,
                                        description: "expense forecast for current month"}
                                    policies:
                                        type: array
                                        items:
                                            type: object
                                            example:
                                                -   id: 214165df-084b-4a4d-9abc-fe4830efb095
                                                    pool_id: 0b37f939-ece5-4f56-85ab-397718567fb9
                                                    type: ttl
                                                    active: True
                                                    limit: 100
                                                    created_at: 1587029026
                                                    deleted_at: 0
                                                -   id: 214165df-084b-4a4d-9abc-fe4830efb095
                                                    pool_id: 0b37f939-ece5-4f56-85ab-397718567fb9
                                                    type: total_expense_limit
                                                    active: False
                                                    limit: 150
                                                    created_at: 1587029026
                                                    deleted_at: 0
                                                -   id: 1bca7ecb-e5e7-4982-81c3-c1a37bc921c9
                                                    resource_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                                    type: daily_expense_limit
                                                    active: False
                                                    limit: 100
                                                    created_at: 1587029026
                                                    deleted_at: 0
                        policies:
                            type: array
                            items:
                                type: object
                                example:
                                    -   id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                                        pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                        type: ttl
                                        active: True
                                        limit: 300
                                        created_at: 1587029026
                                        deleted_at: 0
                                    -   id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                                        pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                        type: total_expense_limit
                                        active: False
                                        limit: 1000
                                        created_at: 1587029026
                                        deleted_at: 0
                                    -   id: 1bca7ecb-e5e7-4982-81c3-c1a37bc921c9
                                        resource_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                        type: daily_expense_limit
                                        active: False
                                        limit: 500
                                        created_at: 1587029026
                                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            404:
                description: |
                    Not found:
                    - OE0002: Pool not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('INFO_ORGANIZATION', 'pool', id)
        try:
            item = await self._get_item(id, **kwargs)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        item_dict = item.to_dict()
        show_details = self.get_arg('details', bool, False)
        show_children = self.get_arg('children', bool, False)
        if show_details or show_children:
            task = await run_task(self.controller.get_details,
                                  item_dict, forecast=True,
                                  show_children=show_children,
                                  show_details=show_details)
            children, pool_limit_cost = task
            if show_children:
                item_dict['children'] = children
            if show_details:
                item_dict.update(**pool_limit_cost)
                item_dict.update({
                    'policies': [policy.to_dict() for policy
                                 in item.policies if not policy.deleted]
                })
        else:
            link = await run_task(self.controller.get_export_link, id)
            if link:
                item_dict['expenses_export_link'] = link
        self.write(json.dumps(item_dict, cls=ModelEncoder))

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing pool
            Required permission: MANAGE_POOLS
        tags: [pools]
        summary: Edit pool
        parameters:
        -   name: id
            in: path
            description: Pool ID
            required: true
            type: string
        -   in: body
            name: body
            description: Pool changes
            required: false
            schema:
                type: object
                properties:
                    parent_id:
                        type: string
                        description: Parent pool id
                    name:
                        type: string
                        description: Pool name
                    limit:
                        type: integer
                        description: Allocated pool limit
                    default_owner_id:
                        type: string
                        description: Default owner id for pool
                    auto_extension:
                        type: boolean
                        description: Automatic extension of parent pools if needed
        responses:
            200:
                description: Success (returns modified object)
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            400:
                description: |
                    Wrong arguments:
                    - OE0211: Parameter is immutable
                    - OE0212: Unexpected parameters
                    - OE0223: Should be an integer
                    - OE0224: Wrong integer argument value
                    - OE0226: Should be True or False
                    - OE0407: Child pool limit value exceeds parent limit
                    - OE0414: Parent pool limit less than the limit of the child pools
                    - OE0449: Field cannot be changed
            403:
                description: |
                    Forbidden:
                    - OE0471: Not enough permissions to extend the pool limit
            404:
                description: |
                    Not found:
                    - OE0002: Pool not found
        security:
        - token: []
        """
        data = self._request_body()
        auto_extension = data.pop('auto_extension', False)
        if auto_extension:
            user_id = await self.check_self_auth()
            data.update({'user_id': user_id})
        await self.check_permissions('MANAGE_POOLS', 'pool', id)
        res = await run_task(self.controller.edit, id, auto_extension, **data)
        self.write(res.to_json())

    async def delete(self, id, **kwargs):
        """
        ---
        description: |
            Deletes an existing pool
            Required permission: MANAGE_POOLS
        tags: [pools]
        summary: Delete pool
        parameters:
        -   name: id
            in: path
            description: Pool ID
            required: true
            type: string
        responses:
            204:
                description: Success
            400:
                description: |
                    Not found:
                    - OE0447: Root pool can't be deleted
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            404:
                description: |
                    Not found:
                    - OE0002: Pool not found
            424:
                description: |
                    Failed dependency:
                    - OE0411: Pool has not deleted children
                    - OE0459: The pool does not have default_owner_id
        security:
        - token: []
        """
        try:
            item = await self._get_item(id, **kwargs)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        if not item.parent_id:
            raise OptHTTPError(400, Err.OE0447, [])
        await self.check_permissions(
            'MANAGE_POOLS', 'pool', item.parent_id)
        await super().delete(id, **kwargs)
