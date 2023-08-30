import json
from rest_api.rest_api_server.handlers.v2.profiling.base import ProfilingHandler
from rest_api.rest_api_server.controllers.profiling.goal import GoalAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute, check_float_attribute)
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.exceptions import Err


class GoalAsyncCollectionHandler(BaseAsyncCollectionHandler, BaseAuthHandler,
                                 ProfilingHandler):
    def _get_controller_class(self):
        return GoalAsyncController

    def _validate_params(self, **data):
        allowed_args = ['target_value', 'tendency', 'name', 'key', 'function']
        unexpected_args = list(filter(lambda x: x not in allowed_args, data))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            for k in ['tendency', 'name', 'key', 'function']:
                value = data.get(k)
                if value is None:
                    raise OptHTTPError(400, Err.OE0216, [k])
                if not isinstance(value, str):
                    raise OptHTTPError(400, Err.OE0214, [k])
                check_string_attribute(k, value)
            target_value = data.get('target_value')
            check_float_attribute('target_value', target_value)
            tendency = data.get('tendency')
            if tendency not in ['more', 'less']:
                raise OptHTTPError(400, Err.OE0217, ['tendency'])
            function = data.get('function')
            if function not in ['avg', 'sum', 'max', 'last']:
                raise OptHTTPError(400, Err.OE0217, ['function'])
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create goal
            Required permission: EDIT_PARTNER
        tags: [profiling_goals]
        summary: Create goal
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Goal parameters
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: Goal name
                        required: true
                        example: Goals met
                    key:
                        type: string
                        description: Goal key
                        required: true
                        example: goals_met
                    tendency:
                        type: string
                        description: Goal tendency
                        enum: ['more', 'less']
                        required: true
                        example: less
                    target_value:
                        type: number
                        description: Goal tagrget value
                        required: true
                        example: 0.9
                    function:
                        type: string
                        description: Aggregate function
                        required: true
                        enum: ['avg', 'sum', 'max', 'last']
                        example: sum
        responses:
            201:
                description: Returns created goal
                schema:
                    type: object
                    example:
                        id: b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                        display_name: Accuracy calculation
                        target_value: 0.8
                        tendency: more
                        name: accuracy_calc
                        function: sum
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0224: Wrong float value
                    - OE0466: Argument should be float
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
                    - OE0002: Organization not found
            409:
                description: |
                    Conflict:
                    - OE0002: Goal is already exist
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        data = self._request_body()
        self._validate_params(**data)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.create, token, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get list of organization goals
            Required permission: INFO_ORGANIZATION
        tags: [profiling_goals]
        summary: List of organization goals
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Organization goals list
                schema:
                    type: object
                    properties:
                        goals:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: |
                                            Unique organization goal id
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
                                        description: |
                                            Goal target value
                                    function:
                                        type: string
                                        enum: ['avg', 'sum', 'max', 'last']
                                        description: Aggregate function
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
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.list, token)
        goals_dict = {'goals': res}
        self.write(json.dumps(goals_dict, cls=ModelEncoder))


class GoalsAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                            ProfilingHandler):
    def _get_controller_class(self):
        return GoalAsyncController

    def _validate_params(self, **data):
        allowed_args = ['target_value', 'tendency', 'name', 'function']
        unexpected_args = list(filter(lambda x: x not in allowed_args, data))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            for k in ['tendency', 'name', 'function']:
                value = data.get(k)
                if value is not None:
                    if not isinstance(value, str):
                        raise OptHTTPError(400, Err.OE0214, [k])
                    check_string_attribute(k, value)
            target_value = data.get('target_value')
            if target_value is not None:
                check_float_attribute('target_value', target_value)
            tendency = data.get('tendency')
            if tendency is not None and tendency not in ['more', 'less']:
                raise OptHTTPError(400, Err.OE0217, ['tendency'])
            function = data.get('function')
            if function is not None and function not in ['avg', 'sum', 'max',
                                                         'last']:
                raise OptHTTPError(400, Err.OE0217, ['function'])
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def get(self, organization_id, id, **kwargs):
        """
        ---
        description: |
            Get goal info by ID
            Required permission: INFO_ORGANIZATION
        tags: [profiling_goals]
        summary: Get goal info
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: id
            in: path
            description: Goal ID
            required: true
            type: string
        responses:
            200:
                description: Organization goal information
                schema:
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
                        function:
                            type: string
                            enum: ['avg', 'sum', 'max', 'last']
                            description: Aggregate func
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
                    - OE0002: Goal not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.get, id, token)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def patch(self, organization_id, id, **kwargs):
        """
        ---
        description: |
            Update goal
            Required permission: EDIT_PARTNER
        tags: [profiling_goals]
        summary: Update goal
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: id
            in: path
            description: Goal ID
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
                        description: New goal name
                        required: False
                        example: Goals met
                    tendency:
                        type: string
                        enum: ['more', 'less']
                        required: False
                        description: Goal tendency
                        example: more
                    target_value:
                        type: number
                        description: Goal target value
                        required: False
                        example: 0.9
                    function:
                        type: string
                        enum: ['avg', 'sum', 'max', 'last']
                        description: Aggregate function
                        required: False
                        example: avg
        responses:
            200:
                description: New goal object
                schema:
                    type: object
                    example:
                        id: b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                        name: Accuracy calculation
                        target_value: 0.8
                        tendency: more
                        key: accuracy
                        function: sum
            400:
                description: |
                    Wrong arguments:
                    - OE0177: Non unique parameters in get request
                    - OE0214: Argument should be a string
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0217: Invalid query parameter
                    - OE0224: Wrong float value
                    - OE0233: Incorrect body received
                    - OE0466: Argument should be float
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        data = self._request_body()
        self._validate_params(**data)
        res = await run_task(self.controller.edit, id, token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, organization_id, id, **kwargs):
        """
        ---
        description: |
            Deletes goal with specified id
            Required permission: EDIT_PARTNER
        tags: [profiling_goals]
        summary: Delete goal
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: id
            in: path
            description: Goal ID
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
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        await run_task(self.controller.delete, id, token)
        self.set_status(204)
