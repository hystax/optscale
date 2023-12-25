import json
from rest_api.rest_api_server.handlers.v2.profiling.base import ProfilingHandler
from rest_api.rest_api_server.controllers.profiling.leaderboard import (
    LeaderboardAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute,
    check_dict_attribute, check_list_attribute, check_float_attribute,
    check_bool_attribute, check_int_attribute)
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.exceptions import Err


class LeaderboardsAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                                   ProfilingHandler):
    def _get_controller_class(self):
        return LeaderboardAsyncController

    @staticmethod
    def _validate_filters(filters):
        if not isinstance(filters, list):
            raise WrongArgumentsException(Err.OE0385, ['filters'])
        for filter_ in filters:
            if not isinstance(filter_, dict):
                raise WrongArgumentsException(Err.OE0217, ['filters'])
            opt_filters_keys = ['min', 'max']
            allowed_filter_keys = opt_filters_keys + ['id']
            unexpected_filter_keys = list(filter(
                lambda x: x not in allowed_filter_keys, filter_.keys()))
            if unexpected_filter_keys:
                message = ', '.join(unexpected_filter_keys)
                raise WrongArgumentsException(Err.OE0212, [message])
            if 'id' not in filter_ or not any(
                    filter_.get(x) is not None for x in opt_filters_keys):
                raise WrongArgumentsException(Err.OE0217, ['filters'])
            for key in opt_filters_keys:
                if filter_.get(key) is not None:
                    check_float_attribute(key, filter_[key], check_length=False)
            if (filter_.get('min') is not None and
                    filter_.get('max') is not None and
                    filter_['min'] > filter_['max']):
                raise WrongArgumentsException(Err.OE0541, ['min', 'max'])

    def _validate_params(self, create=False, **data):
        req_params = ['primary_goal', 'grouping_tags']
        opt_params = ['other_goals', 'filters', 'group_by_hp']
        allowed_args = req_params + opt_params
        unexpected_args = list(filter(lambda x: x not in allowed_args, data))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])
        missing_args = list(filter(lambda x: x not in data, req_params))
        if missing_args and create:
            message = ', '.join(missing_args)
            raise OptHTTPError(400, Err.OE0216, [message])
        try:
            # parameter: (check_function, allow_empty_parameter)
            attributes_check_map = {
                'grouping_tags': (check_list_attribute, False),
                'primary_goal': (check_string_attribute, None),
                'other_goals': (check_list_attribute, True),
                'filters': (check_list_attribute, True),
                'group_by_hp': (check_bool_attribute, None)
            }
            for param, (check_func, allow_empty) in attributes_check_map.items():
                if create or data.get(param) is not None:
                    check_params = {'name': param, 'value': data.get(param)}
                    if allow_empty is not None:
                        check_params['allow_empty'] = allow_empty
                    check_func(**check_params)
            filters = data.get('filters', [])
            if create or filters is not None:
                self._validate_filters(filters)
            if create:
                filters_goals_ids = [x['id'] for x in filters]
                goals = data.get('other_goals', []) + [data['primary_goal']]
                for goal_id in filters_goals_ids:
                    if goal_id not in goals:
                        raise WrongArgumentsException(Err.OE0217, ['filters'])
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def post(self, organization_id, application_id, **url_params):
        """
        ---
        description: |
            Create leaderboard
            Required permission: EDIT_PARTNER
        tags: [leaderboards]
        summary: Create leaderboard
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
        -   in: body
            name: body
            description: Leaderboard parameters
            required: true
            schema:
                type: object
                properties:
                    grouping_tags:
                        type: list
                        description: List of tags to filter runs
                        required: true
                        example: ['tag_1', 'tag_2']
                    primary_goal:
                        type: string
                        description: Goal id
                        required: true
                        example: "e788576e-e49a-4a9e-912b-51ad2efaad52"
                    other_goals:
                        type: list
                        description: Other goals to filter runs
                        required: false
                        example: ["d094f99a-4b1d-4f6b-8248-ef88a478f8a7"]
                    filters:
                        type: list
                        description: List of filters
                        required: false
                        example: [{"id": "d094f99a-4b1d-4f6b-8248-ef88a478f8a7",
                          "min": 0, "max": 1}]
                    group_by_hp:
                        type: boolean
                        description: Flag for grouping by hyperparameters
                        required: False
                        example: true
        responses:
            201:
                description: Returns created leaderboard
                schema:
                    type: object
                    example:
                        id: "a39fce0e-4768-4bfe-a3b0-2cbbe9bf3c7e"
                        application_id: 05c1f12e-588b-4108-8b74-f48590fd23b9
                        primary_goal: {'name': 'goal1_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'goal1_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}
                        other_goals: [{'name': 'goal2_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'goal2_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}]
                        filters: [{'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef',
                          'min': 1, 'max': 100, 'name': 'goal1_key'}]
                        grouping_tags: ['test_tag']
                        dataset_coverage_rules: {'users_count': 3}
                        group_by_hp: True
                        created_at: 123
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0223: Argument should be integer
                    - OE0224: Wrong float value
                    - OE0226: Argument should be boolean
                    - OE0344: Argument should be dict
                    - OE0466: Argument should be float
                    - OE0541: min should be less than max
                    - OE0549: leaderboard is already exist
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
                    - OE0149: Leaderboard is already exist
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        data = self._request_body()
        self._validate_params(create=True, **data)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.create, application_id, token,
                             **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def get(self, organization_id, application_id, **kwargs):
        """
        ---
        description: |
            Get leaderboard info by ID
            Required permission: INFO_ORGANIZATION
        tags: [leaderboards]
        summary: Get leaderboard info
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
        -   name: details
            in: query
            type: boolean
            description: Pool info for policy
            required: false
        responses:
            200:
                description: Organization leaderboard information
                schema:
                    type: object
                    example:
                        id: "a39fce0e-4768-4bfe-a3b0-2cbbe9bf3c7e"
                        application_id: 05c1f12e-588b-4108-8b74-f48590fd23b9
                        primary_goal: {'name': 'goal1_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'goal1_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}
                        other_goals: [{'name': 'goal2_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'goal2_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}]
                        filters: [{'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef',
                          'min': 1, 'max': 100, 'name': 'goal1_key'}]
                        grouping_tags: ['test_tag']
                        group_by_hp: True
                        created_at: 123
                        deleted_at: 0
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
        details = self.get_arg('details', bool, False)
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.get, application_id, token, details)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def patch(self, organization_id, application_id, **kwargs):
        """
        ---
        description: |
            Update leaderboard
            Required permission: EDIT_PARTNER
        tags: [leaderboards]
        summary: Update leaderboard
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
        -   in: body
            name: body
            description: body with updated parameters
            required: True
            schema:
                type: object
                properties:
                    grouping_tags:
                        type: list
                        description: List of tags to filter runs
                        required: true
                        example: ['tag_1', 'tag_2']
                    dataset_coverage_rules:
                        type: object
                        description: Dataset coverage rules
                        required: true
                        example: {"dataset_label": 3}
                    primary_goal:
                        type: string
                        description: Goal id
                        required: true
                        example: "e788576e-e49a-4a9e-912b-51ad2efaad52"
                    other_goals:
                        type: list
                        description: Other goals to filter runs
                        required: false
                        example: ["d094f99a-4b1d-4f6b-8248-ef88a478f8a7"]
                    filters:
                        type: list
                        description: List of filters
                        required: false
                        example: [{"id": "d094f99a-4b1d-4f6b-8248-ef88a478f8a7",
                          "min": 0, "max": 1}]
                    group_by_hp:
                        type: boolean
                        description: Flag for grouping by hyperparameters
                        required: False
                        example: true
        responses:
            200:
                description: Updated leaderboard object
                schema:
                    type: object
                    example:
                        id: "a39fce0e-4768-4bfe-a3b0-2cbbe9bf3c7e"
                        application_id: 05c1f12e-588b-4108-8b74-f48590fd23b9
                        primary_goal: {'name': 'goal1_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'goal1_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}
                        other_goals: [{'name': 'goal2_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'goal2_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}]
                        filters: [{'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef',
                          'min': 1, 'max': 100, 'name': 'goal1_key'}]
                        grouping_tags: ['test_tag']
                        group_by_hp: True
                        created_at: 123
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0223: Argument should be integer
                    - OE0224: Wrong float value
                    - OE0226: Argument should be boolean
                    - OE0344: Argument should be dict
                    - OE0466: Argument should be float
                    - OE0541: min should be less than max
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        data = self._request_body()
        self._validate_params(**data)
        res = await run_task(self.controller.edit, application_id, token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, organization_id, application_id, **kwargs):
        """
        ---
        description: |
            Deletes leaderboard with specified id
            Required permission: EDIT_PARTNER
        tags: [leaderboards]
        summary: Delete leaderboard
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
        await run_task(self.controller.delete, application_id, token)
        self.set_status(204)
