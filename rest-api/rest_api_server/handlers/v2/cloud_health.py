import json

from optscale_exceptions.common_exc import NotFoundException
from optscale_exceptions.http_exc import OptHTTPError
from rest_api_server.controllers.cloud_health import CloudHealthAsyncController
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import (run_task, ModelEncoder)


class CloudHealthAsyncHandler(BaseAsyncItemHandler, BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return CloudHealthAsyncController

    async def get(self, organization_id):
        """
        ---
        description: |
            Get health scores for cloud regions.
            Only AWS is supported and AWS regions returned even if there are no
            AWS clouds / expenses in AWS cloud.
            Required permission: INFO_ORGANIZATION
        tags: [cloud_health]
        summary: Get health scores for cloud regions
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
            required: true
            type: string
        responses:
            200:
                description: Cloud health
                schema:
                    type: object
                    properties:
                        best_overall_region:
                            type: string
                            description: >
                                name of the region with best overall score
                            example: us-east-1
                        runner_up_region:
                            type: string
                            description: >
                                name of the region with second best
                                overall score
                            example: us-east-2
                        cheapest_top_five_region:
                            type: string
                            description: >
                                name of the region with best price score out of
                                top 5 overall regions
                            example: us-east-1
                        best_az:
                            type: string
                            description: >
                                name of the best AZ
                                out of best_overall_region AZs
                            example: us-east-1a
                        best_az_for_spot:
                            type: string
                            description: >
                                name of the best AZ
                                out of cheapest_top_five_region AZs
                            example: us-east-1a
                        max_score:
                            type: number
                            description: max possible score
                            example: 10.0
                        region_scores:
                            type: array
                            items:
                                type: object
                                properties:
                                    region:
                                        type: string
                                        description: region name
                                    cloud_type:
                                        type: string
                                        description: type of the cloud
                                    overall:
                                        type: number
                                        description: overall score
                                    proximity:
                                        type: number
                                        description: proximity score
                                    network_latency:
                                        type: number
                                        description: network_latency score
                                    price:
                                        type: number
                                        description: price score
                                    capacity_avg:
                                        type: number
                                        description: >
                                            average capacity score out of
                                            all region AZs
                                    capacity_scores:
                                        type: object
                                        description: AZ name <-> AZ score map
                                    performance_avg:
                                        type: number
                                        description: >
                                            average performance score out of
                                            all region AZs
                                    performance_scores:
                                        type: object
                                        description: AZ name <-> AZ score map
                            example:
                            -   region: us-east-1
                                cloud_type: aws_cnr
                                overall: 10.0
                                proximity: 10.0
                                network_latency: 10.0
                                price: 10.0
                                capacity_avg: 10.0
                                capacity_scores:
                                    us-east-1a: 10.0
                                    us-east-1b: 10.0
                                performance_avg: 10.0
                                performance_scores:
                                    us-east-1a: 10.0
                                    us-east-1b: 10.0
                            -   region: us-east-2
                                cloud_type: aws_cnr
                                overall: 9.0
                                proximity: 9.0
                                network_latency: 9.0
                                price: 9.0
                                capacity_avg: 9.0
                                capacity_scores:
                                    us-east-1a: 8.0
                                    us-east-1b: 10.0
                                performance_avg: 9.0
                                performance_scores:
                                    us-east-1a: 8.0
                                    us-east-1b: 10.0
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
            424:
                description: |
                    Failed dependency:
                    - OE0458: Cloud health calculation hasn't been completed yet
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        try:
            org = await self._get_item(organization_id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)

        res = await run_task(self.controller.get_cloud_health, org.id)
        self.write(json.dumps(res, cls=ModelEncoder))
