import json
import logging

from insider_api.controllers.instance import InstanceAsyncController
from insider_api.exceptions import Err
from insider_api.handlers.v2.base import SecretHandler
from insider_api.utils import ModelEncoder

from optscale_exceptions.common_exc import WrongArgumentsException
from optscale_exceptions.http_exc import OptHTTPError


LOG = logging.getLogger(__name__)


class ReservedInstancesOfferingsHandler(SecretHandler):
    def _get_controller_class(self):
        return InstanceAsyncController

    @staticmethod
    def validate_parameters(params):
        required_params = [('cloud_type', str),
                           ('product_description', str),
                           ('tenancy', str),
                           ('flavor', str),
                           ('min_duration', int),
                           ('max_duration', int),
                           ('include_marketplace', bool)]

        if not isinstance(params, dict):
            raise OptHTTPError(400, Err.OI0004, [])
        missing_required = [
            p for p, _ in required_params if params.get(p) is None
        ]
        if missing_required:
            message = ', '.join(missing_required)
            raise OptHTTPError(400, Err.OI0011, [message])

        unexpected_params = params.copy()
        for param, param_type in required_params:
            value = params.get(param)
            unexpected_params.pop(param)
            if value is not None and not isinstance(value, param_type):
                raise OptHTTPError(400, Err.OI0008, [param])

        if unexpected_params:
            message = ', '.join(list(unexpected_params.keys()))
            raise OptHTTPError(400, Err.OI0014, [message])

    async def post(self, **kwargs):
        """
        ---
        tags: [instances]
        summary: Returns suitable reserved instances offering
        description: |
            Returns suitable reserved instances offering
            Required permission: cluster secret
        parameters:
        -   in: body
            name: body
            description: Reserved instances offering search parameters
            required: true
            schema:
                type: object
                required: [product_description, tenancy, flavor, min_duration, max_duration, include_marketplace]
                properties:
                    cloud_type: {type: string,
                        description: "cloud type (aws_cnr)"}
                    product_description: {type: string,
                        description: "product description"}
                    tenancy: {type: string,
                        description: "tenancy"}
                    flavor: {type: string,
                        description: "flavor"}
                    min_duration: {type: integer,
                        description: "min_duration for reserved instance"}
                    max_duration: {type: integer,
                        description: "max_duration"}
                    include_marketplace: {type: boolean,
                       description: "should reserved instance be included in
                       marketplace"}
        responses:
            200:
                description: suitable reserved instance offering info
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            scope: {type: string,
                                description: "Region"}
                            offering_class: {type: string,
                                description: "convertible"}
                            offering_type: {type: string,
                                description: "No Upfront"}
                            fixed_price: {type: integer,
                                description: "0.05"}
                            recurring_charges:
                                type: array
                                items:
                                    type: object
                                    properties:
                                        Amount: {type: integer,
                                            description: "0.1865"}
                                        Frequency: {type: string,
                                            description: "Hourly"}
            400:
                description: |
                    Wrong arguments:
                    - OI0004: Incorrect request body received
                    - OI0008: Invalid params
                    - OI0010: Cloud is not supported
                    - OI0011: Required argument is not provided
                    - OI0014: Unexpected parameters:
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
        LOG.info('Received reserved instances search parameters: %s', params)
        self.validate_parameters(params)
        try:
            res = await self.controller.find_reserved_instances(**params)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        self.set_status(200)
        self.write(json.dumps(res, cls=ModelEncoder))
