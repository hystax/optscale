import json
from rest_api_server.handlers.v2.ri_sp_usage_breakdowns import RiSpUsageAsyncHandler
from rest_api_server.controllers.ri_sp_expenses_breakdown import RiSpExpensesAsyncController
from rest_api_server.utils import (run_task, ModelEncoder)


class RiSpExpensesAsyncHandler(RiSpUsageAsyncHandler):
    def _get_controller_class(self):
        return RiSpExpensesAsyncController

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get Reserved Instances and Savings Plans expenses breakdown
            Required permission: INFO_ORGANIZATION
        tags: [ri_sp_breakdowns]
        summary: Get Reserved Instances and Savings Plans expenses breakdown
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: start_date
            in: query
            description: Start date (timestamp in seconds)
            required: true
            type: integer
        -   name: end_date
            in: query
            description: End date (timestamp in seconds)
            required: true
            type: integer
        -   name: cloud_account_id
            in: query
            description: Id of cloud account
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        responses:
            200:
                description: breakdown expenses data
                schema:
                    type: object
                    properties:
                        breakdown:
                            type: object
                            description: >
                                breakdown for RI/SP costs
                            properties:
                                breakdown_timestamp:
                                    type: array
                                    items:
                                        type: object
                                    description: >
                                        costs data for breakdown timestamp
                                    properties:
                                        cloud_account_id:
                                            type: string
                                            description: cloud account id
                                        cloud_account_type:
                                            type: string
                                            description: type of cloud account
                                            enum: ['aws_cnr']
                                        cloud_account_name:
                                            type: string
                                            description: cloud account name
                                        total:
                                            type: object
                                            description: |
                                                total cost of usage may be
                                                 covered by RI/SP
                                            properties:
                                                cost_with_offer:
                                                    type: number
                                                    description: |
                                                        current cost of usage
                                                cost_without_offer:
                                                    type: number
                                                    description: |
                                                        cost of usage may be
                                                         covered by RI/SP
                                        ri:
                                            type: object
                                            description: Reserved Instances costs
                                            properties:
                                                cost_with_offer:
                                                    type: number
                                                    description: |
                                                        current cost of
                                                        usage covered by RI
                                                cost_without_offer:
                                                    type: number
                                                    description: |
                                                        cost of usage covered by
                                                        RI by OnDemand prices
                                        sp:
                                            type: object
                                            description: Savings Plan costs
                                            properties:
                                                cost_with_offer:
                                                    type: number
                                                    description: |
                                                        current cost of usage
                                                        covered by RI
                                                cost_without_offer:
                                                    type: number
                                                    description: |
                                                        cost of usage covered by
                                                        SP by OnDemand prices
                    example:
                        breakdown:
                            1681716160:
                                -   cloud_account_id: "72771690-619f-4a0c-8652-7bdf3ae48ab7"
                                    cloud_account_type: "aws_cnr"
                                    cloud_account_name: "My cloud account"
                                    total:
                                        cost_with_offer: 10.0
                                        cost_without_offer: 12.0
                                    ri:
                                        cost_with_offer: 4.0
                                        cost_without_offer: 7.0
                                    sp:
                                        cost_with_offer: 1.0
                                        cost_without_offer: 3.0
            424:
                description: |
                    Failed dependency
                    - OE0445: Organization doesn't have any cloud accounts connected
            404:
                description: |
                    Not found
                    - OE0002: Organization not found
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            400:
                description: |
                    Wrong arguments:
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer value
                    - OE0446: "end_date" should be greater than "start_date"
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        args = self.get_expense_arguments(filter_required=False)
        breakdown = await run_task(
            self.controller.get, organization_id, **args)
        self.write(json.dumps({'breakdown': breakdown}, cls=ModelEncoder))
