import json

from tools.optscale_exceptions.common_exc import WrongArgumentsException
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.controllers.infrastructure.runset import (
    RunsetAsyncController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_dict_attribute, check_string_attribute,
    check_float_attribute, check_bool_attribute, check_int_attribute)
from rest_api.rest_api_server.handlers.v2.infrastructure.base import (
    InfrastructureHandler)


KiB = 1024


class RunsetsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                    BaseAuthHandler,
                                    InfrastructureHandler):
    VALIDATION_MAP = {
        'tags': (check_dict_attribute, True),
        'hyperparameters': (check_dict_attribute, True),
        'destroy_conditions': (check_dict_attribute, False),
        'application_id': (check_string_attribute, True),
        'cloud_account_id': (check_string_attribute, True),
        'region_id': (check_string_attribute, True),
        'instance_type': (check_string_attribute, True),
        'commands': (check_string_attribute, True),
        'name_prefix': (check_string_attribute, True),
        'open_ingress': (check_bool_attribute, False),
        'spot_settings': (check_dict_attribute, False),
    }
    CONDITIONS_VALIDATION_MAP = {
        'max_budget': (check_float_attribute, False),
        'reached_goals': (check_bool_attribute, False),
        'max_duration': (check_int_attribute, False),
    }
    SPOT_VALIDATION_MAP = {
        'tries': (check_int_attribute, False),
    }

    def _get_controller_class(self):
        return RunsetAsyncController

    def _validate_destroy_conditions(self, **data):
        unexpected_args = list(filter(
            lambda x: x not in self.CONDITIONS_VALIDATION_MAP, data))
        if unexpected_args:
            message = ', '.join(map(
                lambda x: f'destroy_conditions.{x}', unexpected_args))
            raise OptHTTPError(400, Err.OE0212, [message])
        for param_name, validation_data in self.CONDITIONS_VALIDATION_MAP.items():
            validation_func, is_required = validation_data
            param_value = data.get(param_name)
            if not is_required and not param_value:
                continue
            validation_func(param_name, param_value)

    def _validate_spot_settings(self, **data):
        unexpected_args = list(filter(
            lambda x: x not in self.SPOT_VALIDATION_MAP, data))
        if unexpected_args:
            message = ', '.join(map(
                lambda x: f'spot_settings.{x}', unexpected_args))
            raise OptHTTPError(400, Err.OE0212, [message])
        for param_name, validation_data in self.SPOT_VALIDATION_MAP.items():
            validation_func, is_required = validation_data
            param_value = data.get(param_name)
            if not is_required and param_value is None:
                continue
            extras = {}
            if param_name == 'tries':
                extras['min_length'] = 1  # tries must be non-zero if passed
                extras['max_length'] = 64  # doubt if more tries will help
            validation_func(param_name, param_value, **extras)

    def _validate_params(self, **data):
        unexpected_args = list(filter(
            lambda x: x not in self.VALIDATION_MAP, data))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            for param_name, validation_data in self.VALIDATION_MAP.items():
                validation_func, is_required = validation_data
                param_value = data.get(param_name)
                if not is_required and param_value is None:
                    continue
                extras = {}
                if param_name == 'commands':
                    # directly restricting user data size
                    extras['max_length'] = 128 * KiB
                validation_func(param_name, param_value, **extras)
                if isinstance(param_value, dict):
                    if param_name == 'destroy_conditions':
                        self._validate_destroy_conditions(**param_value)
                    elif param_name == 'spot_settings':
                        self._validate_spot_settings(**param_value)
                    else:
                        for k, v in param_value.items():
                            check_string_attribute(f'{param_name} key', k)
                            check_string_attribute(f'{param_name} value', v)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def post(self, organization_id, template_id, **url_params):
        """
        ---
        description: |
            Create runset from template
            Required permission: EDIT_PARTNER
        tags: [infrastructure_runsets]
        summary: Create runset from template
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Template parameters
            required: true
            schema:
                type: object
                properties:
                    name_prefix:
                        type: string
                        description: Template name prefix
                        required: true
                        example: test_ml
                    tags:
                        type: object
                        description: Template tags
                        required: true
                        example:
                            template_name: test
                    hyperparameters:
                        type: object
                        description: Template hyperparameters
                        required: true
                        example:
                            MODEL_URL: https://example.com/model/url
                            DATASET_URL: https://example.com/dataset/url
                            LEARNING_RATE: 1
                    cloud_account_id:
                        type: string
                        description: One of template cloud accounts ids
                        required: true
                        example: b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                    application_id:
                        type: string
                        description: One of template applications ids
                        required: true
                        example: b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                    instance_type:
                        type: string
                        description: One of template instance families names
                        required: true
                        example: p4
                    region_id:
                        type: string
                        description: One of template regions ids
                        required: true
                        example: us-east-1
                    commands:
                        type: string
                        description: User data to execute
                        required: true
                    destroy_conditions:
                        type: object
                        description: Runset destroy conditions
                        required: true
                        example:
                            max_budget: 1234,
                            reached_goals: True,
                            max_duration: 123456
                    open_ingress:
                        type: boolean
                        description: Open ingress on related runners
                        required: false
                    spot_settings:
                        type: object
                        description: Related runners spot settings
                        required: false
                        example:
                            tries: 4
        responses:
            201:
                description: Returns created runset
                schema:
                    type: object
                    example:
                        template:
                            id: 669b6bb9-ca19-449e-8252-91ff103eb423
                            name: test_template
                        name_prefix: test_prefix
                        tags:
                            template: test
                        hyperparameters:
                            MODEL_URL: https://example.com/model/url
                            DATASET_URL: https://example.com/dataset/url
                            LEARNING_RATE: 1
                        destroy_conditions:
                            max_budget: 1234
                            reached_goals: True
                            max_duration: 123456
                        id: c160ce40-c1bd-41c1-8445-25cdaafbe5c5
                        name: some_name
                        number: 1
                        cloud_account:
                            id: 7b03ca22-8d71-4005-aa09-2937c7ee7289
                            name: creds
                            type: aws_cnr
                        application:
                            id: 6e6f696e-218a-4718-8051-0da96168b360
                            name: Test project
                        owner:
                            id: a0a7fb4b-4cd3-4165-bec0-e6817ea65c35
                            name: name1
                        instance_type:
                            name: m5.xlarge
                            cloud_type: aws_cnr
                        region:
                            id: us-east-1
                            name: us-east-1
                            cloud_type: aws_cnr
                        duration: 0
                        runs_count: 0
                        succeeded_runs: 0
                        cost: 0
                        state: 1
                        created_at: 1617611286
                        started_at: 0
                        destroyed_at: 0
                        deleted_at: 0
                        open_ingress: False
                        spot_settings:
                            tries: 4
            400:
                description: |
                    Wrong arguments:
                    - OE0005: Instance type in region doesn't exist
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0216: Argument is not provided
                    - OE0223: Argument should be integer
                    - OE0224: Value of argument should be between 0 and 2147483647
                    - OE0344: Argument should be a dictionary
                    - OE0466: Argument should be float
                    - OE0538: Runset param should be one of
                    - OE0539: Runset param should be value
                    - OE0541: Budget should be less than value
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
                    - OE0378: Current user is not a member in provided organization
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        user_id = await self.check_self_auth()
        user_info = await self.get_user_info(user_id)
        data = self._request_body()
        self._validate_params(**data)
        data['user_id'] = user_info['id']
        token = await self._get_infrastructure_token(organization_id)
        res = await run_task(
            self.controller.create,
            organization_id, template_id, token, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def get(self, organization_id, template_id, **url_params):
        """
        ---
        description: |
            List runsets created from template
            Required permission: INFO_ORGANIZATION
        tags: [infrastructure_runsets]
        summary: List runsets created from template
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: template_id
            in: path
            description: Template id
            required: true
            type: string
        responses:
            200:
                description: Runsets created from template
                schema:
                    type: object
                    properties:
                        runsets:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: Unique runset id
                                    template:
                                        type: object
                                        description: Template info
                                        properties:
                                            id:
                                                type: string
                                                description: Template id
                                            name:
                                                type: string
                                                description: Template name
                                    name:
                                        type: string
                                        description: Runset name
                                    number:
                                        type: integer
                                        description: Runset number
                                    name_prefix:
                                        type: string
                                        description: Runset name prefix
                                    tags:
                                        type: object
                                        description: Runset tags
                                    hyperparameters:
                                        type: object
                                        description: Runset hyperparameters
                                    cloud_account:
                                        type: object
                                        description: Cloud account info
                                        properties:
                                            id:
                                                type: string
                                                description: Cloud account id
                                            name:
                                                type: string
                                                description: Cloud account name
                                            type:
                                                type: string
                                                description: Cloud type
                                    application:
                                        type: object
                                        description: Runset application info
                                        properties:
                                            id:
                                                type: string
                                                description: Application id
                                            name:
                                                type: string
                                                description: Application name
                                    instance_type:
                                        type: object
                                        description: Runset instance family info
                                        properties:
                                            name:
                                                type: string
                                                description: Instance type name
                                            type:
                                                type: string
                                                description: Cloud type
                                    region:
                                        type: object
                                        description: Template region info
                                        properties:
                                            id:
                                                type: string
                                                description: Region id
                                            name:
                                                type: string
                                                description: Region name
                                            type:
                                                type: string
                                                description: Cloud type
                                    commands:
                                        type: string
                                        description: User data to execute
                                    destroy_conditions:
                                        type: object
                                        description: Runset destroy conditions
                                        properties:
                                            max_budget:
                                                type: number
                                                description: |
                                                    Destroy runset if budget reached
                                            reached_goals:
                                                type: string
                                                description: |
                                                    Destroy runset if goals reached
                                            max_duration:
                                                type: string
                                                description: |
                                                    Destroy runset after certain duration
                                    duration:
                                        type: integer
                                        description: Runset duration
                                    cost:
                                        type: number
                                        description: Runset runners consumed cost
                                    runs_count:
                                        type: integer
                                        description: Runset runs count
                                    succeeded_runs:
                                        type: integer
                                        description: Runset succeeded runs count
                                    state:
                                        type: integer
                                        description: Runset state
                                    created_at:
                                        type: integer
                                        description: |
                                            Creation timestamp (service field)
                                    started_at:
                                        type: integer
                                        description: Runset start timestamp
                                    destroyed_at:
                                        type: integer
                                        description: Runset destroy timestamp
                                    deleted_at:
                                        type: integer
                                        description: |
                                            Deleted timestamp (service field)
                                    open_ingress:
                                        type: boolean
                                        description: |
                                            Open ingress on related runners
                                    spot_settings:
                                        type: object
                                        description: |
                                            Related runners spot settings
                                        properties:
                                            tries:
                                                type: integer
                                                description: |
                                                    Tries count to create spot instance
                        total_runs:
                            type: integer
                            description: Runsets runs count
                        total_cost:
                            type: number
                            description: Runsets runners cost
                        last_runset_cost:
                            type: number
                            description: Last runset runners cost
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
        token = await self._get_infrastructure_token(organization_id)
        res = await run_task(self.controller.list,
                             organization_id, template_id, token)
        self.write(json.dumps(res, cls=ModelEncoder))


