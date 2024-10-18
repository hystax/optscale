import json
from datetime import datetime, timezone
from rest_api.rest_api_server.controllers.profiling.run import (
    RunAsyncController, RunBulkAsyncController)
from rest_api.rest_api_server.utils import run_task, ModelEncoder, check_int_attribute
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncItemHandler, BaseAsyncCollectionHandler)
from rest_api.rest_api_server.handlers.v1.base import (
    BaseAuthHandler, BaseAuthQueryTokenHandler)
from rest_api.rest_api_server.handlers.v2.profiling.base import ProfilingHandler
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.exceptions import Err
from tools.optscale_exceptions.http_exc import OptHTTPError


class RunBulkAsyncHandler(BaseAsyncCollectionHandler,
                          BaseAuthHandler,
                          ProfilingHandler):
    def _get_controller_class(self):
        return RunBulkAsyncController

    def post(self, *args, **kwargs):
        self.raise405()

    async def get(self, organization_id, task_id, **kwargs):
        """
        ---
        description: |
            Get list of task runs bulk
            Required permission: INFO_ORGANIZATION
        tags: [profiling_runs]
        summary: List of task runs
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: task_id
            in: path
            description: Task id
            required: true
            type: string
        -   in: query
            name: run_id
            description: run id
            required: false
        responses:
            200:
                description: Task runs
                schema:
                    type: object
                    properties:
                        type: array
                        items:
                            type: object
                            properties:
                                id:
                                    type: string
                                    description: Run id
                                task_id:
                                    type: string
                                    description: Task id
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
                                imports:
                                    type: array
                                    description: List of imported modules
                                    items:
                                        type: string
                                tags:
                                    type: object
                                    description: Object with tags
                                hyperparameters:
                                    type: object
                                    description: Object with hyperparameters
                                data:
                                    type: object
                                    description: Object with data
                                executors:
                                    type: array
                                    description: List of executors
                                    items:
                                        type: string
                                dataset_id:
                                    type: string
                                    description: Dataset id
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
                    - OE0543: External unauthorized
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
        arg = "run_id"
        run_ids = self.get_arguments(arg)
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        try:
            res = await run_task(
                self.controller.bulk_runs_get, task_id, token, run_ids)
        except OptHTTPError as exc:
            if exc.status_code == 400:
                res = []
            else:
                raise
        self.write(json.dumps(res, cls=ModelEncoder))


class RunAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                BaseAuthHandler,
                                ProfilingHandler):
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

    async def get(self, organization_id, task_id, **url_params):
        """
        ---
        description: |
            Get list of task runs
            Required permission: INFO_ORGANIZATION
        tags: [profiling_runs]
        summary: List of task runs
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: task_id
            in: path
            description: Task id
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
                description: Task runs
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
                                    task_id:
                                        type: string
                                        description: Task id
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
                                        description: List of executors
                                        items:
                                            type: string
                                    dataset:
                                        type: object
                                        description: Dataset object
                                    git:
                                        type: object
                                        description: Git object
                                    command:
                                        type: string
                                        description: |
                                            Command with which instrumented
                                            program has been launched
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
                    - OE0543: External unauthorized
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
        dt_args = {
            'start_date': self.get_arg('start_date', int),
            'end_date': self.get_arg('end_date', int),
        }
        self.check_date_arguments(dt_args)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(
            self.controller.list, organization_id, task_id, token,
            **dt_args)
        tasks_dict = {'runs': res}
        self.write(json.dumps(tasks_dict, cls=ModelEncoder))


class RunAsyncItemHandler(BaseAsyncItemHandler, BaseAuthQueryTokenHandler,
                          ProfilingHandler):
    def _get_controller_class(self):
        return RunAsyncController

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
        -   name: token
            in: query
            description: Unique token related to organization profiling token
            required: false
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
                        task_id:
                            type: string
                            description: Task id
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
                            description: Object with run tags
                        data:
                            type: object
                            description: Object with run data
                        executors:
                            type: array
                            description: List of executors
                            items:
                                type: object
                        metrics:
                            type: array
                            description: List of metrics
                            items:
                                type: object
                        dataset:
                            type: object
                            description: Dataset object
                        git:
                            type: object
                            description: Git object
                        command:
                            type: string
                            description: |
                                Command with which instrumented
                                program has been launched
                        console:
                            type: object
                            description: |
                                Console error and output
                            properties:
                                output:
                                    type: string
                                    description: console output data
                                error:
                                    type: string
                                    description: console error data
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
                    - OE0543: External unauthorized
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
        token = self.get_arg('token', str, None)
        if not await self.check_md5_profiling_token(
                organization_id, token, raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.get, organization_id, id, token)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, organization_id, id, **kwargs):
        """
        ---
        description: |
            Deletes run with specified id
            Required permission: CLUSTER_SECRET
        tags: [profiling_runs]
        summary: Delete run
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
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
        security:
        - secret: []
        """
        self.check_cluster_secret()
        token = await self._get_profiling_token(organization_id)
        await run_task(self.controller.delete, id, token)
        self.set_status(204)


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
        -   name: token
            in: query
            description: Unique token related to organization profiling token
            required: false
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
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
                    - OE0543: External unauthorized
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
        token = self.get_arg('token', str, None)
        if not await self.check_md5_profiling_token(
                organization_id, token, raises=False):
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
