import json
from rest_api.rest_api_server.handlers.v2.expenses import (
    FilteredExpensesBaseAsyncHandler)
from rest_api.rest_api_server.controllers.ri_group_breakdown import (
    RiGroupBreakdownAsyncController)
from rest_api.rest_api_server.utils import (run_task, ModelEncoder)


class RiGroupBreakdownAsyncHandler(FilteredExpensesBaseAsyncHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.str_filters = []
        self.int_filters = ['start_date', 'end_date']
        self.list_filters = ['cloud_account_id']

    def _get_controller_class(self):
        return RiGroupBreakdownAsyncController

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get RI group breakdown
            Required permission: INFO_ORGANIZATION
        tags: [ri_sp_breakdowns]
        summary: Get RI usage breakdown
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
                description: Uncovered usage data breakdown
                schema:
                    type: object
                    properties:
                        breakdown:
                            type: object
                            description: >
                                breakdown for RI usage
                            properties:
                                breakdown_timestamp:
                                    type: array
                                    items:
                                        type: object
                                    description: >
                                        usage data for date
                                    properties:
                                        group_id:
                                            type: object
                                            properties:
                                                instance_type:
                                                    type: string
                                                    description: instance flavor
                                                os:
                                                    type: string
                                                    description: operating system
                                                location:
                                                    type: string
                                                    description: instance zone
                                        data:
                                            type: array
                                            items:
                                                type: object
                                            properties:
                                                cloud_account_id:
                                                    type: string
                                                    description: cloud account id
                                                cloud_account_type:
                                                    type: string
                                                    description: |
                                                        type of cloud account
                                                    enum: ['aws_cnr']
                                                cloud_account_name:
                                                    type: string
                                                    description: |
                                                        cloud account name
                                                usage:
                                                    type: number
                                                    description: usage hours
                                                cost:
                                                    type: number
                                                    description: usage cost
                                                cloud_resource_id:
                                                    type: string
                                                    description: |
                                                        cloud resource id
                                                id:
                                                    type: string
                                                    description: resource id
                                                name:
                                                    type: string
                                                    description: resource name

                    example:
                        breakdown:
                            1681716160:
                                -   group_id:
                                        os: Linux
                                        instance_type: t2.large
                                        location: us-west-2a
                                    data:
                                        cloud_account_id: 59edd47b-7722-4d36-ab7e-c03dfff90e06
                                        cloud_account_name: cloud_account
                                        cloud_account_type: aws_cnr
                                        name: instance
                                        id: 64435faa-6c51-4cf5-94ce-715019eaf34a
                                        cloud_resource_id: i-0000000000
                                        cost: 9.99
                                        usage: 24
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
