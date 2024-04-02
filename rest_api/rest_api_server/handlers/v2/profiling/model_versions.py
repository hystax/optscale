import json
from rest_api.rest_api_server.handlers.v2.profiling.base import (
    ProfilingHandler)
from rest_api.rest_api_server.controllers.profiling.model_version import (
    ModelVersionAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute, check_list_attribute,
    check_dict_attribute
)
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.exceptions import Err


class ModelVersionsAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                                    ProfilingHandler):
    def _get_controller_class(self):
        return ModelVersionAsyncController

    def _validate_params(self, **data):
        allowed_args = ['version', 'path', 'aliases', 'tags']
        unexpected_args = list(filter(lambda x: x not in allowed_args, data))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            for param in ['version', 'path']:
                check_string_attribute(param, data.get(param),
                                       allow_empty=True)
            check_list_attribute('aliases', data.get('aliases'),
                                 allow_empty=True)
            check_dict_attribute('tags', data.get('tags'),
                                 allow_empty=True)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def post(self, organization_id, model_id, run_id, **url_params):
        """
        ---
        description: |
            Create model version
            Required permission: EDIT_PARTNER
        tags: [profiling_model_versions]
        summary: Create model version
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: model_id
            in: path
            description: Model id
            required: true
            type: string
        -   name: run_id
            in: path
            description: Run id
            required: true
            type: string
        -   in: body
            name: body
            description: Model version parameters
            required: true
            schema:
                type: object
                properties:
                    version:
                        type: string
                        description: Model version
                    aliases:
                        type: array
                        description: Model version aliases
                        items:
                            type: string
                    path:
                        type: string
                        description: Model version path
                    tags:
                        type: object
                        description: Model version tags
                        example:
                            env: staging
        responses:
            201:
                description: Returns created model
                schema:
                    type: object
                    example:
                        id: ea7a7532-cf56-46c6-8cbb-a07652c7e656
                        version: "1"
                        path: /path/to/model
                        aliases:
                          - winner
                        run_id: 8407ab1d-134b-40a4-9509-16b0d92171d3
                        model_id: 38155e21-9319-4557-9501-71600cb606ad
                        tags:
                          env: staging
                        deleted_at: 0
                        created_at: 1710498201
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0216: Argument is not provided
                    - OE0344: tags should be a dictionary
                    - OE0385: alias should be a list
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
            409:
                description: |
                    Conflict:
                    - OE0534: Model with key already exists
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        data = self._request_body()
        self._validate_params(**data)
        token = await self._get_profiling_token(organization_id)
        res = await run_task(
            self.controller.create, model_id, run_id, token, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def patch(self, organization_id, model_id, run_id, **kwargs):
        """
        ---
        description: |
            Update model version
            Required permission: EDIT_PARTNER
        tags: [profiling_model_versions]
        summary: Update model version
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: model_id
            in: path
            description: Model id
            required: True
            type: string
        -   name: run_id
            in: path
            description: Run id
            required: True
            type: string
        -   in: body
            name: body
            description: body with updated parameters
            required: True
            schema:
                type: object
                properties:
                    version:
                        type: string
                        description: Model version
                    aliases:
                        type: array
                        description: Model version aliases
                        items:
                            type: string
                    path:
                        type: string
                        description: Model version path
                    tags:
                        type: object
                        description: Model version tags
                        example:
                            env: staging
        responses:
            200:
                description: Updated model object
                schema:
                    type: object
                    example:
                        id: ea7a7532-cf56-46c6-8cbb-a07652c7e656
                        version: "1"
                        path: /path/to/model
                        aliases:
                          - winner
                        tags:
                          env: staging
                        run_id: 8407ab1d-134b-40a4-9509-16b0d92171d3
                        model_id: 38155e21-9319-4557-9501-71600cb606ad
                        deleted_at: 0
                        created_at: 1710498201
            400:
                description: |
                    Wrong arguments:
                    - OE0177: Non unique parameters in get request
                    - OE0214: Argument should be a string
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0217: Invalid query parameter
                    - OE0233: Incorrect body received
                    - OE0344: tags should be a dictionary
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
        res = await run_task(
            self.controller.edit, model_id, run_id, token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, organization_id, model_id, run_id, **kwargs):
        """
        ---
        description: |
            Deletes model version by model and run
            Required permission: EDIT_PARTNER
        tags: [profiling_model_versions]
        summary: Delete model version
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: model_id
            in: path
            description: Model id
            required: true
            type: string
        -   name: run_id
            in: path
            description: Run id
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
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_profiling_token(organization_id)
        await run_task(self.controller.delete, model_id, run_id, token)
        self.set_status(204)

    async def get(self, organization_id, model_id, run_id, **kwargs):
        self.raise405()


class TaskModelVersionsAsyncItemHandler(
        BaseAsyncItemHandler, BaseAuthHandler, ProfilingHandler):
    def _get_controller_class(self):
        return ModelVersionAsyncController

    async def get(self, organization_id, task_id, **kwargs):
        """
        ---
        description: |
            Get model versions by task
            Required permission: INFO_ORGANIZATION
        tags: [profiling_models]
        summary: Get model versions by task
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
            200:
                description: Task models versions info
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Model version id
                        path:
                            type: string
                            description: Model version path
                        aliases:
                            type: array
                            description: Model version alias
                            items:
                                type: string
                        tags:
                            type: object
                            description: Model version tags
                            example:
                                env: staging
                        run:
                            type: object
                            description: Run info
                            properties:
                                id:
                                    type: string
                                    description: Run id
                                name:
                                    type: string
                                    description: Run name
                                number:
                                    type: string
                                    description: Run number
                        model:
                            type: object
                            description: Model info
                            properties:
                                name:
                                    type: string
                                    description: Model name
                                key:
                                    type: string
                                    description: Model key
                                description:
                                    type: string
                                    description: Model description
                                created_at:
                                    type: integer
                                    description: Created at timestamp
                                tags:
                                    type: object
                                    description: Model tags
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
        res = await run_task(self.controller.get_versions_by_task,
                             task_id, token)
        self.write(json.dumps({'model_versions': res}, cls=ModelEncoder))
