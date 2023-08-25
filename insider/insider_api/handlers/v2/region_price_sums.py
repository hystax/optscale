import json
import logging

from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  UnauthorizedException,
                                                  NotFoundException)
from tools.optscale_exceptions.http_exc import OptHTTPError

from insider.insider_api.controllers.region_price_sums import (
    RegionPriceSumsAsyncController)
from insider.insider_api.handlers.v2.base import SecretHandler
from insider.insider_api.utils import ModelEncoder


LOG = logging.getLogger(__name__)


class RegionPriceSumsHandler(SecretHandler):
    def _get_controller_class(self):
        return RegionPriceSumsAsyncController

    async def get(self, cloud_type):
        """
        ---
        tags: [region_price_sums]
        summary: Returns regions price sums of 10 selected flavors
        description: |
            Returns regions price sums of 10 selected flavors
            Required permission: cluster secret
        parameters:
        -   in: path
            name: cloud_type
            description: cloud type
            required: true
        responses:
            200:
                description: list of similar flavor prices
                schema:
                    type: object
                    example:
                        price_sums:
                            type: object
                            example:
                                francecentral: 6.918
                                southeastasia: 6.7010000000000005
                                westindia: 6.896999999999999
                                ukwest: 6.805
                                norwayeast: 7.102
                                uaecentral: 8.040000000000001
                                koreasouth: 6.23
                                southcentralus: 6.1419999999999995
                                westus2: 5.382
                                northcentralus: 5.814
                                australiacentral: 6.830000000000001
                                germanywestcentral: 6.310999999999999
                                japanwest: 7.248000000000001
                                canadaeast: 6.156
                                northeurope: 6.077
                                westeurope: 6.3740000000000006
                                koreacentral: 6.774999999999999
                                germanynorth: 7.7909999999999995
                                eastus: 5.705
                                westus: 6.313999999999999
                                australiasoutheast: 6.961
                                westcentralus: 6.120999999999999
                                centralus: 6.342
                                southindia: 7.0489999999999995
                                eastus2: 5.606
                                norwaywest: 8.901
                                uaenorth: 6.495
                                brazilsoutheast: 11.193999999999999
                                southafricanorth: 7.045
                                switzerlandwest: 9.511
                                japaneast: 7.151
                                australiacentral2: 6.830000000000001
                                canadacentral: 6.1499999999999995
                                centralindia: 6.265000000000001
                                francesouth: 9.1691
                                brazilsouth: 9.022
                                southafricawest: 8.537749999999999
                                switzerlandnorth: 7.570999999999999
                                uksouth: 6.896999999999999
                                australiaeast: 6.830000000000001
                                eastasia: 7.492999999999999
            400:
                description: |
                    Wrong arguments:
                    - OI0008: Invalid cloud_type
                    - OI0010: Cloud is not supported
                    - OI0011: Required argument is not provided
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
        security:
        - secret: []
        """
        self.check_cluster_secret()
        try:
            res = await self.controller.get(cloud_type=cloud_type)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        self.set_status(200)
        self.write(json.dumps(
            {'price_sums': res}, cls=ModelEncoder))
