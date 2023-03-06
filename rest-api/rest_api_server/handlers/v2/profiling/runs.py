import json
from datetime import datetime, timezone
from rest_api_server.controllers.profiling.run import RunAsyncController
from rest_api_server.utils import run_task, ModelEncoder, check_int_attribute
from rest_api_server.handlers.v1.base_async import (BaseAsyncItemHandler,
                                                    BaseAsyncCollectionHandler)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v2.profiling.base import ProfilingHandler
from optscale_exceptions.common_exc import WrongArgumentsException
from rest_api_server.exceptions import Err
from optscale_exceptions.http_exc import OptHTTPError


class RunAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                BaseAuthHandler, ProfilingHandler):
    def _get_controller_class(self):
        return RunAsyncController

    def post(self, *args, **kwargs):
        self.raise405()

    @staticmethod
    def check_date_arguments(args):
        max_date_length = int(datetime.max.replace(
            tzinfo=timezone.utc).timestamp() - 1)
        date_arg_names = ['end_date', 'start_date']
        try:
            for arg_name in date_arg_names:
                value = args.get(arg_name)
                if value is None:
                    continue
                check_int_attribute(
                    arg_name, value, max_length=max_date_length)
            end = args.get(date_arg_names[0])
            start = args.get(date_arg_names[1])
            if start and end and end - start < 0:
                raise WrongArgumentsException(
                    Err.OE0446, date_arg_names)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)

    async def get(self, organization_id, application_id, **url_params):
        """
        ---
        description: |
            Get list of application runs
            Required permission: INFO_ORGANIZATION
        tags: [profiling_runs]
        summary: List of application runs
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: application_id
            in: path
            description: Application id
            required: true
            type: string
        -   name: start_date
            in: query
            description: Start date (timestamp in seconds)
            required: false
            type: integer
        -   name: end_date
            in: query
            description: End date (timestamp in seconds)
            required: false
            type: integer
        responses:
            200:
                description: Application runs
                schema:
                    type: object
                    properties:
                        runs:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: Run id
                                    application_id:
                                        type: string
                                        description: App id
                                    start:
                                        type: integer
                                        description: Start time
                                    finish:
                                        type: integer
                                        description: End time
                                    state:
                                        type: integer
                                        description: Run status
                                    number:
                                        type: integer
                                        description: Number of run
                                    tags:
                                        type: object
                                        description: Object with tags
                                    data:
                                        type: object
                                        description: Object with data
                                    executors:
                                        type: array
                                        description: list of executors
                                        items:
                                            type: string
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
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        dt_args = {
            'start_date': self.get_arg('start_date', int),
            'end_date': self.get_arg('end_date', int),
        }
        self.check_date_arguments(dt_args)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(
            self.controller.list, organization_id, application_id, token,
            **dt_args)
        applications_dict = {'runs': res}
        self.write(json.dumps(applications_dict, cls=ModelEncoder))


class RunAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                          ProfilingHandler):
    def _get_controller_class(self):
        return RunAsyncController

    def post(self, *args, **kwargs):
        self.raise405()

    async def get(self, organization_id, id, **url_params):
        """
        ---
        description: |
            Get run info by ID
            Required permission: INFO_ORGANIZATION
        tags: [profiling_runs]
        summary: Get run info
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: id
            in: path
            description: Run ID
            required: true
            type: string
        responses:
            200:
                description: Run information
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Run id
                        application_id:
                            type: string
                            description: App id
                        start:
                            type: integer
                            description: Start time
                        finish:
                            type: integer
                            description: End time
                        state:
                            type: integer
                            description: Run status
                        number:
                            type: integer
                            description: Number of run
                        tags:
                            type: object
                            description: object with run tags
                        data:
                            type: object
                            description: object with run data
                        executors:
                            type: array
                            description: list of executors
                            items:
                                type: object
                        goals:
                            type: array
                            description: list of goals
                            items:
                                type: object
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
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.get, organization_id, id, token)
        self.write(json.dumps(res, cls=ModelEncoder))


class RunBreakdownItemHandler(RunAsyncItemHandler, ProfilingHandler):

    async def get(self, organization_id, id, **url_params):
        """
        ---
        description: |
            Get run info by ID
            Required permission: INFO_ORGANIZATION
        tags: [profiling_runs]
        summary: Get run info
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: id
            in: path
            description: Run ID
            required: true
            type: string
        responses:
            200:
                description: Run breakdown
                schema:
                    type: object
                    example:
                        breakdown:
                            1664975676:
                                executors_count: 1
                                cpu: 1
                                ram: 24
                                process_cpu: 0.6
                                process_ram: 11
                                loss: 0.19
                                step: 20
                            1664954321:
                                executors_count: 2
                                cpu: 2
                                ram: 48
                                process_cpu: 1
                                process_ram: 15
                                loss: 0.18
                                step: 50
                        executors:
                            -   id: 68e5c9d5-310b-460f-922c-a1d27d6085d7
                                platform_type: aws
                                instance_id: i-1234567890
                                account_id: 3841d
                                local_ip: 172.31.24.6
                                public_ip: 3.123.31.120
                                instance_type: t2.large
                                instance_region: eu-central-1
                        milestones:
                            -   run_id: 21d3b463-6be0-4fef-909e-b9e36c21c3cc
                                timestamp: 1664954321
                                milestone: Something happened
                        stages:
                            -   run_id: 21d3b463-6be0-4fef-909e-b9e36c21c3cc
                                start: 1664954002
                                end: 1664958763
                                name: Calculating
            'timestamp': time,
            'milestone': milestone
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
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.breakdown_get,
                             organization_id, id, token)
        self.write(json.dumps(res, cls=ModelEncoder))

    def patch(self, *args, **kwargs):
        self.raise405()

    def delete(self, *args, **kwargs):
        self.raise405()
