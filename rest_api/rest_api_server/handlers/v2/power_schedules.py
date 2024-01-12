import json
import logging
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncItemHandler, BaseAsyncCollectionHandler)
from rest_api.rest_api_server.controllers.power_schedule import (
    PowerScheduleAsyncController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.utils import (
    ModelEncoder, run_task, check_list_attribute)
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException)


LOG = logging.getLogger(__name__)


class PowerSchedulesAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                           BaseAuthHandler):
    def _get_controller_class(self):
        return PowerScheduleAsyncController

    async def post(self, organization_id):
        """
        ---
        description: |
            Create new power schedule
            Required permission: EDIT_PARTNER
        summary: Create new power schedule
        tags: [power_schedules]
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: power schedule to add
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: Name of power schedule
                        required: True
                    timezone:
                        type: string
                        description: timezone name used to power on/off instances
                        required: True
                    power_off:
                        type: string
                        description: power off time in format HH:MM
                        required: True
                        example: "14:21"
                    power_on:
                        type: string
                        description: power on time in format HH:MM
                        required: True
                        example: "05:48"
                    start_date:
                        type: integer
                        description: power schedule start time timestamp UTC
                        required: False
                        example: 1698731002
                    end_date:
                        type: integer
                        description: power schedule end time timestamp UTC
                        required: False
                        example: 1698732002
                    enabled:
                        type: boolean
                        description: should power schedule be applied or not
                        required: False
        responses:
            201:
                description: Success (returns created object)
                schema:
                    type: object
                    example:
                        -   id: "86c4fdf2-8920-46dd-b7e0-fff443a43f1c"
                            organization_id: "9148a512-8b5e-48cd-8ac5-188875cf2f99"
                            name: "my schedule"
                            timezone: "Europe/Vienna"
                            power_off: "14:21"
                            power_on: "05:48"
                            enabled: True
                            start_date: 1687029026
                            end_date: 1697029026
                            created_at: 1587029026
                            deleted_at: 0
                            last_run: 0
                            last_run_error: null
                            resources_count: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0211: Parameter is immutable
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument is not provided
                    - OE0219: Invalid JSON body
                    - OE0223: Argument should be integer
                    - OE0224: Invalid parameter
                    - OE0226: enabled should be True or False
                    - OE0461: end_date can't be in past
                    - OE0550: Parameter should be time string in format HH:MM
                    - OE0552: Parameter power_on can\'t be equal to power_off
                    - OE0553: timezone should be a timezone name
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
            409:
                description: |
                    Conflict:
                    - OE0149: PowerSchedule with name already exists
        security:
        - token: []
        """
        await self.check_permissions('EDIT_PARTNER', 'organization',
                                     organization_id)
        data = self._request_body()
        data['organization_id'] = organization_id
        res = await run_task(self.controller.create, **data)
        self.set_status(201)
        self.write(json.dumps(res))

    async def get(self, organization_id, **kwargs):
        """
        ---
        description: |
            Gets a list of power schedules
            Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
        tags: [power_schedules]
        summary: List of power schedules
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Power schedules list
                schema:
                    type: object
                    properties:
                        power_schedules:
                            type: array
                            items:
                                type: object
                                properties:
                                    name:
                                        type: string
                                        description: Name of power schedule
                                    timezone:
                                        type: string
                                        description: |
                                          timezone name used to power on/off instances
                                    power_off:
                                        type: string
                                        description: power off time in format HH:MM
                                        example: "14:21"
                                    power_on:
                                        type: string
                                        description: power on time in format HH:MM
                                        example: "05:48"
                                    start_date:
                                        type: integer
                                        description: |
                                            power schedule start time timestamp UTC
                                        example: 1698731002
                                    end_date:
                                        type: integer
                                        description: |
                                            power schedule end time timestamp UTC
                                        example: 1698732002
                                    enabled:
                                        type: boolean
                                        description: |
                                            should power schedule be applied or not
                                    last_run:
                                        type: integer
                                        description: timestamp of the last run
                                        example: 0
                                    last_run_error:
                                        type: string
                                        description: |
                                            error for the last failed run, must be
                                            empty if the last run was successful
                                    deleted_at:
                                        type: integer
                                        example: 0
                                    created_at:
                                        type: integer
                                        example: 0
                                    resources_count:
                                        type: integer
                                        example: 5
                401:
                    description: |
                        Unauthorized:
                        - OE0235: Unauthorized
                        - OE0237: This resource requires authorization
                403:
                    description: |
                        Forbidden:
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
        result = await run_task(
            self.controller.list, organization_id=organization_id, **kwargs)
        power_schedules = {"power_schedules": result}
        self.write(json.dumps(power_schedules, cls=ModelEncoder))


class PowerSchedulesAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return PowerScheduleAsyncController

    async def get(self, power_schedule_id):
        """
        ---
        description: |
            Get power schedule
            Required permission: CLUSTER_SECRET or EDIT_PARTNER
        tags: [power_schedules]
        summary: Get power schedule
        parameters:
        -   name: power_schedule_id
            in: path
            description: power schedule id
            required: true
            type: string
        responses:
            200:
                description: Power schedule
                schema:
                    type: object
                    example:
                        -   id: "86c4fdf2-8920-46dd-b7e0-fff443a43f1c"
                            organization_id: "9148a512-8b5e-48cd-8ac5-188875cf2f99"
                            name: "my schedule"
                            timezone: "Europe/Vienna"
                            power_off: "14:21"
                            power_on: "05:48"
                            enabled: True
                            start_date: 1687029026
                            end_date: 1697029026
                            created_at: 1587029026
                            deleted_at: 0
                            last_run: 0
                            last_run_error: null
                            resources_count: 0
                            resources: []
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
            409:
                description: |
                    Conflict:
                    - OE0149: PowerSchedule with name already exists
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'power_schedule', power_schedule_id)
        result = await run_task(self.controller.get_item, power_schedule_id)
        self.write(json.dumps(result, cls=ModelEncoder))

    async def patch(self, power_schedule_id, **kwargs):
        """
        ---
        description: |
            Updates power schedule
            Required permission: CLUSTER_SECRET or EDIT_PARTNER
        tags: [power_schedules]
        summary: Updates power schedule
        parameters:
        -   name: power_schedule_id
            in: path
            description: power schedule id
            required: true
            type: string
        -   in: body
            name: body
            description: power schedule info
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: Name of power schedule
                        required: True
                    timezone:
                        type: string
                        description: timezone name used to power on/off instances
                        required: True
                    power_off:
                        type: string
                        description: power off time in format HH:MM
                        required: True
                        example: "14:21"
                    power_on:
                        type: string
                        description: power on time in format HH:MM
                        required: True
                        example: "05:48"
                    start_date:
                        type: integer
                        description: power schedule start time timestamp UTC
                        required: False
                        example: 1698731002
                    end_date:
                        type: integer
                        description: power schedule end time timestamp UTC
                        required: False
                        example: 1698732002
                    enabled:
                        type: boolean
                        description: should power schedule be applied or not
                        required: False
                    last_run:
                        type: integer
                        description: timestamp of the last run
                        required: False
                        example: 0
                    last_run_error:
                        type: string
                        description: |
                            error for the last failed run, must be empty if
                            the last run was successful
                        required: False
        responses:
            200:
                description: Power schedule
                schema:
                    type: object
                    example:
                        -   id: "86c4fdf2-8920-46dd-b7e0-fff443a43f1c"
                            organization_id: "9148a512-8b5e-48cd-8ac5-188875cf2f99"
                            name: "my schedule"
                            timezone: "Europe/Vienna"
                            power_off: "14:21"
                            power_on: "05:48"
                            enabled: True
                            start_date: 1687029026
                            end_date: 1697029026
                            created_at: 1587029026
                            deleted_at: 0
                            last_run: 0
                            last_run_error: null
                            resources_count: 0
                            resources: []
            400:
                description: |
                    Wrong arguments:
                    - OE0211: Parameter is immutable
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument is not provided
                    - OE0219: Invalid JSON body
                    - OE0223: Argument should be integer
                    - OE0224: Invalid parameter
                    - OE0226: enabled should be True or False
                    - OE0461: end_date can't be in past
                    - OE0550: Parameter should be time string in format HH:MM
                    - OE0552: Parameter power_on can\'t be equal to power_off
                    - OE0553: timezone should be a timezone name
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
            409:
                description: |
                    Conflict:
                    - OE0149: PowerSchedule with name already exists
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'EDIT_PARTNER', 'power_schedule', power_schedule_id)
        data = self._request_body()
        result = await run_task(
            self.controller.edit, power_schedule_id, **data)
        self.write(json.dumps(result, cls=ModelEncoder))

    async def delete(self, power_schedule_id, **kwargs):
        """
        ---
        description: |
            Delete power schedule
            Required permission: EDIT_PARTNER
        tags: [power_schedules]
        summary: Delete power schedule
        parameters:
        -   name: power_schedule_id
            in: path
            description: power schedule id
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
                    - OE0002: Object not found
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'power_schedule', power_schedule_id)
        await run_task(self.controller.delete, power_schedule_id, **kwargs)
        self.set_status(204)