class RunsetsAsyncItemHandler(BaseAsyncItemHandler,
                              BaseAuthHandler,
                              InfrastructureHandler):
    def _get_controller_class(self):
        return RunsetAsyncController

    def _validate_params(self, **data):
        unexpected_args = list(filter(
            lambda x: x != 'action', data))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            check_string_attribute('action', data.get('action'))
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def get(self, organization_id, runset_id, **kwargs):
        """
        ---
        description: |
            Get runset by ID
            Required permission: INFO_ORGANIZATION
        tags: [infrastructure_runsets]
        summary: Get runset
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: runset_id
            in: path
            description: Runset id
            required: true
            type: string
        responses:
            200:
                description: Runset object
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Unique runset id
                        template:
                            type: object
                            description: Template info
                            properties:
                                id:
                                    type: string
                                    description: Template id
                                name:
                                    type: string
                                    description: Template name
                        name:
                            type: string
                            description: Runset name
                        number:
                            type: integer
                            description: Runset number
                        name_prefix:
                            type: string
                            description: Runset name prefix
                        tags:
                            type: object
                            description: Runset tags
                        hyperparameters:
                            type: object
                            description: Runset hyperparameters
                        cloud_account:
                            type: object
                            description: Cloud account info
                            properties:
                                id:
                                    type: string
                                    description: Cloud account id
                                name:
                                    type: string
                                    description: Cloud account name
                                type:
                                    type: string
                                    description: Cloud type
                        application:
                            type: object
                            description: Runset application info
                            properties:
                                id:
                                    type: string
                                    description: Application id
                                name:
                                    type: string
                                    description: Application name
                        instance_type:
                            type: object
                            description: Runset instance family info
                            properties:
                                name:
                                    type: string
                                    description: Instance type name
                                type:
                                    type: string
                                    description: Cloud type
                        region:
                            type: object
                            description: Template region info
                            properties:
                                id:
                                    type: string
                                    description: Region id
                                name:
                                    type: string
                                    description: Region name
                                type:
                                    type: string
                                    description: Cloud type
                        commands:
                            type: string
                            description: User data to execute
                        destroy_conditions:
                            type: object
                            description: Runset destroy conditions
                            properties:
                                max_budget:
                                    type: number
                                    description: Destroy runset if budget reached
                                reached_goals:
                                    type: string
                                    description: Destroy runset if goals reached
                                max_duration:
                                    type: string
                                    description: |
                                        Destroy runset after certain duration
                        duration:
                            type: integer
                            description: Runset duration
                        cost:
                            type: number
                            description: Runset runners consumed cost
                        runs_count:
                            type: integer
                            description: Runset runs count
                        succeeded_runs:
                            type: integer
                            description: Runset succeeded runs count
                        state:
                            type: integer
                            description: Runset state
                        created_at:
                            type: integer
                            description: |
                                Creation timestamp (service field)
                        started_at:
                            type: integer
                            description: Runset start timestamp
                        destroyed_at:
                            type: integer
                            description: Runset destroy timestamp
                        deleted_at:
                            type: integer
                            description: |
                                Deleted timestamp (service field)
                        open_ingress:
                            type: boolean
                            description: |
                                Open ingress on related runners
                        spot_settings:
                            type: object
                            description: |
                                Related runners spot settings
                            properties:
                                tries:
                                    type: integer
                                    description: |
                                        Tries count to create spot instance
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
        token = await self._get_infrastructure_token(organization_id)
        res = await run_task(self.controller.get, organization_id,
                             runset_id, token)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, *args, **kwargs):
        self.raise405()

    async def patch(self, organization_id, runset_id, **kwargs):
        """
        ---
        description: |
            Update runset
            Required permission: EDIT_PARTNER
        tags: [infrastructure_runsets]
        summary: Update runset
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: runset_id
            in: path
            description: Runset id
            required: True
            type: string
        -   in: body
            name: body
            description: Body with updated parameters
            required: True
            schema:
                type: object
                properties:
                    action:
                        type: string
                        description: Action to perform
                        enum: [stop]
        responses:
            200:
                description: Runset object
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Unique runset id
                        template:
                            type: object
                            description: Template info
                            properties:
                                id:
                                    type: string
                                    description: Template id
                                name:
                                    type: string
                                    description: Template name
                        name:
                            type: string
                            description: Runset name
                        number:
                            type: integer
                            description: Runset number
                        name_prefix:
                            type: string
                            description: Runset name prefix
                        tags:
                            type: object
                            description: Runset tags
                        hyperparameters:
                            type: object
                            description: Runset hyperparameters
                        cloud_account:
                            type: object
                            description: Cloud account info
                            properties:
                                id:
                                    type: string
                                    description: Cloud account id
                                name:
                                    type: string
                                    description: Cloud account name
                                type:
                                    type: string
                                    description: Cloud type
                        application:
                            type: object
                            description: Runset application info
                            properties:
                                id:
                                    type: string
                                    description: Application id
                                name:
                                    type: string
                                    description: Application name
                        instance_type:
                            type: object
                            description: Runset instance family info
                            properties:
                                name:
                                    type: string
                                    description: Instance type name
                                type:
                                    type: string
                                    description: Cloud type
                        region:
                            type: object
                            description: Template region info
                            properties:
                                id:
                                    type: string
                                    description: Region id
                                name:
                                    type: string
                                    description: Region name
                                type:
                                    type: string
                                    description: Cloud type
                        commands:
                            type: string
                            description: User data to execute
                        destroy_conditions:
                            type: object
                            description: Runset destroy conditions
                            properties:
                                max_budget:
                                    type: number
                                    description: Destroy runset if budget reached
                                reached_goals:
                                    type: string
                                    description: Destroy runset if goals reached
                                max_duration:
                                    type: string
                                    description: |
                                        Destroy runset after certain duration
                        duration:
                            type: integer
                            description: Runset duration
                        cost:
                            type: number
                            description: Runset runners consumed cost
                        runs_count:
                            type: integer
                            description: Runset runs count
                        succeeded_runs:
                            type: integer
                            description: Runset succeeded runs count
                        state:
                            type: integer
                            description: Runset state
                        created_at:
                            type: integer
                            description: |
                                Creation timestamp (service field)
                        started_at:
                            type: integer
                            description: Runset start timestamp
                        destroyed_at:
                            type: integer
                            description: Runset destroy timestamp
                        deleted_at:
                            type: integer
                            description: |
                                Deleted timestamp (service field)
                        open_ingress:
                            type: boolean
                            description: |
                                Open ingress on related runners
                        spot_settings:
                            type: object
                            description: |
                                Related runners spot settings
                            properties:
                                tries:
                                    type: integer
                                    description: |
                                        Tries count to create spot instance
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0216: Argument is not provided
                    - OE0545: Action is not supported
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
            409:
                description: |
                    Conflict:
                    - OE0544: Runset state transition is not allowed
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_infrastructure_token(organization_id)
        data = self._request_body()
        self._validate_params(**data)
        res = await run_task(self.controller.edit,
                             organization_id, runset_id, token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))
