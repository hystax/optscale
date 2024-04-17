import json
from rest_api.rest_api_server.handlers.v2.profiling.base import ProfilingHandler
from rest_api.rest_api_server.controllers.profiling.leaderboard_dataset import (
    LeaderboardDatasetAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute, check_list_attribute)
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.exceptions import Err


class LeaderboardDatasetBase(BaseAsyncItemHandler, BaseAuthHandler,
                             ProfilingHandler):

    def _get_controller_class(self):
        return LeaderboardDatasetAsyncController

    @staticmethod
    def _validate_dataset_ids(dataset_ids):
        check_list_attribute('dataset_ids', dataset_ids)
        for dataset_id in dataset_ids:
            check_string_attribute('dataset_ids', dataset_id)

    def _validate_params(self, create=False, **data):
        try:
            params = ['dataset_ids', 'name']
            unexpected_args = list(filter(lambda x: x not in params, data))
            if unexpected_args:
                message = ', '.join(unexpected_args)
                raise OptHTTPError(400, Err.OE0212, [message])
            missing_args = list(filter(lambda x: x not in data, params))
            if missing_args and create:
                message = ', '.join(missing_args)
                raise OptHTTPError(400, Err.OE0216, [message])
            ds_ids = data.get('dataset_ids')
            if ds_ids:
                self._validate_dataset_ids(ds_ids)
            name = data.get('name')
            if name:
                check_string_attribute('name', name)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)


