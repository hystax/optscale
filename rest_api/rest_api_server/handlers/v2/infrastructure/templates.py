import json

from rest_api.rest_api_server.controllers.infrastructure.template import (
    TemplateAsyncController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute,
    check_dict_attribute, check_list_attribute, check_float_attribute)
from rest_api.rest_api_server.handlers.v2.infrastructure.base import (
    InfrastructureHandler)

from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException


class TemplatesAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                      BaseAuthHandler,
                                      InfrastructureHandler):
    VALIDATION_MAP = {
        'tags': (check_dict_attribute, True),
        'hyperparameters': (check_dict_attribute, True),
        'application_ids': (check_list_attribute, True),
        'cloud_account_ids': (check_list_attribute, True),
        'region_ids': (check_list_attribute, True),
        'instance_types': (check_list_attribute, True),
        'budget': (check_float_attribute, True),
        'name': (check_string_attribute, True),
        'name_prefix': (check_string_attribute, True)
    }

    def _get_controller_class(self):
        return TemplateAsyncController

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
                elif isinstance(param_value, dict):
                    for k, v in param_value.items():
                        check_string_attribute(f'{param_name} key', k)
                        check_string_attribute(f'{param_name} value', v)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create runset template
            Required permission: EDIT_PARTNER
        tags: [infrastructure_templates]
        summary: Create runset template
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
                    name:
                        type: string
                        description: Template name
                        required: true
                        example: Some template
                    name_prefix:
                        type: string
                        description: Template name prefix
                        required: true
                        example: test_ml
                    budget:
                        type: number
                        description: |
                            Max budget of runset which will be created
                            from template
                        required: true
                        example: 100.5
                    tags:
                        type: object
                        description: Template tags
                        required: true
                        example:
                            template_name: test
                    hyperparameters:
                        type: object
                        description: Template hyperparameters definition
                        required: false
                        example:
                            Model URL: MODEL_URL
                            Dataset URL: DATASET_URL
                            Learning rate: LEARNING_RATE
                    cloud_account_ids:
                        type: array
                        description: list of template cloud accounts ids
                        required: true
                        example:
                        -   b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                        -   5c285343-274e-44c2-9b8b-c87359601fc4
                    application_ids:
                        type: array
                        description: list of template applications ids
                        required: true
                        example:
                        -   b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                        -   5c285343-274e-44c2-9b8b-c87359601fc4
                    instance_types:
                        type: array
                        description: list of template instance families names
                        required: true
                        example:
                        -   p4
                        -   p3
                    region_ids:
                        type: array
                        description: list of template regions ids
                        required: true
                        example:
                        -   us-east-1
                        -   us-west-1
        responses:
            201:
                description: Returns created template
                schema:
                    type: object
                    example:
                        name: Test project template
                        budget: 1234
                        name_prefix: test_prefix
                        tags:
                            template: test
                        hyperparameters:
                            Model URL: MODEL_URL
                            Dataset URL: DATASET_URL
                            Learning rate: LEARNING_RATE
                        id: 1519de9a-9430-41d9-9af9-772adb36b051
                        cloud_accounts:
                        -   id: a3857500-32d2-4f4a-8cdb-d0c8d0171955
                            name: creds
                            type: aws_cnr
                        applications:
                        -   id: 9b8a61c0-7ef4-4370-b28f-8d00e6a3a0a3
                            name: Test project
                        instance_types:
                        -   name: p4
                            cloud_type: aws_cnr
                        -   name: p3
                            cloud_type: aws_cnr
                        -   name: p2
                            cloud_type: aws_cnr
                        regions:
                        -   id: us-east-1
                            name: us-east-1
                            cloud_type: aws_cnr
                        -   id: us-west-1
                            name: us-west-1
                            cloud_type: aws_cnr
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0216: Argument is not provided
                    - OE0224: Value of argument should be between 0 and 2147483647
                    - OE0287: At least 1 parameter value is required
                    - OE0344: Argument should be a dictionary
                    - OE0385: Argument should be a list
                    - OE0466: Argument should be float
                    - OE0542: Instance types are unsupported on regions
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
                    - OE0149: Template with such name already exists
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        data = self._request_body()
        self._validate_params(**data)
        token = await self._get_infrastructure_token(organization_id)
        res = await run_task(
            self.controller.create, organization_id, token, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))


