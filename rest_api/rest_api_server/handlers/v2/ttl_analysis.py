from datetime import datetime

from tools.optscale_exceptions.common_exc import WrongArgumentsException
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.controllers.ttl_analysis import TtlAnalysisAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import run_task, check_int_attribute


MAX_TTL_VALUE = 720


class TtlAnalysisAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                                  BaseHandler):
    def _get_controller_class(self):
        return TtlAnalysisAsyncController

    async def get(self, pool_id):
        """
        ---
        description: |
            Get analysis of TTL value for pool in specified date range
            Required permission: INFO_ORGANIZATION
        tags: [ttl_analysis]
        summary: Get TTL analysis
        parameters:
        -   name: pool_id
            in: path
            description: Pool id
            required: true
            type: string
        -   name: start_date
            in: query
            description: Start date (timestamp in seconds)
            required: true
            type: integer
        -   name: end_date
            in: query
            description: End date (timestamp in seconds). Defaults to current TS
            required: false
            type: integer
        -   name: ttl
            in: query
            description: >
                TTL in hours to base analysis on. Defaults to the value set in
                policy (if configured). Max value - 720
            required: false
            type: integer
        responses:
            200:
                description: TTL analysis
                schema:
                    type: object
                    properties:
                        resources_outside_of_ttl:
                            type: integer
                            description: Count of resources in resources list
                        resources_tracked:
                            type: integer
                            description: >
                                Count of all processed resources in date range
                        total_expenses:
                            type: number
                            description: Total expenses in date range
                        expenses_outside_of_ttl:
                            type: number
                            description: >
                                Sum of expenses for resource in resources list
                                after TTL reached
                        resources:
                            type: array
                            description: >
                                List of resources for which TTL exceeded in
                                date range
                            items:
                                type: object
                                properties:
                                    cloud_account_id:
                                        type: string
                                        description: Cloud account id
                                    cloud_account_name:
                                        type: string
                                        description: Cloud account name
                                    cloud_resource_id:
                                        type: string
                                        description: Cloud resource id
                                    cloud_type:
                                        type: string
                                        description: Type of the cloud account
                                    expenses_outside_of_ttl:
                                        type: number
                                        description: >
                                            Expenses for resource after TTL
                                            reached
                                    hours_outside_of_ttl:
                                        type: integer
                                        description: >
                                            Hours resource existed in date range
                                            since TTL reached
                                    id:
                                        type: string
                                        description: Resource id
                                    name:
                                        type: string
                                        description: Resource name
                                    owner_id:
                                        type: string
                                        description: Id of the resource owner
                                    owner_name:
                                        type: string
                                        description: Name of the resource owner
                                    type:
                                        type: string
                                        description: Resource type
                    example:
                        resources_outside_of_ttl: 5
                        resources_tracked: 10
                        total_expenses: 22.0
                        expenses_outside_of_ttl: 11.0
                        resources:
                        - cloud_account_id: 4352b0f1-b6a7-4f6e-b550-4812095eb109
                          cloud_account_name: AWS
                          cloud_resource_id: i-0e0408dfa3e919097
                          cloud_type: aws_cnr
                          expenses_outside_of_ttl: 5.0
                          hours_outside_of_ttl: 11
                          id: 4ea09458-e6c3-4e5d-b0fd-e3f69d70e8fe
                          name: flashgrid_dontdelete
                          owner_id: 00cc3264-6b1b-4f0b-9397-166b137aabb9
                          owner_name: Mr. Smith
                          type: Instance
            400:
                description: |
                    Wrong arguments:
                    - OE0216: Argument not provided
                    - OE0217: Invalid argument
                    - OE0224: Wrong integer value
                    - OE0446: "end_date" should be greater than "start_date"
            424:
                description: |
                    Failed dependency:
                    - OE0457: Unable to find policy for pool, please specify TTL
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Pool not found
        security:
        - token: []
        """
        await self.check_permissions('INFO_ORGANIZATION', 'pool', pool_id)
        args = {
            'start_date': self.get_arg('start_date', int),
            'end_date': self.get_arg('end_date', int),
            'ttl': self.get_arg('ttl', int),
        }
        max_date = int(datetime.max.timestamp() - 1)
        try:
            check_int_attribute('start_date', args['start_date'],
                                max_length=max_date)
            if args['end_date'] is not None:
                check_int_attribute('end_date', args['end_date'],
                                    max_length=max_date)
            if args['ttl'] is not None:
                check_int_attribute('ttl', args['ttl'], min_length=1,
                                    max_length=MAX_TTL_VALUE)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)

        res = await run_task(self.controller.get, pool_id, **args)
        self.write(res)
