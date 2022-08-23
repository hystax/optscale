import json
import logging

from rest_api_server.controllers.pool import PoolAsyncController
from rest_api_server.controllers.organization import OrganizationAsyncController
from rest_api_server.handlers.v1.organizations import (
    OrganizationAsyncCollectionHandler as OrganizationAsyncCollectionHandler_v1)
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.utils import ModelEncoder, run_task

from optscale_exceptions.common_exc import UnauthorizedException, NotFoundException
from optscale_exceptions.http_exc import OptHTTPError
LOG = logging.getLogger(__name__)


class OrganizationsOverviewAsyncHandler(OrganizationAsyncCollectionHandler_v1,
                                        BaseHandler):
    def _get_controller_class(self):
        return PoolAsyncController

    async def get(self):
        """
        ---
        description: |
            Gets a list of organizations available to user.
            Required permission: TOKEN
        tags: [organizations_overview]
        summary: List of pool info from organizations available to user
        parameters:
        -   name: details
            in: query
            description: display child pools, expenses and policies info
            required: false
            type: boolean
            default: false
        responses:
            200:
                description: Organizations list available for user
                schema:
                    type: object
                    properties:
                        organizations:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: Unique organization id
                                    name:
                                        type: string
                                        description: Organization name
                                    deleted_at:
                                        type: integer
                                        description: Deleted timestamp (service field)
                                    created_at:
                                        type: integer
                                        description: Created timestamp (service field)
                                    pool_id:
                                        type: string
                                        description: Root pool id
                                    is_demo:
                                        type: bool
                                        description: Is organization demo or not
                                    cost:
                                        type: integer
                                        description: Expenses for this month (only when details=True)
                                    last_month_cost:
                                        type: integer
                                        description: |
                                         Expenses for previous month (only when details=True)
                                    forecast:
                                        type: integer
                                        description: |
                                         Expense forecast for current month (only when details=True)
                                    saving:
                                        type: integer
                                        description: |
                                         Possible savings for organization (only when details=True)
                                    pools:
                                        type: array
                                        items:
                                            type: object
                                            properties:
                                                id:
                                                    type: string,
                                                    description: Unique pool id
                                                parent_id:
                                                    type: string
                                                    description: Parent pool id
                                                name:
                                                    type: string
                                                    description: Pool name
                                                organization_id:
                                                    type: string
                                                    description: Organization id
                                                limit:
                                                    type: integer
                                                    description: Pool limit
                                                unallocated_limit:
                                                    type: integer
                                                    description: Unallocated pool limit
                                                deleted_at:
                                                    type: integer
                                                    description: |
                                                     Deleted timestamp (service field)
                                                created_at:
                                                    type: integer
                                                    description: |
                                                     Created timestamp (service field)
                                                default_owner_id:
                                                    type: string
                                                    description: Default owner id
                                                default_owner_name:
                                                    type: string
                                                    description: Default owner name
                                                cost:
                                                    type: integer
                                                    description: Expenses for this month (only when details=True)
                                                forecast:
                                                    type: integer
                                                    description: |
                                                     Expense forecast for current month (only when details=True)
                                                children:
                                                    type: array
                                                    description: Pool children (when details is true)
                                                    items:
                                                        type: object
                                                        properties:
                                                            id:
                                                                type: string,
                                                                description: Unique pool id
                                                            name:
                                                                type: string
                                                                description: |
                                                                 Pool display name
                                                            deleted_at:
                                                                type: integer
                                                                description: |
                                                                 Deleted timestamp (service field)
                                                            parent_id:
                                                                type: string
                                                                description: |
                                                                 Pool's parent id
                                                            limit:
                                                                type: integer
                                                                description: |
                                                                 Pool limit
                                                            unallocated_limit:
                                                                type: integer
                                                                description: |
                                                                 Unallocated pool limit
                                                            cost:
                                                                type: integer
                                                                description: |
                                                                 Expenses for this month
                                                            last_month_cost:
                                                                type: integer
                                                                description: |
                                                                 Expenses for previous month
                                                            forecast:
                                                                type: integer
                                                                description: |
                                                                 Expense forecast for current month
                                                            saving:
                                                                type: integer
                                                                description: |
                                                                 Possible savings for organization
                                                            policies:
                                                                type: array
                                                                items:
                                                                type: object
                                                                properties:
                                                                    id:
                                                                        type: string
                                                                        description: Unique policy id
                                                                    pool_id:
                                                                        type: string
                                                                        description: Unique pool id
                                                                    type:
                                                                        type: string
                                                                        enum: |
                                                                         [ttl,total_expense_limit,daily_expense_limit]
                                                                        description: Policy type
                                                                    active:
                                                                        type: boolean
                                                                        description: |
                                                                         Policy active or not
                                                                    limit:
                                                                        type: integer
                                                                        description: |
                                                                         Policy limit (expense value or timestamp)
                                                                    created_at:
                                                                        type: integer
                                                                        description: |
                                                                         Created timestamp (service field)
                                                                    deleted_at:
                                                                        type: integer
                                                                        description: |
                                                                         Deleted timestamp (service field)
                                                policies:
                                                    type: array
                                                    description: Pool policies (only when details=True)
                                                    items:
                                                        type: object
                                                        properties:
                                                            id:
                                                                type: string
                                                                description: Unique policy id
                                                            pool_id:
                                                                type: string
                                                                description: Unique pool id
                                                            type:
                                                                type: integer
                                                                enum: [ttl, total_expense_limit, daily_expense_limit]
                                                                description: Policy type
                                                            active:
                                                                type: boolean
                                                                description: Policy active or not
                                                            limit:
                                                                type: integer
                                                                description: |
                                                                 Policy limit (expense value or timestamp)
                                                            created_at:
                                                                type: integer
                                                                description: |
                                                                 Created timestamp (service field)
                                                            deleted_at:
                                                                type: integer
                                                                description: |
                                                                 Deleted timestamp (service field)

            401: {description: "Unauthorized: \n\n
                - OE0235: Unauthorized\n\n
                - OE0237: This resource requires authorization"}
        security:
        - token: []
        """
        details = self.get_arg('details', bool, False)
        res = []
        try:
            org_ctrl = OrganizationAsyncController(
                self.session(), self._config, self.token)
            orgs = await run_task(
                org_ctrl.root_organizations_list, self.token)
            for org in orgs:
                org_data = org.to_dict()
                org_data['pools'] = []
                try:
                    overview = await run_task(
                        self.controller.get_overview, org, details)
                    org_data['pools'].append(overview)
                    if details:
                        saving_overview = await run_task(
                            self.controller.get_overview_savings, org.id)
                        org_data['saving'] = saving_overview
                        org_data['last_month_cost'] = overview[
                            'last_month_cost']
                        org_data['cost'] = org_data['pools'][0]['cost']
                        forecast = await run_task(
                            self.controller.get_organization_forecast,
                            org_data['last_month_cost'] + org_data['cost'],
                            org_data['cost'], org.id)
                        org_data['forecast'] = forecast
                except NotFoundException:
                    pass
                res.append(org_data)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)

        self.write(json.dumps({'organizations': res}, cls=ModelEncoder))
