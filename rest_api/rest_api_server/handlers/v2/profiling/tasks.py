import json
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.controllers.profiling.task import (
    TaskAsyncController)
from rest_api.rest_api_server.handlers.v2.profiling.base import ProfilingHandler
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute, check_list_attribute)
from rest_api.rest_api_server.exceptions import Err


class TasksAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                  BaseAuthHandler, ProfilingHandler):
    def _get_controller_class(self):
        return TaskAsyncController

    def _validate_params(self, **data):
        allowed_args = ['key', 'name', 'metrics', 'owner_id', 'description']
        unexpected_args = list(filter(lambda x: x not in allowed_args, data))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            for k in ['key', 'name']:
                value = data.get(k)
                if value is None:
                    raise OptHTTPError(400, Err.OE0216, [k])
                if not isinstance(value, str):
                    raise OptHTTPError(400, Err.OE0214, [k])
                check_string_attribute(k, value)
            description = data.get('description')
            if description:
                check_string_attribute('description', description,
                                       max_length=1000)
            owner_id = data.get('owner_id')
            if owner_id is not None:
                if not isinstance(owner_id, str):
                    raise OptHTTPError(400, Err.OE0214, ['owner_id'])
                check_string_attribute('owner_id', owner_id)
            metrics = data.get('metrics')
            if metrics:
                if not isinstance(metrics, list):
                    raise OptHTTPError(400, Err.OE0385, ['metrics'])
                for metric_id in metrics:
                    check_string_attribute('metrics', metric_id)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create task
            Required permission: EDIT_PARTNER
        tags: [profiling_tasks]
        summary: Create task
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Task parameters
            required: true
            schema:
                type: object
                properties:
                    key:
                        type: string
                        description: Task key
                        example: Metrics Met
                    owner_id:
                        type: string
                        description: Owner id
                        example: Task owner
                    name:
                        type: string
                        description: Task name
                        example: metrics_met
                    description:
                        type: string
                        description: Task description
                        example: Example Task
                    metrics:
                        type: array
                        description: list of attached metrics
                        items:
                            type: string
                        example:
                            -   b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                            -   5c285343-274e-44c2-9b8b-c87359601fc4
        responses:
            201:
                description: Returns created task
                schema:
                    type: object
                    example:
                        id: 6e278b91-25f7-4baf-89ba-b43e92539781
                        name: Metrics Met
                        description: Example task
                        key: metrics_met
                        owner_id: 5c285343-274e-44c2-9b8b-c87359601fc4
                        metrics:
                            -   id: b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                                name: Accuracy calculation
                                target_value: 0.8
                                tendency: more
                                key: accuracy
                            -   id: 5c285343-274e-44c2-9b8b-c87359601fc4
                                name: Loss calculation
                                target_value: 0.7
                                tendency: less
                                key: loss
                        owner:
                            -   id: 5c285343-274e-44c2-9b8b-c87359601fc4
                            -   name: My name
                        status: Completed
                        last_run: 1665523835
                        last_run_duration: 3939
                        last_successful_run: 1665523835
                        runs_count: 1
                        runs:
                            -   id: 8a1b2b54-a7f4-4544-8d65-6f9e3ce2b35f
                                task_id: 5c285343-274e-44c2-9b8b-c87359601fc4
                                start: 1666691576
                                finish: 1666691256
                                state: 2
                                number: 1
                                tags:
                                    key: value
                                    project: regression
                                data:
                                    step: 2000
                                    loss: 0.153871
                                executors:
                                    -   i-09dc9f5553f84a9ad
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0216: Argument is not provided
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
                    - OE0002: Organization not found
            409:
                description: |
                    Conflict:
                    - OE0534: Task with key already exists
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        data = self._request_body()
        self._validate_params(**data)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(
            self.controller.create, organization_id, token, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get list of tasks
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [profiling_tasks]
        summary: List of organization tasks
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Organization tasks list
                schema:
                    type: object
                    properties:
                        tasks:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: |
                                            Unique organization task id
                                    name:
                                        type: string
                                        description: Task name
                                    owner_id:
                                        type: string
                                        description: Task owner id
                                    description:
                                        type: string
                                        description: Task description
                                    key:
                                        type: string
                                        description: Task key
                                    status:
                                        type: string
                                        description: |
                                            Run status
                                    last_run:
                                        type: integer
                                        description: |
                                            Last run timestamp
                                    last_run_duration:
                                        type: integer
                                        description: |
                                            Last run duration
                                    last_successful_run:
                                        type: integer
                                        description: |
                                            Last successful run
                                    metrics:
                                        type: array
                                        description: list of attached metrics
                                        items:
                                            type: object
                                        properties:
                                            id:
                                                type: string
                                                description: |
                                                  Unique organization metric id
                                            key:
                                                type: string
                                                description: Metric key
                                            name:
                                                type: string
                                                description: Metric name
                                            tendency:
                                                type: string
                                                enum: ['more', 'less']
                                                description: Metric tendency
                                            target_value:
                                                type: number
                                                description: Metric target value
                                    runs_count:
                                        type: integer
                                        description: |
                                            Number of runs
                                    runs:
                                        type: array
                                        description: list of runs
                                        items:
                                            type: object
                                        properties:
                                            id:
                                                type: string
                                                description: Run id
                                            task_id:
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
                    - OE0002: Object not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.list, organization_id, token)
        tasks_dict = {'tasks': res}
        self.write(json.dumps(tasks_dict, cls=ModelEncoder))


class TasksAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                            ProfilingHandler):
    VALIDATION_MAP = {
        'attach': (check_list_attribute, False, {}),
        'detach': (check_list_attribute, False, {}),
        'description': (
            check_string_attribute, True, {'min_length': 0, 'max_length': 1000}
        ),
        'owner_id': (check_string_attribute, False, {}),
        'name': (check_string_attribute, False, {}),
    }

    def _get_controller_class(self):
        return TaskAsyncController

    def _validate_params(self, **data):
        unexpected_args = list(filter(
            lambda x: x not in self.VALIDATION_MAP, data))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            for param_name, validation_data in self.VALIDATION_MAP.items():
                if param_name not in data:
                    continue
                validation_func, is_optional, extras = validation_data
                param_value = data.get(param_name)
                if param_value is not None or (
                        param_value is None and not is_optional):
                    validation_func(param_name, param_value, **extras)
                    if isinstance(param_value, list):
                        for v in param_value:
                            check_string_attribute(f'{param_name} values', v)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def get(self, organization_id, task_id, **kwargs):
        """
        ---
        description: |
            Get task info by ID
            Required permission: INFO_ORGANIZATION
        tags: [profiling_tasks]
        summary: Get task
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
        -   name: last_runs
            in: query
            description: Number of last runs
            required: false
            type: integer
        -   name: last_leaderboards
            in: query
            description: Number of last leaderboards
            required: false
            type: integer
        responses:
            200:
                description: Organization tasks list
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: |
                                Unique organization task id
                        name:
                            type: string
                            description: Task name
                        owner_id:
                            type: string
                            description: Task owner id
                        key:
                            type: string
                            description: Task key
                        description:
                            type: string
                            description: Task description
                        status:
                            type: string
                            description: |
                                Run status
                        last_run:
                            type: integer
                            description: |
                                Last run timestamp
                        last_run_duration:
                            type: integer
                            description: |
                                Last run duration
                        last_successful_run:
                            type: integer
                            description: |
                                Last successful run
                        metrics:
                            type: array
                            description: list of attached metrics
                            items:
                                type: object
                            properties:
                                id:
                                    type: string
                                    description: Unique organization metric id
                                key:
                                    type: string
                                    description: Metric key
                                name:
                                    type: string
                                    description: Metric name
                                tendency:
                                    type: string
                                    enum: ['more', 'less']
                                    description: Metric tendency
                                target_value:
                                    type: number
                                    description: Metric target value
                        runs_count:
                            type: integer
                            description: |
                                Number of runs
                        last_runs:
                            type: array
                            description: list of runs
                            items:
                                type: object
                            properties:
                                id:
                                    type: string
                                    description: Run id
                                task_id:
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
                        last_leaderboards:
                            type: array
                            description: list of leaderboards
                            items:
                                type: object
                            properties:
                                leaderboard_template_id:
                                    type: string
                                    description: Leaderboard template id
                                dataset_ids:
                                    type: array
                                    description: list of dataset ids
                                    items:
                                        type: string
                                name:
                                    type: string
                                    description: Leaderboard name
                                deleted_at:
                                    type: integer
                                    description: Deleted at timestamp
                                created_at:
                                    type: integer
                                    description: Created at timestamp
                                id:
                                    type: string
                                    description: Leaderboard id
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
        last_runs = self.get_arg('last_runs', int, 0)
        last_leaderboards = self.get_arg('last_leaderboards', int, 0)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.get, organization_id,
                             task_id, token, last_runs=last_runs,
                             last_leaderboards=last_leaderboards)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def patch(self, organization_id, task_id, **kwargs):
        """
        ---
        description: |
            Update task
            Required permission: EDIT_PARTNER
        tags: [profiling_tasks]
        summary: Update task
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: task_id
            in: path
            description: Task id
            required: True
            type: string
        -   in: body
            name: body
            description: body with updated parameters
            required: True
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: New task name
                        required: False
                        example: Metrics met
                    owner_id:
                        type: string
                        description: New task owner id
                        required: False
                        example: 5340379b-b88b-402a-be18-be442b66321e
                    description:
                        type: string
                        description: New task description
                        required: False
                        example: New task description
                    attach:
                        type: array
                        description: list of metrics to attach
                        items:
                            type: string
                        example:
                            -   6e278b91-25f7-4baf-89ba-b43e92539781
                            -   5c285343-274e-44c2-9b8b-c87359601fc4
                    detach:
                        type: array
                        description: list of metrics to detach
                        items:
                            type: string
                        example:
                            -   5be74ae0-fe96-40b0-b65d-d76d974f6913
        responses:
            200:
                description: New task object
                schema:
                    type: object
                    example:
                        id: 6e278b91-25f7-4baf-89ba-b43e92539781
                        name: Metrics Met
                        key: metrics_met
                        description: New task description
                        owner_id: 5c285343-274e-44c2-9b8b-c87359601fc4
                        metrics:
                            -   id: b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                                name: Accuracy calculation
                                target_value: 0.8
                                tendency: more
                                key: accuracy
                            -   id: 5c285343-274e-44c2-9b8b-c87359601fc4
                                name: Loss calculation
                                target_value: 0.7
                                tendency: less
                                key: loss
                        owner:
                            -   id: 5c285343-274e-44c2-9b8b-c87359601fc4
                            -   name: My name
                        status: Completed
                        last_run: 1665523835
                        last_run_duration: 3939
                        last_successful_run: 1665523835
                        runs_count: 1
                        runs:
                            -   id: 8a1b2b54-a7f4-4544-8d65-6f9e3ce2b35f
                                task_id: 5c285343-274e-44c2-9b8b-c87359601fc4
                                start: 1666691576
                                finish: 1666691256
                                state: 2
                                number: 1
                                tags:
                                    key: value
                                    project: regression
                                data:
                                    step: 2000
                                    loss: 0.153871
                                executors:
                                    -   i-09dc9f5553f84a9ad
            400:
                description: |
                    Wrong arguments:
                    - OE0177: Non unique parameters in get request
                    - OE0214: Argument should be a string
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0217: Invalid query parameter
                    - OE0233: Incorrect body received
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0543: External unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
            409:
                description: |
                    Conflict:
                    - OE0556: Metric is used in task leaderboard(s)
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        data = self._request_body()
        self._validate_params(**data)
        res = await run_task(self.controller.edit,
                             organization_id, task_id, token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, organization_id, task_id, **kwargs):
        """
        ---
        description: |
            Deletes task with specified id
            Required permission: EDIT_PARTNER
        tags: [profiling_tasks]
        summary: Delete task
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
        responses:
            204:
                description: Success
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
                    - OE0002: Task not found
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        await run_task(self.controller.delete, task_id, token)
        self.set_status(204)
