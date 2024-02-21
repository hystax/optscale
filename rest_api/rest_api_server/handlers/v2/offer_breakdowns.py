import json
from rest_api.rest_api_server.handlers.v2.expenses import (
    FilteredExpensesBaseAsyncHandler)
from rest_api.rest_api_server.controllers.offer_breakdown import (
    OfferBreakdownAsyncController)
from rest_api.rest_api_server.utils import (run_task, ModelEncoder)


class OfferBreakdownAsyncHandler(FilteredExpensesBaseAsyncHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.str_filters = []
        self.int_filters = ['start_date', 'end_date']
        self.list_filters = ['cloud_account_id']

    def _get_controller_class(self):
        return OfferBreakdownAsyncController

    async def get(self, organization_id, **url_params):
        """
         ---
         description: |
             Get RI/SP cost breakdown by offer
             Required permission: INFO_ORGANIZATION
         tags: [ri_sp_breakdowns]
         summary: Get RI/SP offers cost breakdown
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
                 description: Offers cost data breakdown
                 schema:
                     type: object
                     properties:
                         breakdown:
                             type: object
                             description: >
                                 breakdown for RI/SP offers
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
                                         cost:
                                             type: number
                                             description: current cost of offer usage
                                         expected_cost:
                                             type: number
                                             description: |
                                               cost of usage expected to spend
                                         id:
                                             type: string
                                             description: offer id
                                         cloud_resource_id:
                                             type: string
                                             description: offer cloud resource id
                                         payment_option:
                                             type: string
                                             description: offer payment option
                                         offering_type:
                                             type: string
                                             description: offering type
                                         purchase_term:
                                             type: string
                                             description: offer purchase term
                                         applied_region:
                                             type: string
                                             description: offer applied region
                     example:
                         breakdown:
                             1681716160:
                                 -   cloud_account_id: 72771690-619f-4a0c-8652-7bdf3ae48ab7
                                     cloud_account_type: aws_cnr
                                     cloud_account_name: "My cloud account"
                                     id: cde8d333-c3d6-481c-854f-8450d41e291f
                                     cloud_resource_id: ea328889-174a-4f73-8bf1-8b5720639b9d
                                     cost: 10
                                     expected_cost: 11
                                     payment_option: "No Upfront"
                                     offering_type: standard
                                     purchase_term: 1yr
                                     applied_region: Any
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
