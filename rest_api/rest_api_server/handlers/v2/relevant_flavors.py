import json
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.utils import run_task, ModelEncoder
from rest_api.rest_api_server.controllers.relevant_flavor import (
    RelevantFlavorAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from tools.optscale_exceptions.http_exc import OptHTTPError

GLOBAL_REGIONS = ['ap', 'eu', 'ca', 'sa', 'us', 'af', 'me']
SUPPORTED_CLOUDS = ['aws_cnr', 'azure_cnr', 'nebius']


class RelevantFlaforsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                            BaseAuthHandler, BaseHandler):

    def _get_controller_class(self):
        return RelevantFlavorAsyncController

    def get_url_params(self):
        return {
            'cloud_types': self.get_arg(
                'cloud_type', str, SUPPORTED_CLOUDS, repeated=True),
            'min_cpu': self.get_arg('min_cpu', int),
            'max_cpu': self.get_arg('max_cpu', int),
            'min_ram': self.get_arg('min_ram', int),
            'max_ram': self.get_arg('max_ram', int),
            'region': self.get_arg('region', str),
            'preferred_currency': self.get_arg('preferred_currency', str)
        }

    @staticmethod
    def validate_parameters(params):
        cloud_types = params['cloud_types']
        for cloud_type in cloud_types:
            if cloud_type not in SUPPORTED_CLOUDS:
                raise OptHTTPError(400, Err.OE0436, [cloud_type])
        required_params = [('region', str)]
        optional_params = [
            ('min_cpu', int), ('max_cpu', int), ('min_ram', int),
            ('max_ram', int), ('preferred_currency', str)
        ]
        if not isinstance(params, dict):
            raise OptHTTPError(400, Err.OE0233, [])
        missing_required = [
            p for p, _ in required_params if params.get(p) is None
        ]
        if missing_required:
            message = ', '.join(missing_required)
            raise OptHTTPError(400, Err.OE0216, [message])
        all_params = required_params + optional_params
        for param, param_type in all_params:
            value = params.get(param)
            if value is not None and not isinstance(value, param_type):
                raise OptHTTPError(400, Err.OE0217, [param])
        region = params['region']
        if region not in GLOBAL_REGIONS:
            raise OptHTTPError(400, Err.OE0217, ['region'])
        for min_k, max_k in [
            ('min_cpu', 'max_cpu'), ('min_ram', 'max_ram')
        ]:
            min_v = params.get(min_k)
            max_v = params.get(max_k)
            if min_v is not None and max_v is not None and min_v > max_v:
                raise OptHTTPError(400, Err.OE0446, [max_k, min_k])

    async def get(self, organization_id):
        """
        ---
        tags: [relevant_flavors]
        summary: List of relevant flavors
        description: |
            List of relevant flavors with prices
            Required permission: cluster secret
        parameters:
        -   in: query
            name: cloud_type
            description: cloud type
            required: false
            type: string
        -   in: query
            name: min_cpu
            description: minimum flavor cpu
            required: false
            type: integer
        -   in: query
            name: max_cpu
            description: maximum flavor cpu
            required: false
            type: integer
        -   in: query
            name: min_ram
            description: minimum flavor ram
            required: false
            type: integer
        -   in: query
            name: max_ram
            description: maximum flavor ram
            required: false
            type: integer
        -   in: query
            name: region
            description: flavor region
            required: true
            type: string
        -   in: query
            name: preferred_currency
            description: preferred flavor currency
            required: true
            type: string
        responses:
            200:
                description: list of relevant flavors
                schema:
                    type: object
                    properties:
                        flavors:
                            type: array
                            items:
                                type: object
                                properties:
                                    cpu: {type: string, description:
                                        "cpu count"}
                                    ram: {type: string, description:
                                        "ram count in GiB"}
                                    cloud_type:
                                        type: object
                                        properties:
                                            name: {type: string, description:
                                                "flavor name"}
                                            cost: {type: string,
                                                description: "flavor cost per hour"}
                                            currency: {type: string, description:
                                                "price currency"}
                                            instance_family: {type: string, description:
                                                "flavor instance family name"}
                                            location: {type: string, description:
                                                "flavor location"}
            400:
                description: |
                    Wrong arguments:
                    - OE0002: Organization not found
                    - OE0233: Incorrect request body
                    - OE0217: Invalid parameter
                    - OE0216: Required argument is not provided
                    - OE0436: Type is not supported
                    - OE0435: Service call error
                    - OE0446: "min_param" should be greater than "max_param"
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
        security:
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)

        params = self.get_url_params()
        self.validate_parameters(params)
        flavors, errors = await run_task(
            self.controller.list, organization_id, **params)
        flavors = {'flavors': flavors, 'errors': errors}
        self.write(json.dumps(flavors, cls=ModelEncoder))

    async def post(self, organization_id, **url_params):
        self.raise405()
