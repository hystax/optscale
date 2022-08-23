import json

from rest_api_server.controllers.cluster_type import (
    ClusterTypeAsyncController, ClusterTypeApplyAsyncController)
from rest_api_server.exceptions import Err
from rest_api_server.handlers.v1.base_async import (BaseAsyncCollectionHandler,
                                                    BaseAsyncItemHandler)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.utils import run_task, ModelEncoder

from optscale_exceptions.http_exc import OptHTTPError
from optscale_exceptions.common_exc import WrongArgumentsException


class ClusterTypeAsyncCollectionHandler(BaseAsyncCollectionHandler, BaseAuthHandler,
                                        BaseHandler):
    def _get_controller_class(self):
        return ClusterTypeAsyncController

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create cluster type
            Required permission: MANAGE_RESOURCES
        tags: [cluster_types]
        summary: Create cluster type
        parameters:
        -   in: path
            name: organization_id
            description: Organization id
            required: true
        -   in: body
            name: body
            description: Cluster type info
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: "Cluster type name"
                        required: true
                    tag_key:
                        type: string
                        description: "Tag key name to create clusters"
                        required: true
        responses:
            201:
                description: Created (returns created object)
                schema:
                    type: object
                    properties:
                        id: {type: string, description:
                            "Cluster type id"}
                        deleted_at: {type: integer, description:
                            "Deleted timestamp (service field)"}
                        created_at: {type: integer, description:
                            "Created timestamp (service field)"}
                        organization_id: {type: string, description:
                            "Organization id"}
                        name: {type: string, description:
                            "Cluster type name"}
                        tag_key: {type: string, description:
                            "Tag key to create clusters"}
                        priority: {type: integer, description:
                            "Priority"}
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument not provided
                    - OE0233: Incorrect body received
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
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
            409:
                description: |
                    Conflict:
                    - OE0149: Cluster type with name already exist
        security:
        - token: []
        """
        await self.check_permissions('MANAGE_RESOURCES', 'organization',
                                     organization_id)
        await super().post(organization_id=organization_id, **url_params)

    def _validate_params(self, **kwargs):
        expected = ['name', 'tag_key', 'organization_id']
        not_provided = list(filter(lambda x: x not in kwargs.keys(), expected))
        if not_provided:
            raise OptHTTPError(400, Err.OE0216, [not_provided[0]])
        unexpected = list(filter(lambda x: x not in expected, kwargs.keys()))
        if unexpected:
            raise OptHTTPError(400, Err.OE0212, [', '.join(unexpected)])

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of organization cluster types
            Required permission: INFO_ORGANIZATION
        tags: [cluster_types]
        summary: List cluster types
        parameters:
        -   in: path
            name: organization_id
            description: Organization id
            required: true
        responses:
            200:
                description: Cluster types list
                schema:
                    type: object
                    properties:
                        cluster_types:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string, description:
                                        "Cluster type id"}
                                    deleted_at: {type: integer, description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer, description:
                                        "Created timestamp (service field)"}
                                    organization_id: {type: string, description:
                                        "Organization id"}
                                    name: {type: string, description:
                                        "Cluster type name"}
                                    tag_key: {type: string, description:
                                        "Tag key to create clusters"}
                                    priority: {type: integer, description:
                                        "Priority"}
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
        """
        await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                     organization_id)
        res = await run_task(self.controller.list, organization_id)
        self.write(json.dumps(res, cls=ModelEncoder))


class ClusterTypeAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return ClusterTypeAsyncController

    def _validate_action(self, action):
        if not action:
            raise OptHTTPError(400, Err.OE0216, ['action'])
        if not isinstance(action, str):
            raise OptHTTPError(400, Err.OE0214, ['action'])
        if action not in ['prioritize', 'promote', 'demote', 'deprioritize']:
            raise OptHTTPError(400, Err.OE0166, [action])

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get cluster type
            Required permission: INFO_ORGANIZATION
        tags: [cluster_types]
        summary: Get cluster type
        parameters:
        -   in: path
            name: id
            description: Cluster type id
            required: true
        responses:
            200:
                description: Cluster type data
                schema:
                    type: object
                    properties:
                        id: {type: string, description:
                            "Cluster type id"}
                        deleted_at: {type: integer, description:
                            "Deleted timestamp (service field)"}
                        created_at: {type: integer, description:
                            "Created timestamp (service field)"}
                        organization_id: {type: string, description:
                            "Organization id"}
                        name: {type: string, description:
                            "Cluster type name"}
                        tag_key: {type: string, description:
                            "Tag key to create clusters"}
                        priority: {type: integer, description:
                            "Priority"}
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
                    - OE0002: Cluster type not found
        security:
        - token: []
        """
        item = await self._get_item(id)
        await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                     item.organization_id)
        await super().get(id, **kwargs)

    async def delete(self, id, **kwargs):
        """
        ---
        description: |
            Delete cluster type and based on it clusters
            Required permission: MANAGE_RESOURCES
        tags: [cluster_types]
        summary: Delete cluster type
        parameters:
        -   name: id
            in: path
            description: Cluster type id
            required: true
            type: string
        responses:
            204:
                description: Success
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
                    - OE0002: Cluster type not found
        security:
        - token: []
        """
        item = await self._get_item(id)
        await self.check_permissions('MANAGE_RESOURCES', 'organization',
                                     item.organization_id)
        await super().delete(id, **kwargs)

    def patch(self, id, **kwargs):
        self.raise405()


class ClusterTypePriorityAsyncHandler(ClusterTypeAsyncItemHandler):
    def get(self, id, **kwargs):
        self.raise405()

    def delete(self, id, **kwargs):
        self.raise405()

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing cluster type
            Required permission: MANAGE_RESOURCES
        tags: [cluster_types]
        summary: Edit cluster type
        parameters:
        -   name: id
            in: path
            description: Cluster type id
            required: true
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
                        description: "change cluster type priority"
                        required: True
                        enum: [prioritize, promote, demote, deprioritize]
                        example: promote
        responses:
            200:
                description: Modified cluster type object
                schema:
                    type: object
                    example:
                        id: 99843c5d-462e-4f1b-8774-661cd108c8a7
                        deleted_at: 0
                        created_at: 1617611286
                        organization_id: 5be74ae0-fe96-40b0-b65d-d76d974f6913
                        name: my_cluster_type
                        tag_key: key_example
                        priority: 2
            400:
                description: |
                    Wrong arguments:
                    - OE0166: Action is not supported
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
                    - OE0236: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Cluster type not found
        security:
        - token: []
        """
        item = await self._get_item(id)
        data = self._request_body()
        action = data.get('action')
        self._validate_action(action)
        await self.check_permissions('MANAGE_RESOURCES', 'organization',
                                     item.organization_id)
        res = await run_task(self.controller.edit, id, action=action)
        self.write(json.dumps(res, cls=ModelEncoder))


class ClusterTypeApplyAsyncHandler(BaseAsyncItemHandler, BaseAuthHandler,
                                   BaseHandler):
    def _get_controller_class(self):
        return ClusterTypeApplyAsyncController

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Re-apply cluster types to resources
            Required permission: MANAGE_RESOURCES
        tags: [cluster_types]
        summary: Re-apply cluster types
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        responses:
            200:
                description:
                schema:
                    type: object
                    properties:
                        processed_resources: {type: integer, description:
                            "Processed resources count"}
                        processed_cluster_types:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string, description:
                                        "Cluster type id"}
                                    name: {type: string, description:
                                        "Cluster type name"}
                                    clustered_resources_count: {type: integer,
                                        description: "Clustered resources count"}
                                    clusters_count: {type: integer, description:
                                        "Clusters count"}
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0233: Incorrect body received
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
                    - OE0378: Current user is not a member in organization
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        if data:
            raise OptHTTPError(400, Err.OE0212, [', '.join(data)])
        await self.check_permissions('MANAGE_RESOURCES', 'organization',
                                     organization_id)
        user_id = await self.check_self_auth()
        user_info = await self.get_user_info(user_id)
        res = await run_task(self.controller.reapply_clusters,
                             organization_id, user_info)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))
