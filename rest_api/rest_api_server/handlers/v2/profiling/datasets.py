import json

from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.controllers.profiling.dataset import (
    DatasetAsyncController)
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute, check_list_attribute,
    check_int_attribute, check_dict_attribute)
from rest_api.rest_api_server.handlers.v2.profiling.base import (
    ProfilingHandler)

from tools.optscale_exceptions.common_exc import WrongArgumentsException
from tools.optscale_exceptions.http_exc import OptHTTPError


def check_timespan_range(data: dict):
    if 'timespan_from' in data:
        if data['timespan_from'] is not None:
            check_int_attribute('timespan_from', data['timespan_from'])
    if 'timespan_to' in data:
        if data['timespan_to'] is not None:
            timespan_from = data.get('timespan_from')
            min_length = timespan_from if timespan_from else 0
            check_int_attribute('timespan_to', data['timespan_to'],
                                min_length=min_length)


class DatasetsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                     BaseAuthHandler,
                                     ProfilingHandler):
    VALIDATION_MAP = {
        'labels': (check_list_attribute, False),
        'description': (check_string_attribute, False),
        'name': (check_string_attribute, False),
        'path': (check_string_attribute, True),
        'timespan_from': (check_int_attribute, False),
        'timespan_to': (check_int_attribute, False)
    }

    def _get_controller_class(self):
        return DatasetAsyncController

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
                if not is_required and not param_value:
                    continue
                validation_func(param_name, param_value)
                if isinstance(param_value, list):
                    for v in param_value:
                        check_string_attribute(f'{param_name} values', v)
            check_timespan_range(data)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create dataset
            Required permission: EDIT_PARTNER
        tags: [profiling_datasets]
        summary: Create dataset
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Dataset parameters
            required: true
            schema:
                type: object
                properties:
                    path:
                        type: string
                        description: Dataset path
                        required: true
                        example: s3://ml-bucket/dataset
                    name:
                        type: string
                        description: Dataset name
                        required: false
                        example: Test
                    description:
                        type: string
                        description: Dataset description
                        required: false
                        example: Test ML dataset
                    labels:
                        type: array
                        description: |
                            List of labels related to leaderboards
                            evaluation protocols
                        required: false
                        example:
                        - test
                        - demo
                    timespan_from:
                        type: integer
                        description: Timespan from timestamp
                        required: false
                        example: 1698740386
                    timespan_to:
                        type: integer
                        description: Timespan to timestamp
                        required: false
                        example: 1698740386
        responses:
            201:
                description: Returns created dataset
                schema:
                    type: object
                    example:
                        id: 1519de9a-9430-41d9-9af9-772adb36b051
                        path: s3://ml-bucket/dataset
                        name: Test
                        description: Test ML dataset
                        labels:
                        - test
                        - demo
                        created_at: 1697175347
                        deleted_at: 0
                        timespan_from: 1698740386
                        timespan_to: 1698741386
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0216: Argument is not provided
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer value
                    - OE0385: Argument should be a list
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
                    - OE0551: Dataset with such name already exists
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        data = self._request_body()
        self._validate_params(**data)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(
            self.controller.create, token, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            List datasets
            Required permission: INFO_ORGANIZATION
        tags: [profiling_datasets]
        summary: List datasets
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Datasets list
                schema:
                    type: object
                    properties:
                        datasets:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: Unique dataset id
                                    path:
                                        type: string
                                        description: Dataset path
                                    name:
                                        type: string
                                        description: Dataset name
                                    description:
                                        type: string
                                        description: Dataset description
                                    labels:
                                        type: array
                                        description: |
                                            List of labels related to leaderboards
                                            evaluation protocols
                                        items:
                                            type: string
                                    created_at:
                                        type: integer
                                        description: Creation timestamp (service field)
                                    deleted_at:
                                        type: integer
                                        description: Deleted timestamp (service field)
                                    timespan_from:
                                        type: integer
                                        description: Timespan from timestamp
                                    timespan_to:
                                        type: integer
                                        description: Timespan to timestamp
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
        res = await run_task(self.controller.list, token)
        datasets_dict = {'datasets': res}
        self.write(json.dumps(datasets_dict, cls=ModelEncoder))


class DatasetsAsyncItemHandler(BaseAsyncItemHandler,
                               BaseAuthHandler,
                               ProfilingHandler):
    VALIDATION_MAP = {
        'labels': (check_list_attribute, {'allow_empty': True}),
        'description': (check_string_attribute, {'min_length': 0}),
        'name': (check_string_attribute, {'min_length': 0}),
        'timespan_from': (check_int_attribute, {}),
        'timespan_to': (check_int_attribute, {})
    }

    def _get_controller_class(self):
        return DatasetAsyncController

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
                validation_func, extras = validation_data
                param_value = data.get(param_name)
                if param_value is not None:
                    validation_func(param_name, param_value, **extras)
                    if isinstance(param_value, list):
                        for v in param_value:
                            check_string_attribute(f'{param_name} values', v)
            check_timespan_range(data)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def get(self, organization_id, dataset_id, **kwargs):
        """
        ---
        description: |
            Get dataset by ID
            Required permission: INFO_ORGANIZATION
        tags: [profiling_datasets]
        summary: Get dataset
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: dataset_id
            in: path
            description: Dataset id
            required: true
            type: string
        responses:
            200:
                description: Dataset object
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Unique dataset id
                        path:
                            type: string
                            description: Dataset path
                        name:
                            type: string
                            description: Dataset name
                        description:
                            type: string
                            description: Dataset description
                        labels:
                            type: array
                            description: |
                                List of labels related to leaderboards
                                evaluation protocols
                            items:
                                type: string
                        created_at:
                            type: integer
                            description: Creation timestamp (service field)
                        deleted_at:
                            type: integer
                            description: Deleted timestamp (service field)
                        timespan_from:
                            type: integer
                            description: Timespan from timestamp
                        timespan_to:
                            type: integer
                            description: Timespan to timestamp
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
        res = await run_task(self.controller.get, dataset_id, token)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def patch(self, organization_id, dataset_id, **kwargs):
        """
        ---
        description: |
            Update dataset
            Required permission: EDIT_PARTNER
        tags: [profiling_datasets]
        summary: Update dataset
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: dataset_id
            in: path
            description: Dataset id
            required: True
            type: string
        -   in: body
            name: body
            description: Body with updated parameters
            required: True
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: Dataset name
                        example: Test
                    description:
                        type: string
                        description: Dataset extended info
                        example: Some description
                    labels:
                        type: array
                        description: |
                            List of labels related to leaderboards
                            evaluation protocols
                        example:
                        -   demo
                        -   test
                    timespan_from:
                        type: integer
                        description: Timespan from timestamp
                        required: false
                        example: 1698740386
                    timespan_to:
                        type: integer
                        description: Timespan to timestamp
                        required: false
                        example: 1698740386
        responses:
            200:
                description: Dataset object
                schema:
                    type: object
                    example:
                        id: 1519de9a-9430-41d9-9af9-772adb36b051
                        path: s3://ml-bucket/dataset
                        name: Test
                        description: Test ML dataset
                        labels:
                        - test
                        - demo
                        created_at: 1697175347
                        deleted_at: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer value
                    - OE0385: Argument should be a list
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
        data = self._request_body()
        self._validate_params(**data)
        res = await run_task(self.controller.edit,
                             dataset_id, token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, organization_id, dataset_id, **kwargs):
        """
        ---
        description: |
            Deletes dataset with specified id
            Required permission: EDIT_PARTNER
        tags: [profiling_datasets]
        summary: Delete dataset
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: dataset_id
            in: path
            description: Dataset id
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
                    - OE0002: Object not found
            409:
                description: |
                    Conflict:
                    - OE0555: Dataset with id used in leaderboard(s)
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        await run_task(self.controller.delete,
                       dataset_id, token)
        self.set_status(204)
