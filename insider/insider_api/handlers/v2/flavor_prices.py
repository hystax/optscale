import json
import logging

from insider_api.controllers.flavor_price import FlavorPriceAsyncController
from insider_api.handlers.v2.base import SecretHandler
from insider_api.utils import ModelEncoder

from optscale_exceptions.common_exc import (
    WrongArgumentsException, UnauthorizedException, NotFoundException)
from optscale_exceptions.http_exc import OptHTTPError


LOG = logging.getLogger(__name__)


class FlavorPricesCollectionHandler(SecretHandler):
    def _get_controller_class(self):
        return FlavorPriceAsyncController

    async def get(self, cloud_type):
        """
        ---
        tags: [flavor_prices]
        summary: List flavor prices
        description: |
            List flavor prices
            Required permission: cluster secret
        parameters:
        -   in: path
            name: cloud_type
            description: cloud type
            required: true
            type: string
        -   in: query
            name: region
            description: region name
            required: true
            type: string
        -   in: query
            name: flavor
            description: flavor
            required: true
            type: string
        -   in: query
            name: os_type
            description: OS type
            required: true
            type: string
        -   in: query
            name: preinstalled
            description: pre-installed software (for AWS only)
            required: false
            type: string
        -   in: query
            name: quantity
            description: quantity (for Alibaba only)
            required: false
            type: string
        -   in: query
            name: billing_method
            description: billing method (for Alibaba only)
            required: false
            type: string
            enum: ['subscription', 'pay_as_you_go']
        -   in: query
            name: currency
            description: currency
            required: false
            type: string
        responses:
            200:
                description: suitable flavor prices
                schema:
                    type: object
                    properties:
                        prices:
                            type: array
                            items:
                                type: object
                                properties:
                                    flavor: {type: string, description:
                                        "Flavor name"}
                                    region: {type: string, description:
                                        "Region"}
                                    price: {type: integer, description:
                                        "Flavor price"}
                                    operating_system: {type: string,
                                        description: "OS type"}
                                    price_unit: {type: string, description:
                                        "Pricing period"}
                                    currency: {type: string, description:
                                        "Price currency"}
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
        url_params = {
            'region': self.get_arg('region', str),
            'flavor': self.get_arg('flavor', str),
            'os_type': self.get_arg('os_type', str),
            'preinstalled': self.get_arg('preinstalled', str),
            'quantity': self.get_arg('quantity', int),
            'billing_method': self.get_arg('billing_method', str),
            'currency': self.get_arg('currency', str, default='USD')
        }
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
            {'prices': res}, cls=ModelEncoder))
