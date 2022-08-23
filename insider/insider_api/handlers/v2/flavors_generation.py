import json
import logging
from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            UnauthorizedException,
                                            NotFoundException)
from optscale_exceptions.http_exc import OptHTTPError

from insider_api.controllers.flavor_generation import (
    FlavorGenerationAsyncController)
from insider_api.exceptions import Err
from insider_api.handlers.v2.base import SecretHandler
from insider_api.utils import ModelEncoder

LOG = logging.getLogger(__name__)


class FlavorsGenerationHandler(SecretHandler):
    def _get_controller_class(self):
        return FlavorGenerationAsyncController

    @staticmethod
    def validate_parameters(params):
        required_params = [('cloud_type', str),
                           ('region', str),
                           ('current_flavor', str)]

        optional_params = [('os_type', str),
                           ('preinstalled', str),
                           ('meter_id', str)]
        supported_cloud_types = ['aws_cnr', 'azure_cnr', 'alibaba_cnr']

        if not isinstance(params, dict):
            raise OptHTTPError(400, Err.OI0004, [])

        missing_required = [
            p for p, _ in required_params if params.get(p) is None
        ]
        if missing_required:
            message = ', '.join(missing_required)
            raise OptHTTPError(400, Err.OI0011, [message])

        cloud_type = params.get('cloud_type')
        if cloud_type not in supported_cloud_types:
            raise OptHTTPError(400, Err.OI0010, [cloud_type])

        meter_id = params.get('meter_id')
        if meter_id and cloud_type != 'azure_cnr':
            raise OptHTTPError(400, Err.OI0016, [cloud_type, 'meter_id'])

        preinstalled = params.get('preinstalled')
        if preinstalled and cloud_type != 'aws_cnr':
            raise OptHTTPError(400, Err.OI0016, [cloud_type, 'preinstalled'])

        all_params = required_params + optional_params
        for param, param_type in all_params:
            value = params.get(param)
            if value is not None and not isinstance(value, param_type):
                raise OptHTTPError(400, Err.OI0008, [param])

    async def post(self, **kwargs):
        """
        ---
        tags: [flavors_generation]
        summary: Returns newest flavor generation
        description: |
            Returns newest flavor generation
            Required permission: cluster secret
        parameters:
        -   in: body
            name: body
            description: Flavor generation search parameters
            required: true
            schema:
                type: object
                required: [cloud_type, resource_type, region, current_flavor]
                properties:
                    cloud_type: {type: string,
                        description: "cloud type (aws_cnr, azure_cnr,
                        alibaba_cnr)"}
                    region: {type: string,
                        description: "region name"}
                    current_flavor: {type: object,
                        description: "flavor that used"}
                    os_type: {type: string, enum: [Linux, Windows],
                       description: "The price for the flavor is calculated
                       for this os (AWS only), default - Linux"}
                    preinstalled: {type: string,
                       enum: [NA, SQL Web, SQL Std, SQL Ent],
                       description: "The price for flavor takes into account
                       this pre-installed software, default - NA (AWS only)"}
                    meter_id: {type: string,
                        description: "Pricing meter id (Azure only)"}
        responses:
            200:
                description: suitable flavor info
                schema:
                    type: object
                    example:
                        proposed_flavor: c5.medium
                        proposed_daily_price: 0.05
            400:
                description: |
                    Wrong arguments:
                    - OI0008: Invalid cloud_type / pricing_id
                    - OI0010: Cloud is not supported
                    - OI0011: Required argument is not provided
                    - OI0012: Region is not available
                    - OI0013: Resource type is not supported for cloud
                    - OI0016: Cloud does not support parameter
            404:
                description: |
                    Not Found:
                    - OI0009: Discovery not found
            401:
                description: |
                    Unauthorized:
                    - OI0007: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OI0005: Bad secret
                    - OI0017: Unexpected response from cloud
        security:
        - secret: []
        """
        self.check_cluster_secret()
        params = self._request_body()
        LOG.info('Received flavor generation search parameters: %s', params)
        self.validate_parameters(params)
        try:
            res = await self.controller.find_flavor_generation(
                                 **params)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        self.set_status(200)
        self.write(json.dumps(res, cls=ModelEncoder))
