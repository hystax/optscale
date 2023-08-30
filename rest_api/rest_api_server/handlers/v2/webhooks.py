import json
from bson import ObjectId
from sqlalchemy import Enum
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.utils import run_task, ModelEncoder
from rest_api.rest_api_server.controllers.webhook import (
    WebhookAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.models.types import WebhookObjectTypes, WebhookActionTypes
from rest_api.rest_api_server.utils import object_to_xlsx

OBJECT_PERMISSIONS_MAP = {
    WebhookObjectTypes.ENVIRONMENT.value: 'MANAGE_RESOURCES'
}


class MongoEncoder(ModelEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


class WebhookAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                    BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return WebhookAsyncController

    def _validate_params(self, **kwargs):
        required = ['object_type', 'object_id', 'action', 'url']
        optional = ['headers', 'active']
        not_provided = list(filter(lambda x: x not in kwargs.keys(), required))
        if not_provided:
            raise OptHTTPError(400, Err.OE0216, [not_provided[0]])
        allowed_params = required + optional
        unexpected = list(filter(
            lambda x: x not in allowed_params, kwargs.keys()))
        if unexpected:
            raise OptHTTPError(400, Err.OE0212, [', '.join(unexpected)])
        object_type = kwargs.get('object_type')
        action = kwargs.get('action')
        for value, enum_type in [(object_type, WebhookObjectTypes),
                                 (action, WebhookActionTypes)]:
            self._get_enum_value(value, enum_type)

    @staticmethod
    def _get_enum_value(value, enum_type):
        try:
            result = Enum(enum_type).enum_class(value)
        except ValueError as ex:
            raise OptHTTPError(400, Err.OE0287, [str(ex)])
        return result

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of webhooks for objects.
            Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
        tags: [webhooks]
        summary: "List of webhooks with filters"
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   name: object_type
            in: query
            description: object type
            required: false
            type: string
            enum: [environment]
        -   name: object_id
            in: query
            description: object id
            required: false
            type: string
        -   name: active
            in: query
            description: active flag
            required: false
            type: boolean
        -   name: action
            in: query
            description: hook action
            required: false
            type: string
            enum: [booking_acquire, booking_release]
        responses:
            200:
                description: webhook list
                schema:
                    type: object
                    properties:
                        webhooks:
                            type: array
                            items:
                                type: object
                            example:
                                - id: e1a3bb04-d513-42d2-b9b7-019d24097dec
                                  created_at: 1632829593
                                  deleted_at: 0
                                  organization_id: aea929ab-3103-4932-a77c-ca0a758a992b
                                  object_type: environment
                                  object_id: 99843c5d-462e-4f1b-8774-661cd108c8a7
                                  url: https://example.com/hook_api
                                  action: booking_acquire
                                  headers: "{'token': 'some_token'}"
                                - id: 21285b43-c154-4d0a-b2cc-43ce26f1fb16
                                  created_at: 1632829433
                                  deleted_at: 0
                                  organization_id: aea929ab-3103-4932-a77c-ca0a758a992b
                                  object_type: environment
                                  object_id: 99843c5d-462e-4f1b-8774-661cd108c8a7
                                  url: https://example.com/another_hook_api
                                  action: booking_release
                                  headers: "{'token': 'some_token'}"
            400:
                description: |
                    Wrong arguments:
                    - OE0287: Invalid action or object_type
            401:
                description: |
                    Unauthorized:
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
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        params = dict(organization_id=organization_id)
        object_type = self.get_arg('object_type', str, None)
        if object_type:
            params['object_type'] = self._get_enum_value(
                object_type, WebhookObjectTypes)
        action = self.get_arg('action', str, None)
        if action:
            params['action'] = self._get_enum_value(action, WebhookActionTypes)
        active = self.get_arg('active', bool, None)
        if active is not None:
            params['active'] = active
        object_id = self.get_arg('object_id', str, None)
        if object_id:
            params['object_id'] = object_id
        res = await run_task(self.controller.list, **params)
        webhooks = {'webhooks': [
            webhook.to_dict() for webhook in res
        ]}
        self.write(json.dumps(webhooks, cls=ModelEncoder))

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create webhook
            Required permission: MANAGE_RESOURCES
        tags: [webhooks]
        summary: Create webhook
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: body
            description: Webhook info
            required: true
            schema:
                type: object
                properties:
                    object_type:
                        type: string
                        enum: [environment]
                        description: Object type
                        required: True
                        example: environment
                    object_id:
                        type: string
                        description: Object id
                        required: True
                        example: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                    action:
                        type: string
                        enum: [booking_acquire, booking_release]
                        description: Webhook action
                        required: True
                        example: booking_acquire
                    url:
                        type: string
                        description: "Webhook url"
                        required: True
                        example: https://example.com/hook_api
                    active:
                        type: boolean
                        description: Webhook active flag
                        required: False
                        example: False
                        default: True
                    headers:
                        type: string
                        description: Json encoded string with headers
                        required: True
                        example: "{'token': 'some_token'}"
        responses:
            201:
                description: Created (returns created attachment object)
                schema:
                    type: object
                    example:
                        id: e1a3bb04-d513-42d2-b9b7-019d24097dec
                        created_at: 1632829593
                        deleted_at: 0
                        organization_id: aea929ab-3103-4932-a77c-ca0a758a992b
                        object_type: environment
                        object_id: 99843c5d-462e-4f1b-8774-661cd108c8a7
                        url: https://example.com/hook_api
                        action: booking_acquire
                        headers: "{'token': 'some_token'}"
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0219: Argument should be json encoded string
                    - OE0226: Argument should be boolean
                    - OE0233: Incorrect body received
                    - OE0287: Invalid action or object_type
                    - OE0456: Duplicate path parameters in the request body
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Entity not found
            409:
                description: |
                    Conflict:
                    - OE0503: Webhook already exists
        security:
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        permission = OBJECT_PERMISSIONS_MAP[data.get('object_type')]
        await self.check_permissions(
            permission, 'organization', organization_id)
        res = await run_task(self.controller.create,
                             organization_id=organization_id, **data)
        self.set_status(201)
        self.write(res.to_json())


class WebhookAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return WebhookAsyncController

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Update existing webhook
            Required permission: MANAGE_RESOURCES
        tags: [webhooks]
        summary: Update webhook
        parameters:
        -   name: id
            in: path
            description: Webhook id
            required: true
            type: string
        -   in: body
            name: body
            description: updated parameters
            required: false
            schema:
                type: object
                properties:
                    active:
                        type: boolean
                        required: False
                        description: Active flag
                    url:
                        type: string
                        required: False
                        description: Webhook url
                    headers:
                        type: string
                        required: False
                        description: Json encoded string with headers
        responses:
            200:
                description: Success (returns modified value)
                schema:
                    type: object
                    example:
                        id: e1a3bb04-d513-42d2-b9b7-019d24097dec
                        created_at: 1632829593
                        deleted_at: 0
                        organization_id: aea929ab-3103-4932-a77c-ca0a758a992b
                        object_type: environment
                        object_id: 99843c5d-462e-4f1b-8774-661cd108c8a7
                        url: https://example.com/hook_api
                        action: booking_acquire
                        headers: "{'token': 'some_token'}"
            400:
                description: |
                    Wrong arguments:
                    - OE0211: Immutable parameters
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0219: Argument should be json encoded string
                    - OE0226: Argument should be boolean
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Webhook not found
        security:
        - token: []
        """
        item = await self._get_item(id)
        object_type = item.object_type.value
        object_type = OBJECT_PERMISSIONS_MAP[object_type]
        await self.check_permissions(object_type, 'webhook', id)
        data = self._request_body()
        await super().patch(id, **data)

    async def delete(self, id, **kwargs):
        """
        ---
        description: >
            Delete webhook
            Required permission: MANAGE_RESOURCES
        tags: [webhooks]
        summary: Delete webhook
        parameters:
        -   name: id
            in: path
            description: Webhook ID
            required: true
            type: string
        responses:
            204:
                description: Success
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Webhook not found
        security:
        - token: []
        """
        item = await self._get_item(id)
        object_type = item.object_type.value
        object_type = OBJECT_PERMISSIONS_MAP[object_type]
        await self.check_permissions(object_type, 'webhook', id)
        await super().delete(id)

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get webhook info by ID
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [webhooks]
        summary: Get webhook
        parameters:
        -   name: id
            in: path
            description: Webhook ID
            required: true
            type: string
        responses:
            200:
                description: Webhook info
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Unique webhook id
                        deleted_at:
                            type: integer
                            description: Deleted timestamp (service field)
                        created_at:
                            type: integer
                            description: Created timestamp (service field)
                        organization_id:
                            type: string
                            description: Organization id
                        object_type:
                            type: string
                            description: Webhook object type
                            enum: [environment]
                        object_id:
                            type: string
                            description: Webhook object id
                        active:
                            type: boolean
                            description: Webhook active flag
                        action:
                            type: string
                            description: Webhook action
                            enum: [booking_acquire, booking_release]
                        url:
                            type: string
                            description: Webhook url
                        headers:
                            type: string
                            description: Json encoded string with headers
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Webhook not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('INFO_ORGANIZATION', 'webhook', id)
        await super().get(id, **kwargs)


class WebhookLogsAsyncCollectionHandler(WebhookAsyncCollectionHandler):
    async def get(self, webhook_id, **kwargs):
        """
        ---
        description: |
            Get webhook logs by id
            Required permission: INFO_ORGANIZATION
        tags: [webhooks]
        summary: Get webhook logs
        parameters:
        -   name: id
            in: path
            description: Webhook ID
            required: true
            type: string
        -   name: format
            in: query
            description: response format
            required: false
            type: string
        responses:
            200:
                description: list of webhook logs
                schema:
                    type: object
                    properties:
                        logs:
                            type: array
                            items:
                                type: object
                            example:
                                -   id: e1a3bb04-d513-42d2-b9b7-019d24097dec
                                    organization_id: aea929ab-3103-4932-a77c-ca0a758a992b
                                    webhook_id: 033f55e7-6a8e-464b-891e-e845128b161c
                                    url: https://example.com/hook_api
                                    headers: "{'token': 'some_token'}"
                                    success: True
                                    execution_time: 1634199946
                                    execution_result: ok
                                    body:
                                        webhook_id: 033f55e7-6a8e-464b-891e-e845128b161c
                                        action: booking_acquire
                                        object_type: shared_resource
                                        object_id: 0e4cf423-5a5d-4f24-ac9f-b8a1b8e1927c
                                        description:
                                -   id: 08c34417-c0a9-4569-a419-ee461fee275c
                                    organization_id: aea929ab-3103-4932-a77c-ca0a758a992b
                                    webhook_id: 0a8e8970-700c-4b31-bdb5-e60d6a8f920d
                                    url: https://example.com/hook_api
                                    headers: "{'token': 'some_token'}"
                                    success: False
                                    execution_time: 1634199946
                                    execution_result: Error description
                                    body:
                                        webhook_id: 0a8e8970-700c-4b31-bdb5-e60d6a8f920d
                                        action: booking_acquire
                                        object_type: shared_resource
                                        object_id: 0acab653-e6b2-4e84-b08b-b3ab9f704aee
                                        description:
            400:
                description: |
                    Wrong arguments:
                    - OE0473: Format is not allowed
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Employee not found
        security:
        - token: []
        """
        _format = self.get_arg('format', str, 'json')
        await self.check_permissions(
            'INFO_ORGANIZATION', 'webhook', webhook_id)
        res = await run_task(self.controller.get_logs, webhook_id)
        filename, logs = res
        if _format == 'json':
            self.set_content_type('application/json; charset="utf-8"')
            self.set_header('Content-Disposition',
                            'attachment; filename="%s.%s"' % (
                                filename, _format))
            self.write(json.dumps({'logs': logs}, cls=MongoEncoder,
                                  indent=4, sort_keys=True))
        elif _format == 'xlsx':
            self.set_content_type('application/vnd.openxmlformats-'
                                  'officedocument.spreadsheetml.sheet')
            self.set_header('Content-Disposition',
                            'attachment; filename="%s.%s"' % (
                                filename, _format))
            res_str = json.dumps(logs, cls=MongoEncoder)
            self.write(object_to_xlsx(json.loads(res_str)))
        else:
            raise OptHTTPError(400, Err.OE0473, [_format])

    def post(self, **url_params):
        self.raise405()
