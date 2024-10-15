import json
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.controllers.profiling.artifact import (
    ArtifactAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.profiling.base import (
    ProfilingHandler)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute, check_dict_attribute,
    check_int_attribute)


MAX_MONGO_INT = 2**63 - 1
MAX_TIMESTAMP = 2**31 - 1


def _validate_params(data, is_new=True):
    allowed_args = ['name', 'description', 'tags', 'path']
    if is_new:
        allowed_args.append('run_id')
    unexpected_args = list(filter(lambda x: x not in allowed_args, data))
    if unexpected_args:
        message = ', '.join(unexpected_args)
        raise OptHTTPError(400, Err.OE0212, [message])
    try:
        run_id = data.get('run_id')
        path = data.get('path')
        if is_new:
            check_string_attribute('run_id', run_id)
            check_string_attribute('path', path)
        elif run_id:
            raise WrongArgumentsException(Err.OE0212, ['run_id'])
        else:
            check_string_attribute('path', path, allow_empty=True)
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


class ArtifactsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                      BaseAuthHandler, ProfilingHandler):
    def _get_controller_class(self):
        return ArtifactAsyncController

    def _validate_params(self, **data):
        _validate_params(data)

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create artifact
            Required permission: EDIT_PARTNER
        tags: [profiling_artifacts]
        summary: Create artifact
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Artifact parameters
            required: true
            schema:
                type: object
                properties:
                    path:
                        type: string
                        description: Artifact path link
                    run_id:
                        type: string
                        description: id of run generated this artifact
                    name:
                        type: string
                        description: Artifact name
                    description:
                        type: string
                        description: Artifact description
                    tags:
                        type: object
                        description: Artifact tags
                        example:
                            env: staging
        responses:
            201:
                description: Returns created artifact
                schema:
                    type: object
                    example:
                        id: ea7a7532-cf56-46c6-8cbb-a07652c7e656
                        name: My artifact
                        description: Example Artifact
                        path: s3://my/artifact.jpg
                        run:
                            id: f5f0948d-8ccf-49fc-8e4e-2bef1ad19a64
                            name: best_run
                            number: 1
                            task_id: 49c16dab-baec-486d-b5cf-1541da07276f
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

    def _get_query_params(self):
        params = {}
        max_values = {
            'created_at_lt': MAX_TIMESTAMP,
            'created_at_gt': MAX_TIMESTAMP,
            'limit': MAX_MONGO_INT,
            'start_from': MAX_MONGO_INT
        }
        try:
            for param in ['run_id', 'task_id']:
                values = self.get_arg(param, str, [], repeated=True)
                if values:
                    params[param] = values
            for param in max_values.keys():
                value = self.get_arg(param, int, None)
                if value:
                    check_int_attribute(param, value,
                                        max_length=max_values[param])
                    params[param] = value
            text_like = self.get_arg('text_like', str, None)
            if text_like:
                params['text_like'] = text_like
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        return params

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get list of artifacts
            Required permission: INFO_ORGANIZATION
        tags: [profiling_artifacts]
        summary: List of organization artifacts
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: run_id
            description: Ids of runs that generated artifacts
            required: false
            type: array
            in: query
            items:
                type: string
            collectionFormat: multi
        -   name: task_id
            description: Ids of tasks that generated artifacts
            required: false
            type: array
            in: query
            items:
                type: string
            collectionFormat: multi
        -   name: created_at_gt
            in: query
            description: minimum created_at timestamp filter value
            required: false
            type: integer
        -   name: created_at_lt
            in: query
            description: maximum created_at timestamp filter value
            required: false
            type: integer
        -   name: text_like
            in: query
            description: |
                filter values by substring in path, name, description or tags
            required: false
            type: string
        -   name: limit
            in: query
            description: limit artifacts to return
            required: false
            type: integer
        -   name: start_from
            in: query
            description: return artifacts starting from this number
            required: false
            type: integer
        responses:
            200:
                description: Organization artifacts list
                schema:
                    type: object
                    properties:
                        artifacts:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: |
                                            Unique artifact id
                                    name:
                                        type: string
                                        description: Artifact name
                                    description:
                                        type: string
                                        description: Artifact description
                                    path:
                                        type: string
                                        description: Artifact key
                                    tags:
                                        type: object
                                        description: Artifact tags
                                        example:
                                            env: staging
                                    run:
                                        type: object
                                        description: Artifact run
                                        example:
                                            id: f5f0948d-8ccf-49fc-8e4e-2bef1ad19a64
                                            name: best_run
                                            number: 1
                                            task_id: 49c16dab-baec-486d-b5cf-1541da07276f
                        count:
                            type: integer
                            description: Filtered artifacts count
                        total_count:
                            type: integer
                            description: Total artifacts count
                        start_from:
                            type: integer
                            description: Start artifact number
                        limit:
                            type: integer
                            description: Start artifact number
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
        params = self._get_query_params()
        res = await run_task(self.controller.list, token, **params)
        self.write(json.dumps(res, cls=ModelEncoder))


class ArtifactsAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                                ProfilingHandler):

    def _get_controller_class(self):
        return ArtifactAsyncController

    def _validate_params(self, **data):
        _validate_params(data, is_new=False)

    async def get(self, organization_id, artifact_id, **kwargs):
        """
        ---
        description: |
            Get artifact info by ID
            Required permission: INFO_ORGANIZATION
        tags: [profiling_artifacts]
        summary: Get artifact
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: artifact_id
            in: path
            description: Artifact id
            required: true
            type: string
        responses:
            200:
                description: Organization artifact info
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: |
                                Unique organization artifact id
                        name:
                            type: string
                            description: Artifact name
                        path:
                            type: string
                            description: Artifact path
                        description:
                            type: string
                            description: Artifact description
                        created_at:
                            type: integer
                            description: Created at timestamp
                        run:
                            type: object
                            description: Artifact run
                            example:
                                id: f5f0948d-8ccf-49fc-8e4e-2bef1ad19a64
                                name: best_run
                                number: 1
                                task_id: 49c16dab-baec-486d-b5cf-1541da07276f
                        tags:
                            type: object
                            description: Artifact tags
                            example:
                                key: value
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
        res = await run_task(self.controller.get, artifact_id, token)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def patch(self, organization_id, artifact_id, **kwargs):
        """
        ---
        description: |
            Update artifact
            Required permission: EDIT_PARTNER
        tags: [profiling_artifacts]
        summary: Update artifact
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: artifact_id
            in: path
            description: Artifact id
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
                        description: Artifact name
                    description:
                        type: string
                        description: Artifact description
                    path:
                        type: string
                        description: Artifact file path link
                    tags:
                        type: object
                        description: Artifact tags
                        example:
                            key: value
        responses:
            200:
                description: Updated artifact object
                schema:
                    type: object
                    example:
                        id: 6e278b91-25f7-4baf-89ba-b43e92539781
                        name: my artifact
                        path: s3://my/artifact.jpg
                        description: Artifact description
                        created_at: 1709087249
                        run:
                            id: f5f0948d-8ccf-49fc-8e4e-2bef1ad19a64
                            name: best_run
                            task_id: 49c16dab-baec-486d-b5cf-1541da07276f
                            number: 1
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
        res = await run_task(self.controller.edit, artifact_id, token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, organization_id, artifact_id, **kwargs):
        """
        ---
        description: |
            Deletes artifact with specified id
            Required permission: EDIT_PARTNER
        tags: [profiling_artifacts]
        summary: Delete artifact
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: artifact_id
            in: path
            description: Artifact id
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
        await run_task(self.controller.delete, artifact_id, token)
        self.set_status(204)
