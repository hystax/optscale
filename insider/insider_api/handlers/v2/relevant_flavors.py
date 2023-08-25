import json
import logging

from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, UnauthorizedException, NotFoundException)
from tools.optscale_exceptions.http_exc import OptHTTPError

from insider.insider_api.controllers.relevant_flavor import (
    RelevantFlavorAsyncController)
from insider.insider_api.handlers.v2.base import SecretHandler
from insider.insider_api.utils import ModelEncoder
from insider.insider_api.exceptions import Err

LOG = logging.getLogger(__name__)
GLOBAL_REGIONS = ['ap', 'eu', 'ca', 'sa', 'us', 'af', 'me']


class RelevantFlavorCollectionHandler(SecretHandler):
    def _get_controller_class(self):
        return RelevantFlavorAsyncController

    def get_url_params(self):
        return {
            'min_cpu': self.get_arg('min_cpu', int),
            'max_cpu': self.get_arg('max_cpu', int),
            'min_ram': self.get_arg('min_ram', int),
            'max_ram': self.get_arg('max_ram', int),
            'region': self.get_arg('region', str),
            'preferred_currency': self.get_arg('preferred_currency', str)
        }

    @staticmethod
    def validate_parameters(params):
        required_params = [('region', str)]

        optional_params = [('min_cpu', int),
                           ('max_cpu', int),
                           ('min_ram', int),
                           ('max_ram', int),
                           ('preferred_currency', str)
                           ]
        if not isinstance(params, dict):
            raise OptHTTPError(400, Err.OI0004, [])
        missing_required = [
            p for p, _ in required_params if params.get(p) is None
        ]
        if missing_required:
            message = ', '.join(missing_required)
            raise OptHTTPError(400, Err.OI0011, [message])
        all_params = required_params + optional_params
        for param, param_type in all_params:
            value = params.get(param)
            if value is not None and not isinstance(value, param_type):
                raise OptHTTPError(400, Err.OI0008, [param])
        region = params['region']
        if region not in GLOBAL_REGIONS:
            raise OptHTTPError(400, Err.OI0012, [region])

    async def get(self, cloud_type):
        """
        ---
        tags: [relevant_flavors]
        summary: List of relevant flavors
        description: |
            List of relevant flavors with prices
            Required permission: cluster secret
        parameters:
        -   in: path
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
                        cloud_type:
                            type: array
                            items:
                                type: object
                                properties:
                                    name: {type: string, description:
                                        "flavor name"}
                                    cpu: {type: string, description:
                                        "cpu count"}
                                    memory: {type: string, description:
                                        "ram count in GiB"}
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
                    - OI0008: Invalid cloud_type
                    - OI0010: Cloud is not supported
                    - OI0011: Required argument is not provided
                    - OI0012: Region is not available
                    - OI0015: Operating system is not available
            401:
                description: |
                    Unauthorized:
                    - OI0007: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OI0005: Bad secret
        security:
        - secret: []
        """
        self.check_cluster_secret()
        url_params = self.get_url_params()
        self.validate_parameters(url_params)
        try:
            res = await self.controller.get(
                cloud_type=cloud_type, **url_params)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.set_status(200)
        self.write(json.dumps(
            {cloud_type: res}, cls=ModelEncoder))
