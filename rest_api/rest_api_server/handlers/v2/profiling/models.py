import json
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.controllers.profiling.model import (
    ModelAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.profiling.base import (
    ProfilingHandler)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute, check_dict_attribute)


def _validate_params(data, key_required=True):
    allowed_args = ['name', 'description', 'tags']
    if key_required:
        allowed_args.append('key')
    unexpected_args = list(filter(lambda x: x not in allowed_args, data))
    if unexpected_args:
        message = ', '.join(unexpected_args)
        raise OptHTTPError(400, Err.OE0212, [message])
    try:
        key = data.get('key')
        if key_required:
            check_string_attribute('key', key)
        else:
            check_string_attribute('key', key, allow_empty=True)
        for k in ['name', 'description']:
            value = data.get(k)
            check_string_attribute(k, value, allow_empty=True)
        description = data.get('description')
        if description:
            check_string_attribute('description', description,
                                   max_length=1000, allow_empty=True)
        tags = data.get('tags', {})
        if tags:
            check_dict_attribute('tags', tags, allow_empty=True)
    except WrongArgumentsException as exc:
        raise OptHTTPError.from_opt_exception(400, exc)


class ModelsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                   BaseAuthHandler, ProfilingHandler):
    def _get_controller_class(self):
        return ModelAsyncController

    def _validate_params(self, **data):
        _validate_params(data)

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create model
            Required permission: EDIT_PARTNER
        tags: [profiling_models]
        summary: Create model
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Model parameters
            required: true
            schema:
                type: object
                properties:
                    key:
                        type: string
                        description: Model key
                    name:
                        type: string
                        description: Model name
                    description:
                        type: string
                        description: Model description
                    tags:
                        type: object
                        description: Model tags
                        example:
                            env: staging
        responses:
            201:
                description: Returns created model
                schema:
                    type: object
                    example:
                        id: ea7a7532-cf56-46c6-8cbb-a07652c7e656
                        name: My model
                        description: Example Model
                        key: my_model
                        tags:
                            env: staging
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0216: Argument is not provided
                    - OE0344: tags should be a dictionary
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
            Get list of models
            Required permission: INFO_ORGANIZATION
        tags: [profiling_models]
        summary: List of organization models
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Organization models list
                schema:
                    type: object
                    properties:
                        models:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: |
                                            Unique organization model id
                                    name:
                                        type: string
                                        description: Model name
                                    description:
                                        type: string
                                        description: Model description
                                    key:
                                        type: string
                                        description: Model key
                                    tags:
                                        type: object
                                        description: Model tags
                                        example:
                                            env: staging
                                    last_version:
                                        type: object
                                        description: Last model version
                                        example:
                                            id: ea7a7532-cf56-46c6-8cbb-a07652c7e656
                                            version: "1"
                                            path: /path/to/model
                                            aliases:
                                                - winner
                                            run_id: 8407ab1d-134b-40a4-9509-16b0d92171d3
                                            model_id: 38155e21-9319-4557-9501-71600cb606ad
                                            deleted_at: 0
                                            created_at: 1710498201
                                    aliased_versions:
                                        type: array
                                        example:
                                            - id: ea7a7532-cf56-46c6-8cbb-a07652c7e656
                                              version: "1"
                                              path: /path/to/model
                                              aliases:
                                                  - winner
                                              run_id: 8407ab1d-134b-40a4-9509-16b0d92171d3
                                              model_id: 38155e21-9319-4557-9501-71600cb606ad
                                              deleted_at: 0
                                              created_at: 1710498201
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
        res = await run_task(self.controller.list, token)
        models_dict = {'models': res}
        self.write(json.dumps(models_dict, cls=ModelEncoder))


class ModelsAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                             ProfilingHandler):

    def _get_controller_class(self):
        return ModelAsyncController

    def _validate_params(self, **data):
        _validate_params(data, key_required=False)

    async def get(self, organization_id, model_id, **kwargs):
        """
        ---
        description: |
            Get model info by ID
            Required permission: INFO_ORGANIZATION
        tags: [profiling_models]
        summary: Get model
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
        responses:
            200:
                description: Organization model info
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: |
                                Unique organization model id
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
                            example:
                                key: value
                        versions:
                            type: object
                            description: versions details
                            properties:
                                version:
                                    type: object
                                    description: version
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
                                        path:
                                            type: string
                                            description: Model version path
                                        alias:
                                            type: string
                                            description: Model version alias
                                        tags:
                                            type: object
                                            description: Model version tags
                                    example:
                                        1.11-rc:
                                            id: 10b7df6e-e620-4b16-84cc-09ae3a91de25
                                            name: my run
                                            number: 7
                                            path: /path/to/model
                                            alias: winner
                                            tags:
                                                env: staging
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
        res = await run_task(self.controller.get, model_id, token)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def patch(self, organization_id, model_id, **kwargs):
        """
        ---
        description: |
            Update model
            Required permission: EDIT_PARTNER
        tags: [profiling_models]
        summary: Update model
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
        -   in: body
            name: body
            description: body with updated parameters
            required: True
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: Model name
                    description:
                        type: string
                        description: Model description
                    tags:
                        type: object
                        description: Model tags
                        example:
                            key: value
        responses:
            200:
                description: Updated model object
                schema:
                    type: object
                    example:
                        id: 6e278b91-25f7-4baf-89ba-b43e92539781
                        name: my model
                        key: my_model
                        description: Model description
                        created_at: 1709087249
                        tags:
                            env: staging
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
        res = await run_task(self.controller.edit, model_id, token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, organization_id, model_id, **kwargs):
        """
        ---
        description: |
            Deletes model with specified id
            Required permission: EDIT_PARTNER
        tags: [profiling_models]
        summary: Delete model
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
        await run_task(self.controller.delete, model_id, token)
        self.set_status(204)