class PowerSchedulesActionsAsyncHandler(BaseAsyncCollectionHandler,
                                        BaseAuthHandler):
    def _validate_params(self, kwargs):
        try:
            req_args = ['action', 'instance_id']
            args_unexpected = list(
                filter(lambda x: x not in req_args, kwargs.keys()))
            if args_unexpected:
                params = ', '.join(args_unexpected)
                raise WrongArgumentsException(Err.OE0212, [params])
            args_missing = list(
                filter(lambda x: x not in kwargs.keys(), req_args))
            params = ', '.join(args_missing)
            if args_missing:
                raise WrongArgumentsException(Err.OE0216, [params])
            if kwargs['action'] not in ['attach', 'detach']:
                raise WrongArgumentsException(Err.OE0217, ['action'])
            check_list_attribute('instance_id', kwargs['instance_id'])
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    def _get_controller_class(self):
        return PowerScheduleAsyncController

    async def post(self, power_schedule_id):
        """
        ---
        description: |
            Power schedule resources bulk actions
            Required permission: EDIT_PARTNER
        tags: [power_schedules]
        summary: Attach/detach resources to power schedule in one bulk operation
        parameters:
        -   in: path
            name: power_schedule_id
            description: power schedule id
            required: true
        -   in: body
            name: body
            description: power schedule to add
            required: true
            schema:
                type: object
                properties:
                    action:
                        description: instance's action
                        required: true
                        type: string
                        enum: [attach, detach]
                        example: attach
                    instance_id:
                        description: ids of active instances to attach/detach
                        required: true
                        type: array
                        items:
                            type: string
                        example: ["7e7dd1d2-3173-4e14-affc-9e5a9098a1b9",
                            "d7a8a215-2a61-404c-b4e3-5f1267ea3d0d"]
        responses:
            200:
                description: Applying action results
                schema:
                    type: object
                    example:
                        action: "attach"
                        failed: ["7e7dd1d2-3173-4e14-affc-9e5a9098a1b9"]
                        succeeded: ["d7a8a215-2a61-404c-b4e3-5f1267ea3d0d"]
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0216: Argument is not provided
                    - OE0217: Invalid argument
                    - OE0233: Incorrect body received
                    - OE0385: Argument should be a list
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
            'EDIT_PARTNER', 'power_schedule', power_schedule_id)
        data = self._request_body()
        self._validate_params(data)
        try:
            res = await run_task(self.controller.bulk_action,
                                 power_schedule_id, data)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(404, exc)
        self.write(res)
