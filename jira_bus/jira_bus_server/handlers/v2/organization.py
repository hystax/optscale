import logging

from jira_bus_server.controllers.organization import (
    OrganizationAsyncController)
from jira_bus_server.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class OrganizationCollectionHandler(BaseHandler):
    def _get_controller_class(self):
        return OrganizationAsyncController

    async def get(self):
        """
        ---
        description: >
            Get OptScale organization list available for current user.\n\n
            User must be assigned to OptScale.
            Required permission: ATLASSIAN(require_account)
        tags: [organization]
        summary: Get organization list
        responses:
            200:
                description: Organization assignment
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
                                        description: OptScale organization id
                                    name:
                                        type: string
                                        description: OptScale organization name
                                    is_manager:
                                        type: boolean
                                        description: >
                                            True if current user is
                                            organization manager
            404:
                description: |
                    Not found:
                    - OJ0008: user not found
            424:
                description: |
                    Failed dependency:
                    - OJ0021: OptScale user is not assigned for account
        """
        _, account_id, _ = await self.check_atlassian_auth(
            require_account=True, context_qsh=True)
        org_list = await self.controller.list_organizations(account_id)
        self.write({'organizations': org_list})
