import json
from rest_api.rest_api_server.controllers.profiling.application import (
    ApplicationAsyncController)
from rest_api.rest_api_server.handlers.v2.profiling.base import ProfilingHandler
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder, check_string_attribute
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.exceptions import Err


class ApplicationsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                         BaseAuthHandler, ProfilingHandler):
    def _get_controller_class(self):
        return ApplicationAsyncController

    def _validate_params(self, **data):
        allowed_args = ['key', 'name', 'goals', 'owner_id']
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
            owner_id = data.get('owner_id')
            if owner_id is not None:
                if not isinstance(owner_id, str):
                    raise OptHTTPError(400, Err.OE0214, ['owner_id'])
                check_string_attribute('owner_id', owner_id)
            goals = data.get('goals')
            if goals:
                if not isinstance(goals, list):
                    raise OptHTTPError(400, Err.OE0385, ['goals'])
                for goal_id in goals:
                    check_string_attribute('goals', goal_id)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create application
            Required permission: EDIT_PARTNER
        tags: [profiling_applications]
        summary: Create application
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Application parameters
            required: true
            schema:
                type: object
                properties:
                    key:
                        type: string
                        description: Application key
                        example: Goals Met
                    owner_id:
                        type: string
                        description: Owner id
                        example: Application owner
                    name:
                        type: string
                        description: Application name
                        example: goals_met
                    goals:
                        type: array
                        description: list of attached goals
                        items:
                            type: string
                        example:
                            -   b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                            -   5c285343-274e-44c2-9b8b-c87359601fc4
        responses:
            201:
                description: Returns created application
                schema:
                    type: object
                    example:
                        id: 6e278b91-25f7-4baf-89ba-b43e92539781
                        name: Goals Met
                        key: goals_met
                        owner_id: 5c285343-274e-44c2-9b8b-c87359601fc4
                        goals:
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
                                application_id: 5c285343-274e-44c2-9b8b-c87359601fc4
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
                    - OE0534: Application is already exist
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
            Get list of applications
            Required permission: INFO_ORGANIZATION
        tags: [profiling_applications]
        summary: List of organization applications
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Organization applications list
                schema:
                    type: object
                    properties:
                        applications:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: |
                                            Unique organization application id
                                    name:
                                        type: string
                                        description: |
                                            Application name
                                    owner_id:
                                        type: string
                                        description: |
                                            Application owner id
                                    key:
                                        type: string
                                        description: |
                                            Application key
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
                                    goals:
                                        type: array
                                        description: list of attached goals
                                        items:
                                            type: object
                                        properties:
                                            id:
                                                type: string
                                                description: Unique organization goal id
                                            key:
                                                type: string
                                                description: Goal key
                                            name:
                                                type: string
                                                description: Goal name
                                            tendency:
                                                type: string
                                                enum: ['more', 'less']
                                                description: Goal tendency
                                            target_value:
                                                type: number
                                                description: Goal target value
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
                    - OE0002: Object not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.list, organization_id, token)
        applications_dict = {'applications': res}
        self.write(json.dumps(applications_dict, cls=ModelEncoder))


class ApplicationsAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                                   ProfilingHandler):
    def _get_controller_class(self):
        return ApplicationAsyncController

    def _validate_params(self, **data):
        allowed_args = ['name', 'attach', 'detach', 'owner_id']
        unexpected_args = list(filter(lambda x: x not in allowed_args, data))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            for k in ['name', 'owner_id']:
                value = data.get(k)
                if value is not None:
                    if not isinstance(value, str):
                        raise OptHTTPError(400, Err.OE0214, [k])
                    check_string_attribute(k, value)
            for k in ['attach', 'detach']:
                goals = data.get(k)
                if goals:
                    if not isinstance(goals, list):
                        raise OptHTTPError(400, Err.OE0385, [k])
                    for goal_id in goals:
                        check_string_attribute('goal_id', goal_id)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def get(self, organization_id, application_id, **kwargs):
        """
        ---
        description: |
            Get application info by ID
            Required permission: INFO_ORGANIZATION
        tags: [profiling_applications]
        summary: Get application
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
        responses:
            200:
                description: Organization applications list
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: |
                                Unique organization application id
                        name:
                            type: string
                            description: |
                                Application name
                        owner_id:
                            type: string
                            description: |
                                Application owner id
                        key:
                            type: string
                            description: |
                                Application key
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
                        goals:
                            type: array
                            description: list of attached goals
                            items:
                                type: object
                            properties:
                                id:
                                    type: string
                                    description: Unique organization goal id
                                key:
                                    type: string
                                    description: Goal key
                                name:
                                    type: string
                                    description: Goal name
                                tendency:
                                    type: string
                                    enum: ['more', 'less']
                                    description: Goal tendency
                                target_value:
                                    type: number
                                    description: Goal target value
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
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.get, organization_id,
                             application_id, token)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def patch(self, organization_id, application_id, **kwargs):
        """
        ---
        description: |
            Update application
            Required permission: EDIT_PARTNER
        tags: [profiling_applications]
        summary: Update application
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: application_id
            in: path
            description: Application id
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
                        description: New application name
                        required: False
                        example: Goals met
                    owner_id:
                        type: string
                        description: New application owner id
                        required: False
                        example: 5340379b-b88b-402a-be18-be442b66321e
                    attach:
                        type: array
                        description: list of goals to attach
                        items:
                            type: string
                        example:
                            -   6e278b91-25f7-4baf-89ba-b43e92539781
                            -   5c285343-274e-44c2-9b8b-c87359601fc4
                    detach:
                        type: array
                        description: list of goals to detach
                        items:
                            type: string
                        example:
                            -   5be74ae0-fe96-40b0-b65d-d76d974f6913
        responses:
            200:
                description: New application object
                schema:
                    type: object
                    example:
                        id: 6e278b91-25f7-4baf-89ba-b43e92539781
                        name: Goals Met
                        key: goals_met
                        owner_id: 5c285343-274e-44c2-9b8b-c87359601fc4
                        goals:
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
                                application_id: 5c285343-274e-44c2-9b8b-c87359601fc4
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
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        data = self._request_body()
        self._validate_params(**data)
        res = await run_task(self.controller.edit,
                             organization_id, application_id, token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, organization_id, application_id, **kwargs):
        """
        ---
        description: |
            Deletes application with specified id
            Required permission: EDIT_PARTNER
        tags: [profiling_applications]
        summary: Delete application
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
                    - OE0002: Application not found
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        await run_task(self.controller.delete,
                       application_id, token)
        self.set_status(204)
