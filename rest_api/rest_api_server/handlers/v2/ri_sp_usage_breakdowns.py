import json
from rest_api.rest_api_server.handlers.v2.expenses import FilteredExpensesBaseAsyncHandler
from rest_api.rest_api_server.controllers.ri_sp_usage_breakdown import RiSpUsageAsyncController
from rest_api.rest_api_server.utils import (run_task, ModelEncoder)


class RiSpUsageAsyncHandler(FilteredExpensesBaseAsyncHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.str_filters = []
        self.int_filters = ['start_date', 'end_date']
        self.list_filters = ['cloud_account_id']

    def _get_controller_class(self):
        return RiSpUsageAsyncController

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get RI/SP usage breakdown
            Required permission: INFO_ORGANIZATION
        tags: [ri_sp_breakdowns]
        summary: Get RI/SP usage breakdown
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
                description: Reserved Instances and Savings Plan usage data breakdown
                schema:
                    type: object
                    properties:
                        breakdown:
                            type: object
                            description: >
                                breakdown for RI/SP usage
                            properties:
                                breakdown_timestamp:
                                    type: array
                                    items:
                                        type: object
                                    description: >
                                        usage data for date
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
                                        total_usage_hrs:
                                            type: number
                                            description: total usage in hours
                                        ri_usage_hrs:
                                            type: number
                                            description: total usage covered by RI in hours
                                        sp_usage_hrs:
                                            type: number
                                            description: total usage covered by SP in hours
                    example:
                        breakdown:
                            1681716160:
                                -   cloud_account_id: "72771690-619f-4a0c-8652-7bdf3ae48ab7"
                                    cloud_account_type: "aws_cnr"
                                    cloud_account_name: "My cloud account"
                                    total_usage_hrs: 100
                                    ri_usage_hrs: 50
                                    sp_usage_hrs: 30
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
                    - OE0217: Invalid query parameter
                    - OE0216: Argument is not provided
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

    async def patch(self, *args, **kwargs):
        self.raise405()

    async def delete(self, *args, **kwargs):
        self.raise405()
