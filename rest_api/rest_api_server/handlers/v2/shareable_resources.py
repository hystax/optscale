import json
from datetime import datetime, timezone
from rest_api.rest_api_server.controllers.shareable_resource import ShareableBookingAsyncController
from tools.optscale_exceptions.common_exc import (NotFoundException,
                                                  ForbiddenException)
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncItemHandler, BaseAsyncCollectionHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.models.enums import RolePurposes
from rest_api.rest_api_server.utils import run_task, ModelEncoder, check_int_attribute
from tools.optscale_exceptions.common_exc import WrongArgumentsException


class ShareableBookingBaseAsyncHandler(BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return ShareableBookingAsyncController

    async def check_booking_permission(self, resource_type, resource_id):
        user_id = await self.check_self_auth()
        user_roles = self.get_roles_info(
            [user_id], [RolePurposes.optscale_engineer.value,
                        RolePurposes.optscale_manager.value])
        user_purposes = {user_role.get('role_purpose')
                         for user_role in user_roles}
        cloud_resource_id = resource_id
        if resource_type == 'shareable_booking':
            try:
                shareable_booking = await run_task(self.controller.get,
                                                   resource_id)
            except NotFoundException as ex:
                raise OptHTTPError.from_opt_exception(404, ex)
            cloud_resource_id = shareable_booking.resource_id
        is_admin_permission = True
        if (RolePurposes.optscale_manager.value not in user_purposes and
                RolePurposes.optscale_engineer.value in user_purposes):
            is_admin_permission = False
            await self.check_permissions(
                'MANAGE_OWN_RESOURCES', 'cloud_resource', cloud_resource_id)
        else:
            await self.check_permissions('BOOK_ENVIRONMENTS', resource_type,
                                         resource_id)
        return is_admin_permission


class ShareableBookingAsyncHandler(BaseAsyncCollectionHandler,
                                   ShareableBookingBaseAsyncHandler):
    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create shareable book schedule for resource
            Required permission: BOOK_ENVIRONMENTS or MANAGE_OWN_RESOURCES
        tags: [shareable_resources]
        summary: Create shareable book schedule for resource
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: body
            description: Shareable book schedule info
            required: true
            schema:
                type: object
                properties:
                    resource_id:
                        type: string
                        description: "Resource id"
                        required: True
                        example: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                    acquired_by_id:
                        type: string
                        description: "Employee id"
                        required: True
                        example: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                    acquired_since:
                        type: integer
                        description: Shareable schedule start timestamp schedule
                        required: False
                    released_at:
                        type: integer
                        description: Shareable schedule till timestamp schedule
                        required: False
                    ssh_key_id:
                        type: string
                        description: Ssh key id
                        required: False
                    jira_auto_release:
                        type: boolean
                        description: "Release without attachmets"
                        required: False
                        example: True
        responses:
            201:
                description: Created (returns created shareable book object)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        resource_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        organization_id: 19239823-c9a1-448a-9ba3-b22f1f60e826
                        acquired_by: "{
                            'id': '747a69cb-9cb6-40c7-94a0-91979a9bd827',
                            'name': ''employee name'}"
                        acquired_since: 1628582018
                        released_at: 0
                        created_at: 1587029026
                        deleted_at: 0
                        ssh_key: "{'id': '2861cc1d-a201-4a3a-87ab-6cda88758208',
                            'created_at': 1634901529, 'deleted_at': 0,
                            'name': 'my ssh', 'default': 'False',
                            'employee_id': '2d383309-5e99-427a-a447-d35e87f8f097',
                            'fingerprint': '12:f8:7e:78:61:b4:bf:e2:de:24:15:96:4e:d4:72:53',
                            'key': 'ssh-rsa AAAAC3Nz ubuntu'}"
                        auto_detach_status: None
                        event_id: googlecalendareventid
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
                    - OE0233: Incorrect body received
                    - OE0384: Invalid resource type
                    - OE0416: Argument should not contain only whitespaces
                    - OE0435: Auth call error
                    - OE0446: released_at should be greater than acquired_since
                    - OE0454: Resource does not belong to the organization
                    - OE0456: Duplicate path parameters in the request body
                    - OE0480: Resource is not shareable
                    - OE0481: Clustered resource cannot have own shareable schedule booking
                    - OE0482: Shareable booking slot is already used. Select another one or release the existing before.
                    - OE0505: Employee doesn't have enough permissions
                    - OE0510: ssh_key does not belong to the employee
                    - OE0511: ssh_key should be default for employee
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
                    - OE0495: Creating of shareable booking in the past is not allowed.
            404:
                description: |
                    Not found:
                    - OE0002: Argument not found
        security:
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        resource_id = data.get('resource_id')
        is_admin_permission = await self.check_booking_permission(
            'cloud_resource', resource_id)
        res = await run_task(self.controller.create,
                             organization_id=organization_id,
                             is_admin_permission=is_admin_permission, **data)
        self.set_status(201)
        self.write(res)

    @staticmethod
    def check_date_arguments(args):
        max_date_length = datetime.max.replace(tzinfo=timezone.utc).timestamp()
        date_arg_names = ['end_date', 'start_date']
        try:
            for arg_name in date_arg_names:
                check_int_attribute(
                    arg_name, args[arg_name], max_length=max_date_length)
            if args[date_arg_names[0]] - args[date_arg_names[1]] < 0:
                raise WrongArgumentsException(
                    Err.OE0446, date_arg_names)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of booking with time interval activity
            Required permission: CLUSTER_SECRET
        tags: [shareable_resources]
        summary: List of bookings
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   name: start_date
            in: query
            description: Start date (timestamp in seconds)
            required: true
            type: integer
        -   name: end_date
            in: query
            description: End date (timestamp in seconds)
            required: false
            type: integer
        responses:
            200:
                description: List of booking
                schema:
                    type: object
                    properties:
                        data:
                            type: array
                            items:
                                type: object
                            example:
                                -   id: 0c273e0c-bf14-4a0c-87d8-3c17a0c5df42
                                    resource_id: ab9079bf-39eb-4ef5-8c3c-cf4619662b04
                                    created_at: 1634651742
                                    organization_id: 52485b43-c154-4d0a-b2cc-43ce26f1fbee
                                    acquired_by_id: a9f72db9-8e07-466f-88e9-82f51526f586
                                    deleted_at: 0
                                    acquired_since: 1634651742
                                    released_at: 0
                                    ssh_key: None
                                -   id: 42ca15ee-602e-4daf-9d0c-8533ccaf02ed
                                    resource_id: ab9079bf-39eb-4ef5-8c3c-cf4619662b04
                                    created_at: 1634651743
                                    organization_id: 52485b43-c154-4d0a-b2cc-43ce26f1fbee
                                    acquired_by_id: 5348030f-b0e1-44af-9731-2f664b6aa52f
                                    deleted_at: 0
                                    acquired_since: 1634651743
                                    released_at: 1634651745
                                    ssh_key: None
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
        security:
        - secret: []
        """
        self.check_cluster_secret()
        args = {
            'start_date': self.get_arg('start_date', int),
            'end_date': self.get_arg(
                'end_date', int, default=int(datetime.utcnow().timestamp()))
        }
        self.check_date_arguments(args)
        res = await run_task(self.controller.get_shareable_bookings,
                             organization_id=organization_id, **args)
        result = {'data': [r.to_dict() for r in res]}
        self.write(json.dumps(result, cls=ModelEncoder))


class ShareableResourceAsyncHandler(BaseAsyncCollectionHandler,
                                    ShareableBookingBaseAsyncHandler):
    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of resources with booking scopes
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [shareable_resources]
        summary: List of resources with booking scopes
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   name: client_key
            in: query
            description: Jira issue tenant id
            required: true
            type: string
        -   name: project_key
            in: query
            description: Jira issue project id
            required: true
            type: string
        -   name: issue_number
            in: query
            description: Jira issue number
            required: true
            type: string
        responses:
            200:
                description: List of resources with booking scopes
                schema:
                    type: object
                    properties:
                        data:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description:
                                        "Unique resource id"}
                                    name: {type: string,
                                        description: "Cloud resource name"}
                                    deleted_at: {type: integer,
                                        description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer,
                                        description:
                                        "Created timestamp (service field)"}
                                    cloud_account_id: {type: string,
                                        description: "cloud account id"}
                                    cloud_account_name: {type: string,
                                        description: "cloud account name"}
                                    cloud_account_type: {type: string,
                                        description: "cloud account type"}
                                    cloud_resource_id: {type: string,
                                        description: "Resource id in cloud"}
                                    resource_type: {type: string,
                                        description: "Type of cloud resource"}
                                    pool_id: {type: string,
                                        description: "Pool for resource"}
                                    employee_id: {type: string,
                                        description: "Cloud resource owner id"}
                                    tags: {type: object,
                                        description:
                                        "Cloud resource tags in name: value
                                        format"}
                                    region: {type: string,
                                        description: "Cloud resource region"}
                                    cloud_console_link: {type: string,
                                        description: "Cloud console link,
                                        show link if resource is active,
                                        else None"}
                                    shareable:
                                        type: boolean
                                        description: Is resource shareable?
                                    active:
                                        type: boolean
                                        description: Is resource active?
                                    ssh_only:
                                        type: boolean
                                        description: booking requires ssh_key
                                    shareable_bookings:
                                        type: array
                                        description: >
                                            present booking scopes
                                        items:
                                            type: object
                                            properties:
                                                id:
                                                    type: string
                                                    description: >
                                                        assignment history id
                                                resource_id:
                                                    type: string
                                                    description: resource id
                                                created_at:
                                                    type: integer
                                                    description: >
                                                        time of assignment
                                                organization_id:
                                                    type: string
                                                    description: >
                                                        organization to which
                                                        resource
                                                        is assigned
                                                acquired_by:
                                                    type: object
                                                    description: >
                                                        employee to which
                                                        book is assigned
                                                    properties:
                                                        id:
                                                          type: string
                                                          description: employee id
                                                        name:
                                                          type: string
                                                          description: employee name
                                                deleted_at:
                                                    type: integer
                                                    description: >
                                                        Deleted timestamp
                                                        (service field)
                                                acquired_since:
                                                    type: integer
                                                    description: >
                                                        Start timestamp for
                                                        acquiring
                                                released_at:
                                                    type: integer
                                                    description: >
                                                        End timestamp for
                                                        acquiring
                                                event_id:
                                                    type: string
                                                    description: >
                                                        Google Calendar event id
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
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        filters = {}
        for param, p_type in [
            ('client_key', str), ('project_key', str), ('issue_number', int)
        ]:
            value = self.get_arg(param, p_type, None)
            if value:
                filters.update({param: value})
        result = await run_task(self.controller.get_shareable_resources,
                                organization_id=organization_id)
        if filters:
            filtered_result = []
            for r in result:
                shareable_bookings = r.get('shareable_bookings')
                if not shareable_bookings:
                    continue
                for shareable_booking in shareable_bookings:
                    jira_issue_attachments = shareable_booking.get(
                        'jira_issue_attachments')
                    if not jira_issue_attachments:
                        continue
                    for jira_issue_attachment in jira_issue_attachments:
                        if all(item in jira_issue_attachment.items()
                               for item in filters.items()):
                            filtered_result.append(r)
            result = filtered_result
        self.write(json.dumps({'data': result}, cls=ModelEncoder))


class ShareableResourceBookingsAsyncHandler(BaseAsyncItemHandler,
                                            BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return ShareableBookingAsyncController

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get list of bookings for shareable resource
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [shareable_resources]
        summary: Get list of bookings for shareable resource
        parameters:
        -   in: path
            name: id
            description: resource id
            required: true
        responses:
            200:
                description: List of resource bookings
                schema:
                    type: object
                    properties:
                        bookings:
                            type: array
                            description: present booking scopes
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: booking id
                                    resource_id:
                                        type: string
                                        description: resource id
                                    created_at:
                                        type: integer
                                        description: time of booking creation
                                    organization_id:
                                        type: string
                                        description: >
                                            organization id
                                    acquired_by:
                                        type: object
                                        description: >
                                            employee to which
                                            book is assigned
                                        properties:
                                            id:
                                                type: string
                                                description: employee id
                                            name:
                                                type: string
                                                description: employee name
                                    deleted_at:
                                        type: integer
                                        description: >
                                            Deleted timestamp
                                            (service field)
                                    acquired_since:
                                        type: integer
                                        description: >
                                            Start timestamp for acquiring
                                    released_at:
                                        type: integer
                                        description: >
                                            End timestamp for acquiring
                                    ssh_key:
                                        type: strint
                                        description: >
                                            Json encoded string with ssh_key
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
                    - OE0002: Resource not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'cloud_resource', id)
        res = await run_task(self.controller.get_resource_bookings, id)
        requests = {'bookings': res}
        self.write(json.dumps(requests, cls=ModelEncoder))


class ShareableBookingAsyncItemHandler(BaseAsyncItemHandler,
                                       ShareableBookingBaseAsyncHandler):
    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Release existing shareable booking scope
            Required permission: MANAGE_RESOURCES or acquired_by user token
        tags: [shareable_resources]
        summary: Release shareable booking scope
        parameters:
        -   name: id
            in: path
            description: Shareable Booking Id
            required: true
            type: string
        responses:
            200:
                description: Success (returns modified value)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        resource_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        organization_id: 19239823-c9a1-448a-9ba3-b22f1f60e826
                        acquired_by_id: 747a69cb-9cb6-40c7-94a0-91979a9bd827
                        acquired_since: 1628582018
                        released_at: 0
                        created_at: 1587029026
                        deleted_at: 0
                        ssh_key: None
                        event_id: null
            400:
                description: |
                    Wrong arguments:
                    - OE0003: Database error
                    - OE0177: Non unique parameters in get request
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters
                    - OE0216: Argument is not provided
                    - OE0219: Argument should be a string with valid JSON
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
                    - OE0416: Argument should not contain only whitespaces
                    - OE0446: released_at should be greater than acquired_since
                    - OE0480: Resource is not shareable
                    - OE0482: Shareable booking slot is already used. Select another one or release the existing before.
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0498: Release of shareable booking is not allowed.
            404:
                description: |
                    Not found:
                    - OE0002: Shareable Booking or Employee not found
        security:
        - token: []
        """
        data = self._request_body()
        user_id = await self.check_self_auth()
        try:
            shareable_booking = await self._get_item(id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        is_admin_permission = True
        try:
            await self.check_permissions('MANAGE_RESOURCES',
                                         'shareable_booking', id)
        except OptHTTPError as exc:
            employee = await run_task(self.controller.get_employee_by_id,
                                      shareable_booking.acquired_by_id)
            is_admin_permission = False
            if exc.error_code != 'OE0234' or user_id != employee.auth_user_id:
                raise
        res = await run_task(self.controller.release,
                             item_id=id,
                             is_admin_permission=is_admin_permission, **data)
        self.set_status(200)
        self.write(res.to_json())

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get shareable booking info by ID
            Required permission: INFO_ORGANIZATION OR CLUSTER_SECRET
        tags: [shareable_resources]
        summary: Get shareable booking
        parameters:
        -   name: id
            in: path
            description: Shareable Booking ID
            required: true
            type: string
        responses:
            200:
                description: Success (shareable booking data)
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique shareable booking id"}
                        organization_id: {type: string,
                            description: "Organization id"}
                        resource_id: {type: string,
                            description: "Resource id"}
                        acquired_by: {type: string,
                            description: "Employee ID"}
                        deleted_at: {type: integer,
                            description: "Deleted timestamp (service field)"}
                        created_at: {type: integer,
                            description: "Created timestamp (service field)"}
                        acquired_since: {type: integer,
                            description: "Booking start timestamp"}
                        released_at: {type: integer,
                            description: "Release booking timestamp"}
                        ssh_key: {type: string,
                            description: "Json encoded strint with ssh_key"}
                        event_id : {type: string,
                            description: "Google Calendar event id"}
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
                    - OE0002: Shareable Booking not found
        security:
        - token: []
        - secret: []
        """
        shareable_booking = await self._get_item(id)
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'shareable_booking', id)
        self.write(shareable_booking.to_json())

    async def delete(self, id, **kwargs):
        """
        ---
        description: >
            Deletes a shareable booking with specified id
            Required permission: MANAGE_RESOURCES or acquired_by user token
        tags: [shareable_resources]
        summary: Delete shareable booking
        parameters:
        -   name: id
            in: path
            description: Shareable Booking ID
            required: true
            type: string
        responses:
            204: {description: Success}
            401: {description: "Unauthorized: \n\n
                - OE0235: Unauthorized\n\n
                - OE0237: This resource requires authorization"}
            403: {description: "Forbidden: \n\n
                - OE0234: Forbidden\n\n
                - OE0484: Deleting of shareable booking is not allowed."}
            404: {description: "Not found: \n\n
                - OE0002: Shareable Booking or Employee not found"}
        security:
        - token: []
        """
        user_id = await self.check_self_auth()
        try:
            shareable_booking = await self._get_item(id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        is_admin_permission = True
        try:
            await self.check_permissions('MANAGE_RESOURCES',
                                         'shareable_booking', id)
        except OptHTTPError as exc:
            employee = await run_task(self.controller.get_employee_by_id,
                                      shareable_booking.acquired_by_id)
            if exc.error_code == 'OE0234' and user_id == employee.auth_user_id:
                is_admin_permission = False
            else:
                raise
        try:
            await run_task(self.controller.delete, item_id=id,
                           is_admin_permission=is_admin_permission)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        self.set_status(204)