class TemplatesAsyncItemHandler(BaseAsyncItemHandler,
                                BaseAuthHandler,
                                InfrastructureHandler):
    VALIDATION_MAP = {
        'tags': (check_dict_attribute, False),
        'hyperparameters': (check_dict_attribute, False),
        'application_ids': (check_list_attribute, False),
        'cloud_account_ids': (check_list_attribute, False),
        'region_ids': (check_list_attribute, False),
        'instance_types': (check_list_attribute, False),
        'budget': (check_float_attribute, False),
        'name': (check_string_attribute, False),
        'name_prefix': (check_string_attribute, False)
    }

    def _get_controller_class(self):
        return TemplateAsyncController

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
                if param_value is None:
                    continue
                validation_func(param_name, param_value)
                if isinstance(param_value, list):
                    for v in param_value:
                        check_string_attribute(f'{param_name} values', v)
                elif isinstance(param_value, dict):
                    for k, v in param_value.items():
                        check_string_attribute(f'{param_name} key', k)
                        check_string_attribute(f'{param_name} value', v)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)

    async def get(self, organization_id, template_id, **kwargs):
        """
        ---
        description: |
            Get template by ID
            Required permission: INFO_ORGANIZATION
        tags: [infrastructure_templates]
        summary: Get template
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
                description: Template object
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Unique template id
                        name:
                            type: string
                            description: Template name
                        budget:
                            type: number
                            description: |
                                Max budget of runset which will be created
                                from template
                        name_prefix:
                            type: string
                            description: Template name prefix
                        tags:
                            type: object
                            description: Template tags
                        hyperparameters:
                            type: object
                            description: Template hyperparameters definition
                        cloud_accounts:
                            type: array
                            description: list of template cloud accounts info
                            items:
                                type: object
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
                        applications:
                            type: array
                            description: list of template applications info
                            items:
                                type: object
                            properties:
                                id:
                                    type: string
                                    description: Application id
                                name:
                                    type: string
                                    description: Application name
                        instance_types:
                            type: array
                            description: list of template instance families info
                            items:
                                type: object
                            properties:
                                name:
                                    type: string
                                    description: Instance type name
                                type:
                                    type: string
                                    description: Cloud type
                        regions:
                            type: array
                            description: list of template regions info
                            items:
                                type: object
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
                             template_id, token)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def patch(self, organization_id, template_id, **kwargs):
        """
        ---
        description: |
            Update runset template
            Required permission: EDIT_PARTNER
        tags: [infrastructure_templates]
        summary: Update runset template
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: template_id
            in: path
            description: Template id
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
                        description: Template name
                        example: Some template
                    name_prefix:
                        type: string
                        description: Template name prefix
                        example: test_ml
                    budget:
                        type: number
                        description: |
                            Max budget of runset which will be created
                            from template
                        example: 100.5
                    tags:
                        type: object
                        description: Template tags
                        example:
                            template_name: test
                    hyperparameters:
                        type: object
                        description: Template hyperparameters definition
                        example:
                            Model URL: MODEL_URL
                            Dataset URL: DATASET_URL
                            Learning rate: LEARNING_RATE
                    cloud_account_ids:
                        type: array
                        description: list of template cloud accounts ids
                        example:
                        -   b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                        -   5c285343-274e-44c2-9b8b-c87359601fc4
                    application_ids:
                        type: array
                        description: list of template applications ids
                        example:
                        -   b65f85f8-d2cb-4ea6-88ab-4a9f2a82ba20
                        -   5c285343-274e-44c2-9b8b-c87359601fc4
                    instance_types:
                        type: array
                        description: list of template instance families names
                        example:
                        -   p4
                        -   p3
                    region_ids:
                        type: array
                        description: list of template regions ids
                        example:
                        -   us-east-1
                        -   us-west-1
        responses:
            200:
                description: New application object
                schema:
                    type: object
                    example:
                        name: Test project template
                        budget: 1234
                        name_prefix: test_prefix
                        tags:
                            template: test
                        hyperparameters:
                            Model URL: MODEL_URL
                            Dataset URL: DATASET_URL
                            Learning rate: LEARNING_RATE
                        id: 1519de9a-9430-41d9-9af9-772adb36b051
                        cloud_accounts:
                        -   id: a3857500-32d2-4f4a-8cdb-d0c8d0171955
                            name: creds
                            type: aws_cnr
                        applications:
                        -   id: 9b8a61c0-7ef4-4370-b28f-8d00e6a3a0a3
                            name: Test project
                        instance_types:
                        -   name: p4
                            cloud_type: aws_cnr
                        -   name: p3
                            cloud_type: aws_cnr
                        -   name: p2
                            cloud_type: aws_cnr
                        regions:
                        -   id: us-east-1
                            name: us-east-1
                            cloud_type: aws_cnr
                        -   id: us-west-1
                            name: us-west-1
                            cloud_type: aws_cnr
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters in string
                    - OE0216: Argument is not provided
                    - OE0224: Value of argument should be between 0 and 2147483647
                    - OE0287: At least 1 parameter value is required
                    - OE0344: Argument should be a dictionary
                    - OE0385: Argument should be a list
                    - OE0466: Argument should be float
                    - OE0542: Instance types are unsupported on regions
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
                    - OE0149: Template with such name already exists
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_infrastructure_token(organization_id)
        data = self._request_body()
        self._validate_params(**data)
        res = await run_task(self.controller.edit,
                             organization_id, template_id, token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, organization_id, template_id, **kwargs):
        """
        ---
        description: |
            Deletes runset template with specified id
            Required permission: EDIT_PARTNER
        tags: [infrastructure_templates]
        summary: Delete runset template
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
                    - OE0537: Template can't be deleted because of existing runsets
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        token = await self._get_infrastructure_token(organization_id)
        await run_task(self.controller.delete,
                       template_id, token)
        self.set_status(204)


class TemplatesOverviewAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                              BaseAuthHandler,
                                              InfrastructureHandler):
    def _get_controller_class(self):
        return TemplateAsyncController

    async def post(self, organization_id, **url_params):
        self.raise405()

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get runset templates overview
            Required permission: INFO_ORGANIZATION
        tags: [infrastructure_templates]
        summary: Get runset templates overview
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Organization templates overview
                schema:
                    type: object
                    properties:
                        templates:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description:  Unique template id
                                    name:
                                        type: string
                                        description: Template name
                                    total_runs:
                                        type: integer
                                        description: |
                                            Template runsets runs count
                                    total_cost:
                                        type: number
                                        description: |
                                            Templates runsets runners cost
                                    last_runset_cost:
                                        type: number
                                        description: |
                                            Last template runset runners cost
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
        res = await run_task(self.controller.list_overview, organization_id, token)
        applications_dict = {'templates': res}
        self.write(json.dumps(applications_dict, cls=ModelEncoder))
