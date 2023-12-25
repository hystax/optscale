import json

from rest_api.rest_api_server.controllers.layout import LayoutsAsyncController
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncItemHandler, BaseAsyncCollectionHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import (run_task, ModelEncoder)


class LayoutsAsyncCollectionHandler(
        BaseAsyncCollectionHandler, BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return LayoutsAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
            Gets a list of layouts for employee
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [layout]
        summary: List of layouts
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: layout_type
            in: query
            description: Layout type
            required: false
            type: string
        -   name: include_shared
            in: query
            description: Show shared layouts
            required: false
            type: boolean
        -   name: entity_id
            in: query
            description: Entity id to filter by
            required: false
            type: string
        responses:
            200:
                description: Layouts list
                schema:
                    type: object
                    properties:
                        layouts:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description: "Unique layout id"}
                                    name: {type: string,
                                        description: "Name of layout"}
                                    type: {type: string,
                                        description: "Type of layout"}
                                    shared: {type: boolean,
                                        description: "Is layout visible for
                                        other employees"}
                                    entity_id: {type: string,
                                        description: "Related entity id"}
                                    owner_id: {type: string,
                                        description: "Owner employee id"}
                        current_employee_id:
                            type: string
                            description: current employee id
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
            - secret: []
            - token: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
            user_id = await self.check_self_auth()
        else:
            user_id = None
        layout_type = self.get_arg('layout_type', str, None)
        include_shared = self.get_arg('include_shared', bool, False)
        entity_id = self.get_arg('entity_id', str, None)
        res = await run_task(self.controller.list, user_id, organization_id,
                             layout_type, include_shared, entity_id)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def post(self, organization_id, **_url_params):
        """
        ---
        description: |
            Create new layout for employee
            Required permission: INFO_ORGANIZATION
        summary: Create layout
        tags: [layout]
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Layout to add
            required: true
            schema:
                type: object
                properties:
                    type:
                        type: string
                        description: Type of layout
                        required: true
                        example: ml_run_charts_dashboard
                    name:
                        type: string
                        description: Layout name
                        required: true
                        example: "My dashboard"
                    shared:
                        type: boolean
                        description: Is this layout visible for other employees
                        required: true
                    data:
                        type: string
                        description: JSON string with layout data
                        required: false
                        default: "{}"
                    entity_id:
                        type: string
                        description: Id of an entity related to layout
                        required: false
                        example: 91d92bb0-a75e-4440-98b0-a74a0da94d0b
        responses:
            201:
                description: Success (returns created object)
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique layout id"}
                        name: {type: string,
                            description: "Name of layout"}
                        type: {type: string,
                            description: "Type of layout"}
                        shared: {type: boolean,
                            description: "Is layout visible for other employees"}
                        data: {type: string,
                            description: "JSON string with layout data"}
                        entity_id: {type: string,
                            description: "Related entity id"}
                        owner_id: {type: string,
                            description: "Owner employee id"}
            400:
                description: |
                    Wrong arguments:
                        - OE0212: Unexpected parameters
                        - OE0214: Argument should be a string
                        - OE0216: Argument is not provided
                        - OE0219: data should be a string with valid JSON
                        - OE0226: shared should be True or False
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
        user_id = await self.check_self_auth()
        data = self._request_body()
        self._validate_params(**data)
        res = await run_task(self.controller.create,
                             user_id, organization_id, **data)
        self.set_status(201)
        self.write(json.dumps(res.to_dict()))


class LayoutsAsyncItemHandler(
        BaseAsyncItemHandler, BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return LayoutsAsyncController

    async def get(self, organization_id, layout_id):
        """
        ---
        description: |
            Gets Layout by id.
            Required permission: INFO_ORGANIZATION
        tags: [layout]
        summary: Gets layout by id
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: layout_id
            in: path
            description: Layout id
            required: true
            type: string
        responses:
            200:
                description: Layout
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique layout id"}
                        name: {type: string,
                            description: "Name of layout"}
                        type: {type: string,
                            description: "Type of layout"}
                        shared: {type: boolean,
                            description: "Is layout visible for other employees"}
                        data: {type: string,
                            description: "JSON string with layout data"}
                        entity_id: {type: string,
                            description: "Related entity id"}
                        owner_id: {type: string,
                            description: "Owner employee id"}
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
                    - OE0002: Object not found
        security:
        - token: []
        """
        await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        user_id = await self.check_self_auth()
        res = await run_task(
            self.controller.get_item, user_id, organization_id, layout_id)
        self.write(json.dumps(res.to_dict()))

    async def patch(self, organization_id, layout_id):
        """
        ---
        description: |
            Update layout for employee
            Required permission: INFO_ORGANIZATION
        summary: Update layout
        tags: [layout]
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: layout_id
            in: path
            description: Layout id
            required: true
            type: string
        -   in: body
            name: body
            description: Layout to add
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: Layout name
                        required: false
                        example: "My dashboard"
                    shared:
                        type: boolean
                        description: Is this layout visible for other employees
                        required: true
                    data:
                        type: string
                        description: JSON string with layout data
                        required: false
                        default: "{}"
                    owner_id:
                        type: string
                        description: Owner employee id
                        required: false
        responses:
            200:
                description: Updated layout
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique layout id"}
                        name: {type: string,
                            description: "Name of layout"}
                        type: {type: string,
                            description: "Type of layout"}
                        shared: {type: boolean,
                            description: "Is layout visible for other employees"}
                        data: {type: string,
                            description: "JSON string with layout data"}
                        entity_id: {type: string,
                            description: "Related entity id"}
                        owner_id: {type: string,
                            description: "Owner employee id"}
            400:
                description: |
                    Wrong arguments:
                        - OE0211: Parameter is immutable
                        - OE0212: Unexpected parameters
                        - OE0214: Argument should be a string
                        - OE0216: Argument is not provided
                        - OE0219: data should be a string with valid JSON
                        - OE0226: shared should be True or False
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
                    - OE0002: Object not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        user_id = await self.check_self_auth()
        data = self._request_body()
        res = await run_task(self.controller.edit,
                             user_id, organization_id, layout_id, **data)
        self.write(json.dumps(res.to_dict()))

    async def delete(self, organization_id, layout_id):
        """
        ---
        description: |
            Deletes layout
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [layout]
        summary: Delete layout
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: layout_id
            in: path
            description: Layout id
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
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
            403:
                description: |
                    Forbidden:
                        - OE0234: Forbidden
                        - OE0236: Bad secret
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
            user_id = await self.check_self_auth()
        else:
            user_id = None
        await run_task(
            self.controller.delete, user_id, organization_id, layout_id)
        self.set_status(204)
