import json
from rest_api_server.exceptions import Err
from rest_api_server.utils import run_task, ModelEncoder
from rest_api_server.controllers.ssh_key import (
    SshKeyAsyncController)
from rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from optscale_exceptions.http_exc import OptHTTPError


class SshKeysBaseHandler(BaseAuthHandler):
    def _get_controller_class(self):
        return SshKeyAsyncController

    async def check_ssh_key_permissions(self, employee_id):
        await self.check_permissions(
            'INFO_ORGANIZATION', 'employee', employee_id)
        user_id = await self.check_self_auth()
        employee = await run_task(
            self.controller.get_employee, employee_id)
        if employee.auth_user_id != user_id:
            raise OptHTTPError(403, Err.OE0234, [])


class SshKeysAsyncCollectionHandler(SshKeysBaseHandler,
                                    BaseAsyncCollectionHandler):

    def _validate_params(self, **kwargs):
        required = ['name', 'key']
        optional = ['default']
        not_provided = list(filter(lambda x: x not in kwargs.keys(), required))
        if not_provided:
            raise OptHTTPError(400, Err.OE0216, [not_provided[0]])
        allowed_params = required + optional
        unexpected = list(filter(
            lambda x: x not in allowed_params, kwargs.keys()))
        if unexpected:
            raise OptHTTPError(400, Err.OE0212, [', '.join(unexpected)])

    async def get(self, employee_id):
        """
        ---
        description: |
            Get list of ssh_keys for objects.
            Required permission: INFO_ORGANIZATION
        tags: [ssh_keys]
        summary: "List of employee's ssh_keys"
        parameters:
        -   in: path
            name: employee_id
            description: employee id
            required: true
        responses:
            200:
                description: ssh_keys list
                schema:
                    type: object
                    properties:
                        ssh_keys:
                            type: array
                            items:
                                type: object
                            example:
                                - id: 8a82d3e0-808f-4a62-86b7-a6ab1b202571
                                  created_at: 1635394564
                                  deleted_at: 0
                                  employee_id: 4b6ebab7-f54f-447f-9e90-c0cfa1dfe65b
                                  name: my ssh_key
                                  default: True
                                  fingerprint: "22:c5:a0:8a:16:04:19:00:c8:dc:b9:89:4c:36:e7:2e"
                                  key: ssh-rsa AAAAC3Nz ubuntu
                                - id: d8687291-1b04-4c88-8516-6d45d6308f00
                                  created_at: 1635394564
                                  deleted_at: 0
                                  employee_id: 4b6ebab7-f54f-447f-9e90-c0cfa1dfe65b
                                  name: my another ssh_key
                                  default: False
                                  fingerprint: "4d:44:17:ae:f3:f5:ef:ef:c9:c0:8b:20:94:9d:cd:12"
                                  key: ssh-rsa AAAAC3Nk ubuntu
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
        await self.check_ssh_key_permissions(employee_id)
        params = dict(employee_id=employee_id)
        res = await run_task(self.controller.list, **params)
        ssh_keys = {'ssh_keys': [
            ssh_key.to_dict() for ssh_key in res
        ]}
        self.write(json.dumps(ssh_keys, cls=ModelEncoder))

    async def post(self, employee_id, **url_params):
        """
        ---
        description: |
            Create ssh_key
            Required permission: INFO_ORGANIZATION
        tags: [ssh_keys]
        summary: Create ssh_key
        parameters:
        -   in: path
            name: employee_id
            description: employee id
            required: true
        -   in: body
            name: body
            description: ssh_key info
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: ssh_key name
                        required: True
                        example: my ssh name
                    key:
                        type: string
                        description: ssh public key
                        required: True
                        example: ssh-rsa AAAAC3Nk ubuntu
                    default:
                        type: boolean
                        description: ssh_key is default for employee
                        required: False
                        default: False
        responses:
            201:
                description: Created (returns created attachment object)
                schema:
                    type: object
                    example:
                        id: 8a82d3e0-808f-4a62-86b7-a6ab1b202571
                        created_at: 1635394564
                        deleted_at: 0
                        employee_id: 4b6ebab7-f54f-447f-9e90-c0cfa1dfe65b
                        name: my ssh key
                        default: True
                        fingerprint: "22:c5:a0:8a:16:04:19:00:c8:dc:b9:89:4c:36:e7:2e"
                        key: ssh-rsa AAAAC3Nz ubuntu
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0226: Argument should be boolean
                    - OE0233: Incorrect body received
                    - OE0456: Duplicate path parameters in the request body
                    - OE0507: Invalid public SSH key
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
                    - OE0002: Employee not found
            409:
                description: |
                    Conflict:
                    - OE0506: ssh_key with such fingerprint already exist
        security:
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        await self.check_ssh_key_permissions(employee_id)
        res = await run_task(self.controller.create,
                             employee_id=employee_id, **data)
        self.set_status(201)
        self.write(res.to_json())


