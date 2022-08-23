import json

from rest_api_server.controllers.employee import EmployeeAsyncController
from rest_api_server.exceptions import Err
from rest_api_server.handlers.v1.base_async import (BaseAsyncCollectionHandler,
                                                    BaseAsyncItemHandler)
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task, ModelEncoder, object_to_xlsx

from optscale_exceptions.common_exc import UnauthorizedException
from optscale_exceptions.http_exc import OptHTTPError
from optscale_exceptions.common_exc import WrongArgumentsException
from rest_api_server.utils import check_string_attribute


class EmployeeAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                     BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return EmployeeAsyncController

    async def post(self, **url_params):
        """
        ---
        description: |
            Create employee for organization
            Required permission: CLUSTER_SECRET
        tags: [employees]
        summary: Create employee for an organization
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Employee to add
            required: true
            schema:
                type: object
                properties:
                    name: {type: string, description: "Employee name"}
                    auth_user_id: {type: string, description:
                        "Auth user id for employee"}
        responses:
            201: {description: Success (returns created object)}
            400:
                description: |
                    Wrong arguments:
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters
                    - OE0216: Argument is not provided
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
                    - OE0002: Organization not found
            409:
                description: |
                    Conflict:
                    - OE0149: Employee for this user already exists
        security:
        - secret: []
        """
        self.check_cluster_secret()
        await super().post(**url_params)

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of employees of organization
            Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
        tags: [employees]
        summary: List of employees
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: current_only
            in: query
            description: include only employee for current user only
            required: false
            type: boolean
            default: false
        -   name: exclude_myself
            in: query
            description: exclude current user from response
            required: false
            type: boolean
            default: false
        -   name: roles
            in: query
            description: include info about employee roles
            required: false
            type: boolean
            default: false
        -   name: format
            in: query
            description: Output format
            required: false
            type: string
            default: advanced_json
            enum: [advanced_json, json, xlsx]
        -   name: field
            in: query
            description: Requested employee fields
            requiered: false
            collectionFormat: multi
            type: array
            items:
                type: string
            default: all fields
            enum:
                - id, name, user_email, deleted_at, created_at
                - organization_id, auth_user_id, user_display_name
                - slack_connected, assignments
        responses:
            200:
                description: Employees list
                schema:
                    type: object
                    properties:
                        employees:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string, description:
                                        "Unique employee id"}
                                    name: {type: string, description:
                                        "Employee name"}
                                    user_email: {type: string, description:
                                        "Auth user email for employee"}
                                    deleted_at: {type: integer, description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer, description:
                                        "Created timestamp (service field)"}
                                    organization_id: {type: string, description:
                                        "Employee's organization"}
                                    auth_user_id: {type: string, description:
                                        "Auth user id for employee"}
                                    user_display_name: {type: string, description:
                                        "Auth user display name for employee"}
                                    slack_connected: {type: boolean, description:
                                        "Employee is connected to Slack or not"}
                                    default_ssh_key_id: {type: string, description:
                                        "Employee's default ssh key id"}
                                    jira_connected: {type: boolean, description:
                                        "Employee is connected to Jira or not"}
                                    assignments:
                                        type: array
                                        items:
                                            type: object
                                            properties:
                                                assignment_resource_type: {type: string, description:
                                                    "Assignment resource type for employee auth user"}
                                                assignment_resource_name: {type: string, description:
                                                    "Assignment resource name for employee auth user"}
                                                assignment_resource_purpose: {type: string, description:
                                                    "Pool purpose for resource assignment"}
                                                assignment_id: {type: string, description:
                                                    "Assignment id for employee auth user"}
                                                role_name: {type: string, description:
                                                    "Auth user name"}
                                                assignment_resource_id: {type: string, description:
                                                    "Assignment resource id for employee auth user"}
                                                purpose: {type: string, description:
                                                    "Auth user purpose"}
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0427: "current_only" and "exclude_myself" could not be true in the same time
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

        roles = self.get_arg('roles', bool, False)
        exclude_myself = self.get_arg('exclude_myself', bool, False)
        current_only = self.get_arg('current_only', bool, False)
        fields = self.get_arg(
            'field', str, [], repeated=True)
        if current_only and exclude_myself:
            raise OptHTTPError(400, Err.OE0427, [])
        list_kwargs = {'roles': roles, 'exclude_myself': exclude_myself,
                       'current_only': current_only, 'fields': fields}
        if current_only or exclude_myself:
            user_id = await self.check_self_auth()
            list_kwargs.update({'auth_user_id': user_id})
        res = await run_task(self.controller.list, organization_id,
                             **list_kwargs)
        exp_format = self.get_arg('format', str, default='advanced_json')
        filename = 'organization %s employees' % organization_id
        if exp_format == 'json':
            self.set_content_type('application/json; charset="utf-8"')
            self.set_header('Content-Disposition',
                            'attachment; filename="%s.%s"' % (
                                filename, exp_format))
            self.write(json.dumps({'employees': res}, cls=ModelEncoder,
                                  indent=4, sort_keys=True))
        elif exp_format == 'xlsx':
            self.set_content_type('application/vnd.openxmlformats-'
                                  'officedocument.spreadsheetml.sheet')
            self.set_header('Content-Disposition',
                            'attachment; filename="%s.%s"' % (
                                filename, exp_format))
            self.write(object_to_xlsx(res))
        elif exp_format == 'advanced_json':
            self.write(json.dumps({'employees': res}, cls=ModelEncoder))
        else:
            raise OptHTTPError(400, Err.OE0473, [exp_format])


class EmployeeAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                               BaseHandler):
    def _get_controller_class(self):
        return EmployeeAsyncController

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get employee info by ID
            Required permission: INFO_ORGANIZATION OR CLUSTER_SECRET
        tags: [employees]
        summary: Get employee
        parameters:
        -   name: id
            in: path
            description: Employee ID
            required: true
            type: string
        -   name: roles
            in: query
            description: Include roles
            required: false
            type: boolean
        responses:
            200:
                description: Employee data
                schema:
                    type: object
                    properties:
                        id: {type: string, description: "Unique employee id"}
                        name: {type: string, description: "Employee name"}
                        deleted_at: {type: integer, description:
                            "Deleted timestamp (service field)"}
                        created_at: {type: integer, description:
                            "Created timestamp (service field)"}
                        organization_id: {type: string, description:
                            "Employee's organization"}
                        auth_user_id: {type: string, description:
                            "Auth user id for employee"}
                        default_ssh_key_id: {type: string, description:
                            "Employee's default ssh key id"}
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
                    - OE0002: Employee not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('INFO_ORGANIZATION', 'employee', id)
        await super().get(id, **kwargs)

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing employee
            Required permission: CLUSTER_SECRET
        tags: [employees]
        summary: Edit employee
        parameters:
        -   name: id
            in: path
            description: Employee ID
            required: true
            type: string
        -   in: body
            name: body
            description: Employee changes
            required: false
            schema:
                type: object
                properties:
                    name: {type: string, description: "Employee name"}
                    organization_id: {type: string, description:
                        "Employee's organization"}
        responses:
            200: {description: Success (returns modified object)}
            400:
                description: |
                    Wrong arguments:
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
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
            409:
                description: |
                    Conflict:
                    - OE0149: Employee with name already exists
        security:
        - secret: []
        """
        self.check_cluster_secret()
        await super().patch(id, **kwargs)

    async def delete(self, id, **kwargs):
        """
        ---
        description: |
            Deletes employee specified id and related assignments
            Required permission: CLUSTER_SECRET or EDIT_PARTNER
        tags: [employees]
        summary: Delete employee
        parameters:
        -   name: id
            in: path
            description: Employee ID
            required: true
            type: string
        -   name: new_owner_id
            in: query
            description: |
                Organization manager employee id, which becomes a new owner
                for deleted employee's resources. If not provided, current user
                or one of organization managers is used
            required: false
            type: string
        responses:
            204:
                description: Success
            400:
                description: |
                    Wrong arguments:
                        - OE0217: Invalid new_owner_id
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
                    - OE0497: Deleting of the last organization manager is not allowed
            404:
                description: |
                    Not found:
                    - OE0002: Employee not found
        security:
        - token: []
        - secret: []
        """
        data = {}
        new_owner_id = self.get_arg('new_owner_id', str)
        if new_owner_id:
            data['new_owner_id'] = new_owner_id
        if not self.check_cluster_secret(raises=False):
            user_id = await self.check_self_auth()
            await self.check_permissions('EDIT_PARTNER', 'employee', id)
            data['user_id'] = user_id
        try:
            await super().delete(id, **data)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)


class AuthorizedEmployeeAsyncCollectionHandler(EmployeeAsyncCollectionHandler):

    async def post(self, **url_params):
        self.raise405()

    def _get_input_params(self):
        object_type = self.get_arg('object_type', str)
        object_id = self.get_arg('object_id', str)
        permissions = self.get_arg('permission', str, [], repeated=True)
        check_string_attribute('object_type', object_type)
        check_string_attribute('object_id', object_id)
        if not permissions:
            raise WrongArgumentsException(Err.OE0216, ['permission'])
        for p in permissions:
            check_string_attribute('permission', p)
        return {
            'object_type': object_type,
            'object_id': object_id,
            'permissions': permissions
        }

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of authorized employees for action
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [employees]
        summary: List of authorized employees
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: object_type
            in: query
            description: Authorized object type
            required: true
            type: string
        -   name: object_id
            in: query
            description: Authorized object id
            required: true
            type: string
        -   name: permission
            type: array
            in: query
            items:
                type: string
            collectionFormat: multi
            description: Authorized permission
            required: true
        responses:
            200:
                description: Employees list
                schema:
                    type: object
                    properties:
                        employees:
                            type: array
                            items:
                                type: object
                            example:
                                -   deleted_at: 0
                                    id: fd7d72a1-6945-4d74-a7d4-ae6bede8ceb7
                                    created_at: 1634617431
                                    name: John Smith
                                    organization_id: 4e252eb5-db8c-4fc5-9142-48307187d12f
                                    auth_user_id: 14eec9e2-9074-4e98-8d85-093b1da5199e
                                -   deleted_at: 0
                                    id: 2918d286-66c7-4a09-bda5-5220a54fd649
                                    created_at: 1634617431
                                    name: James Bond
                                    organization_id: 4e252eb5-db8c-4fc5-9142-48307187d12f
                                    auth_user_id: 504a59b2-73f8-4588-a568-7ea3db3241d3
            400:
                description: |
                    Wrong arguments:
                    - OE0215: Wrong number of characters
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0214: Argument should be a string
                    - OE0435: Auth call error
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
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        try:
            input_params = self._get_input_params()
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        res = await run_task(self.controller.get_authorized_employees,
                             organization_id, **input_params)
        employee_dict = {'employees': [e.to_dict() for e in res]}
        self.write(json.dumps(employee_dict, cls=ModelEncoder))
