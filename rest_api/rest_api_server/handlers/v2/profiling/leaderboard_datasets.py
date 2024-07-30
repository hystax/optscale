import json
from rest_api.rest_api_server.controllers.profiling.leaderboard_dataset import (
    LeaderboardDatasetAsyncController)
from rest_api.rest_api_server.handlers.v2.profiling.leaderboards import (
    LeaderboardBaseHandler)
from rest_api.rest_api_server.controllers.profiling.leaderboard import (
    LeaderboardAsyncController)
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute, check_list_attribute)
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException


class LeaderboardDatasetBase(LeaderboardBaseHandler):

    @staticmethod
    def get_required_params():
        return LeaderboardBaseHandler.get_required_params() + [
            'dataset_ids', 'name']

    def _get_controller_class(self):
        return LeaderboardDatasetAsyncController

    @staticmethod
    def _validate_dataset_ids(dataset_ids):
        check_list_attribute('dataset_ids', dataset_ids)
        for dataset_id in dataset_ids:
            check_string_attribute('dataset_ids', dataset_id)

    async def _update_params(self, body, leaderboard_id, token):
        leaderboard_ctrl = LeaderboardAsyncController(
            self.session(), self._config, self.token)
        leaderboard = await run_task(leaderboard_ctrl.get_by_id,
                                     leaderboard_id, token)
        lb_params = self.get_optional_params() + self.get_required_params()
        for opt in lb_params:
            param = leaderboard.get(opt)
            if opt not in body and param is not None:
                body[opt] = param
        return body

    def _validate_params(self, create=False, **data):
        super()._validate_params(create=create, **data)
        try:
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
                    dataset_coverage_rules:
                        type: object
                        description: Dataset coverage rules
                        required: false
                        example: {"dataset_label": 3}
                    grouping_tags:
                        type: list
                        description: List of tags to filter runs
                        required: true
                        example: ['tag_1', 'tag_2']
                    primary_metric:
                        type: string
                        description: Metric id
                        required: true
                        example: "e788576e-e49a-4a9e-912b-51ad2efaad52"
                    other_metrics:
                        type: list
                        description: Other metrics to filter runs
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
                        primary_metric: {'name': 'metric1_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'metric1_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}
                        other_metrics: [{'name': 'metric2_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'metric2_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}]
                        filters: [{'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef',
                          'min': 1, 'max': 100, 'name': 'metric1_key'}]
                        grouping_tags: ['test_tag']
                        group_by_hp: True
                        dataset_coverage_rules: {"dataset_label": 3}
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
        token = await self._get_profiling_token(organization_id)
        data = await self._update_params(self._request_body(),
                                         leaderboard_id, token)
        self._validate_params(create=True, **data)
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
                                type: string
                                description: Metric id
                                example: "e788576e-e49a-4a9e-912b-51ad2efaad52"
                            other_metrics:
                                type: list
                                description: Other metrics to filter runs
                                example: ["d094f99a-4b1d-4f6b-8248-ef88a478f8a7"]
                            filters:
                                type: list
                                description: List of filters
                                example: [{"id": "d094f99a-4b1d-4f6b-8248-ef88a478f8a7",
                                  "min": 0, "max": 1}]
                            grouping_tags:
                                type: list
                                description: List of tags to filter runs
                                example: ['tag_1', 'tag_2']
                            group_by_hp:
                                type: boolean
                                description: Flag for grouping by hyperparameters
                                example: true
                            dataset_coverage_rules:
                                type: object
                                description: Dataset coverage rules
                                example: {"dataset_label": 3}
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
                        created_at: 123
                        deleted_at: 0
                        dataset_coverage_rules: {"dataset_label": 3}
                        primary_metric: {'name': 'metric1_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'metric1_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}
                        other_metrics: [{'name': 'metric2_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'metric2_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}]
                        filters: [{'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef',
                          'min': 1, 'max': 100, 'name': 'metric1_key'}]
                        grouping_tags: ['test_tag']
                        group_by_hp: True
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
                        required: false
                        example: ['583694e5-65f9-4bf9-9eae-51de804bb624']
                    name:
                        type: string
                        description: name
                        required: false
                        example: "Test Leaderboard Dataset"
                    dataset_coverage_rules:
                        type: object
                        description: Dataset coverage rules
                        required: false
                        example: {"dataset_label": 3}
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
                        dataset_coverage_rules: {"dataset_label": 3}
                        primary_metric: {'name': 'metric1_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'metric1_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}
                        other_metrics: [{'name': 'metric2_key', 'target_value': 0.7,
                          'tendency': 'more', 'key': 'metric2_key', 'func': 'avg',
                          'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef'}]
                        filters: [{'id': '43faf829-78c2-4fb2-b61d-2c07c33da3ef',
                          'min': 1, 'max': 100, 'name': 'metric1_key'}]
                        grouping_tags: ['test_tag']
                        group_by_hp: True
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