class SshKeysAsyncItemHandler(BaseAsyncItemHandler, SshKeysBaseHandler):

    async def delete(self, id, **kwargs):
        """
        ---
        description: >
            Delete ssh_key
            Required permission: INFO_ORGANIZATION
        tags: [ssh_keys]
        summary: Delete ssh_key
        parameters:
        -   name: id
            in: path
            description: ssh_key ID
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
                    - OE0002: ssh_key not found
            424:
                description: |
                    Failed dependency:
                    - OE0509: Deleting a non-last default ssh_key is prohibited
        security:
        - token: []
        """
        item = await self._get_item(id)
        await self.check_ssh_key_permissions(item.employee_id)
        await super().delete(id)

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get ssh_key info by ID
            Required permission: INFO_ORGANIZATION
        tags: [ssh_keys]
        summary: Get ssh_key
        parameters:
        -   name: id
            in: path
            description: ssh_key ID
            required: true
            type: string
        responses:
            200:
                description: Ssh_key info
                schema:
                    type: object
                    example:
                        id: 8a82d3e0-808f-4a62-86b7-a6ab1b202571
                        created_at: 1635394564
                        deleted_at: 0
                        employee_id: 4b6ebab7-f54f-447f-9e90-c0cfa1dfe65b
                        name: my ssh key
                        default: True
                        fingerprint: "22:c5:a0:8a:16:04:19:00:c8:dc:b9:89:4c:36:e7:2e"
                        key: ssh-rsa AAAAC3Nz ubuntu
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
                    - OE0002: ssh_key not found
        security:
        - token: []
        """
        item = await self._get_item(id)
        await self.check_ssh_key_permissions(item.employee_id)
        await super().get(id, **kwargs)

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Update existing ssh_key
            Required permission: INFO_ORGANIZATION
        tags: [ssh_keys]
        summary: Update ssh_key
        parameters:
        -   name: id
            in: path
            description: ssh_key id
            required: true
            type: string
        -   in: body
            name: body
            description: updated parameters
            required: false
            schema:
                type: object
                properties:
                    name:
                        type: string
                        required: False
                        description: ssh_key name
                    default:
                        type: boolean
                        required: False
                        description: ssh_key is default for employee
        responses:
            200:
                description: Success (returns modified value)
                schema:
                    type: object
                    example:
                        id: 8a82d3e0-808f-4a62-86b7-a6ab1b202571
                        created_at: 1635394564
                        deleted_at: 0
                        employee_id: 4b6ebab7-f54f-447f-9e90-c0cfa1dfe65b
                        name: my ssh key
                        default: True
                        fingerprint: "22:c5:a0:8a:16:04:19:00:c8:dc:b9:89:4c:36:e7:2e"
                        key: ssh-rsa AAAAC3Nz ubuntu
            400:
                description: |
                    Wrong arguments:
                    - OE0211: Immutable parameters
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0226: Argument should be boolean
                    - OE0508: Manually disabling default ssh_key is prohibited
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
                    - OE0002: ssh_key not found
        security:
        - token: []
        """
        item = await self._get_item(id)
        await self.check_ssh_key_permissions(item.employee_id)
        data = self._request_body()
        if data.get('default') is False:
            raise OptHTTPError(400, Err.OE0508, [])
        await super().patch(id, **data)
