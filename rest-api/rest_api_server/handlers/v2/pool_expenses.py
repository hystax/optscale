import json

from rest_api_server.controllers.pool_expense import (
    PoolExpenseAsyncController)
from rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.utils import run_task, ModelEncoder


class PoolExpensesAsyncHandler(BaseAsyncItemHandler, BaseAuthHandler,
                               BaseHandler):
    def _get_controller_class(self):
        return PoolExpenseAsyncController

    async def get(self, organization_id, **url_params):
        """
        ---
        description: >
            Get summary for all pools in which user can spend money.
            Only highest available pools returned. E.g. if user has permissions
            in both parent and child units, only parent returned.
        Required permission: INFO_ORGANIZATION
        tags: [expenses]
        summary: Get summary for all pools in which user can spend money
        parameters:
        -   in: path
            name: organization_id
            description: id of the organization
            required: true
        responses:
            200:
                description: Pools summary
                schema:
                    type: object
                    properties:
                        expenses:
                            type: object
                            description: summary sums for pools
                            properties:
                                last_month:
                                    type: object
                                    description: last month summary
                                    properties:
                                        total:
                                            type: number
                                            description: >
                                                total expenses for all pools
                                                for last month
                                        date:
                                            type: integer
                                            description: >
                                                timestamp in seconds of the last
                                                of of last month
                                this_month:
                                    type: object
                                    properties:
                                        total:
                                            type: number
                                            description: >
                                                total expenses for all pools
                                                for current month
                                        date:
                                            type: integer
                                            description: >
                                                today's timestamp in seconds
                                this_month_forecast:
                                    type: object
                                    properties:
                                        total:
                                            type: number
                                            description: >
                                                sum of all pools' forecasts
                                                for current month
                                        date:
                                            type: integer
                                            description: >
                                                timestamp of the last day in
                                                current month
                        total:
                            type: number
                            description: total sum of configured pool values
                        pools:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: pool id
                                    name:
                                        type: string
                                        description: >
                                            name of the related object
                                    purpose:
                                        type: string
                                        description: >
                                            purpose of the pool
                                            (pool|business_unit|team|project|
                                            cicd|mlai|asset_pool)
                                    limit:
                                        type: number
                                        description: pool limit value
                                    this_month_expenses:
                                        type: number
                                        description: >
                                            total sum of expenses for
                                            this pool in current month
                                    this_month_forecast:
                                        type: number
                                        description: >
                                            pool's forecast for current month
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
                    - OE0002: Organization not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        res = await run_task(self.controller.get_expenses, organization_id,
                             self.token)
        self.write(json.dumps(res, cls=ModelEncoder))
