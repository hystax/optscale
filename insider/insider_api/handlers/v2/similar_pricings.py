import json
import logging

from insider_api.controllers.similar_pricings import (
    SimilarPricingsAsyncController)
from insider_api.handlers.v2.base import SecretHandler
from insider_api.utils import ModelEncoder


from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            UnauthorizedException,
                                            NotFoundException)
from optscale_exceptions.http_exc import OptHTTPError


LOG = logging.getLogger(__name__)


class SimilarPricingsHandler(SecretHandler):
    def _get_controller_class(self):
        return SimilarPricingsAsyncController

    async def get(self, cloud_type, pricing_id):
        """
        ---
        tags: [similar_pricings]
        summary: Returns flavor price in other regions
        description: |
            Returns flavor price in other regions
            Required permission: cluster secret
        parameters:
        -   in: path
            name: cloud_type
            description: cloud type
            required: true
        -   in: path
            name: pricing_id
            description: pricing id (meterId for azure)
            required: true
        responses:
            200:
                description: list of similar flavor prices
                schema:
                    type: object
                    example:
                        similar_prices:
                            type: array
                            items:
                                type: object
                            example:
                                -   _id: 5ff4353cede95b2d9bdf3501
                                    effectiveStartDate: 2019-10-16T00:00:00Z
                                    isPrimaryMeterRegion: True
                                    retailPrice: 0.19
                                    meterId: 0001e46a-9285-5fa8-b48a-240e307a24f7
                                    currencyCode: USD
                                    created_at: 1608907516
                                    skuName: A3 Spot
                                    serviceFamily: Compute
                                    armRegionName: uknorth
                                    last_seen: 1609829032
                                    armSkuName: Standard_A3
                                    type: Consumption
                                    skuId: DZH318Z0BPVJ/018M
                                    tierMinimumUnits: 0.0
                                    productName: Virtual Machines A Series Windows
                                    serviceName: Virtual Machines
                                    productId: DZH318Z0BPVJ
                                    unitOfMeasure: 1 Hour
                                    meterName: A3 Spot
                                    location: UK North
                                    serviceId: DZH313Z7MMC8
                                    unitPrice: 0.19
                                -   _id: 5ff4353cede95b2d9bdf3502
                                    effectiveStartDate: 2021-01-01T00:00:00Z
                                    isPrimaryMeterRegion: True
                                    retailPrice: 0.043704,
                                    meterId: 001caea7-ff8a-5957-8480-7f1121cc1976
                                    currencyCode: USD
                                    created_at: 1608907516
                                    skuName: A3 Spot
                                    serviceFamily: Compute
                                    armRegionName: centralus
                                    last_seen: 1609829033
                                    armSkuName: Standard_A3
                                    type: Consumption
                                    skuId: DZH318Z0BPVJ/017Q
                                    tierMinimumUnits: 0.0
                                    productName: Virtual Machines A Series Windows
                                    serviceName: Virtual Machines
                                    productId: DZH318Z0BPVJ
                                    effectiveEndDate: 2020-12-31T23:59:00Z
                                    unitOfMeasure: 1 Hour
                                    meterName: A3 Spot
                                    location: US Central
                                    serviceId: DZH313Z7MMC8
                                    unitPrice: 0.043704
            400:
                description: |
                    Wrong arguments:
                    - OI0008: Invalid cloud_type / pricing_id
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
            res = await self.controller.get(
                cloud_type=cloud_type, pricing_id=pricing_id)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        self.set_status(200)
        self.write(json.dumps(
            {'similar_prices': res}, cls=ModelEncoder))