class LeaderboardsDatasetAsyncGenerateHandler(LeaderboardDatasetBase):

    async def get(self, organization_id, leaderboard_dataset_id, **kwargs):
        """
        ---
        description: |
            Get leaderboard Dataset by ID
            Required permission: INFO_ORGANIZATION
        tags: [leaderboards]
        summary: Get leaderboard dataset info
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: leaderboard_dataset_id
            in: path
            description: leaderboard_dataset_id id
            required: true
            type: string
        responses:
            200:
                description: leaderboard datasets information
                schema:
                    type: array
                    items:
                        type: object
                        description: leaderboard dataset information
                        properties:
                            dataset_ids:
                                type: array
                                description: ids of datasets
                                example:
                                - 3656f89b-6b1e-421f-b709-3d0c164d9c33
                            run_ids:
                                type: array
                                description: ids of runs
                                example:
                                - a9be0d72-cab9-43c3-bb79-19b831e2bf85
                            tags:
                                description: tags
                                type: object
                                example:
                                    mode: Linear
                            hyperparams:
                                description: template hyperparameters
                                type: object
                                example:
                                    Model: null
                            metrics:
                                description: run metrics
                                type: object
                                example:
                                    accuracy: 1.1
                            primary_metric:
                                description: primary goal value
                                type: object
                                example:
                                    loss: 0
                            qualification:
                                type: array
                                description: covered datasets
                                example:
                                - 0662493d-b9aa-4c53-b4e7-30b7d73f205d
                            qual_runs:
                                type: array
                                description: filtered runs ids
                                example:
                                - 9801c63b-5adf-464c-991f-7acd7b0701bf
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
        res = await run_task(self.controller.generate, leaderboard_dataset_id,
                             token)
        self.write(json.dumps(res, cls=ModelEncoder))


class LeaderboardsDatasetAsyncCollectionHandler(LeaderboardDatasetBase):

    async def post(self, organization_id, leaderboard_id, **url_params):
        """
        ---
        description: |
            Create leaderboard
            Required permission: EDIT_PARTNER
        tags: [leaderboards]
        summary: Create leaderboard datasets
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: leaderboard_id
            in: path
            description: Leaderboard id
            required: true
            type: string
        -   in: body
            name: body
            description: Leaderboard dataset parameters
            required: true
            schema:
                type: object
                properties:
                    dataset_ids:
                        type: list
                        description: List of dataset ids
                        required: true
                        example: ['583694e5-65f9-4bf9-9eae-51de804bb624']
                    name:
                        type: string
                        description: Name
                        required: true
                        example: "Experiment just-a-test"
        responses:
            201:
                description: Returns created leaderboard dataset
                schema:
                    type: object
                    example:
                        id: "a39fce0e-4768-4bfe-a3b0-2cbbe9bf3c7e"
                        leaderboard_id: 05c1f12e-588b-4108-8b74-f48590fd23b9
                        name: my lbds
                        dataset_ids: ['43faf829-78c2-4fb2-b61d-2c07c33da3ef']
                        created_at: 123
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0385: Argument should be a list
                    - OE0216: Argument is not provided
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
            'EDIT_PARTNER', 'organization', organization_id)
        data = self._request_body()
        self._validate_params(create=True, **data)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(self.controller.create, leaderboard_id, token,
                             **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def get(self, organization_id, leaderboard_id):
        """
        ---
        description: |
            Get leaderboard Dataset list by leaderboard ID
            Required permission: INFO_ORGANIZATION
        tags: [leaderboards]
        summary: Get leaderboard dataset list
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: leaderboard_id
            in: path
            description: leaderboard id
            required: true
            type: string
        responses:
            200:
                description: Organization leaderboard dataset information
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            name:
                                type: string
                                description: leaderboard dataset name
                            id:
                                type: string
                                description: leaderboard dataset id
                            leaderboard_id:
                                type: string
                                description: leaderboard id
                            created_at:
                                type: integer
                                description: created at timestamp
                            deleted_at:
                                type: integer
                                description: deleted at timestamp
                            dataset_ids:
                                type: array
                                description: ids of datasets
                                example:
                                - 3656f89b-6b1e-421f-b709-3d0c164d9c33
                            primary_metric:
                                type: object
                                properties:
                                    name:
                                        type: string
                                        description: Goal name
                                    key:
                                        type: string
                                        description: Goal key
                                    tendency:
                                        type: string
                                        description: Tendency
                                        example: more
                                    func:
                                        type: string
                                        description: Func
                                        example: sum
                                    target_value:
                                        type: number
                                        description: Goal target value
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
        res = await run_task(self.controller.list, leaderboard_id, token)
        self.write(json.dumps(res, cls=ModelEncoder))


class LeaderboardsDatasetAsyncItemHandler(LeaderboardDatasetBase):

    async def get(self, organization_id, leaderboard_dataset_id, **kwargs):
        """
        ---
        description: |
            Get leaderboard Dataset by ID
            Required permission: INFO_ORGANIZATION
        tags: [leaderboards]
        summary: Get leaderboard dataset info
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: leaderboard_dataset_id
            in: path
            description: leaderboard_dataset_id id
            required: true
            type: string
        -   name: details
            in: query
            type: boolean
            description: show details
            required: false
        responses:
            200:
                description: Organization leaderboard information
                schema:
                    type: object
                    example:
                        id: "a39fce0e-4768-4bfe-a3b0-2cbbe9bf3c7e"
                        leaderboard_id: 05c1f12e-588b-4108-8b74-f48590fd23b9
                        name: my lbds
                        grouping_tags: ['43faf829-78c2-4fb2-b61d-2c07c33da3ef']
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
        res = await run_task(
            self.controller.get, leaderboard_dataset_id, token, details)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def patch(self, organization_id, leaderboard_dataset_id, **kwargs):
        """
        ---
        description: |
            Update leaderboard dataset
            Required permission: EDIT_PARTNER
        tags: [leaderboards]
        summary: Update leaderboard dataset
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: leaderboard_dataset_id
            in: path
            description: Leaderboard dataset id
            required: true
            type: string
        -   in: body
            name: body
            description: body with updated parameters
            required: True
            schema:
                type: object
                properties:
                    dataset_ids:
                        type: list
                        description: List of dataset ids
                        required: true
                        example: ['583694e5-65f9-4bf9-9eae-51de804bb624']
                    name:
                        type: string
                        description: name
                        required: true
                        example: "Test Leaderboard Dataset"
        responses:
            200:
                description: Updated leaderboard dataset object
                schema:
                    type: object
                    example:
                        id: "a39fce0e-4768-4bfe-a3b0-2cbbe9bf3c7e"
                        leaderboard_id: 05c1f12e-588b-4108-8b74-f48590fd23b9
                        name: my lbds
                        grouping_tags: ['43faf829-78c2-4fb2-b61d-2c07c33da3ef']
                        group_by_hp: True
                        created_at: 123
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
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
        res = await run_task(self.controller.edit, leaderboard_dataset_id, token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, organization_id, leaderboard_dataset_id, **kwargs):
        """
        ---
        description: |
            Deletes leaderboard dataset with specified id
            Required permission: EDIT_PARTNER
        tags: [leaderboards]
        summary: Delete leaderboard dataset
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: leaderboard_dataset_id
            in: path
            description: Leaderboard dataset id
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
        await run_task(self.controller.delete, leaderboard_dataset_id, token)
        self.set_status(204)
