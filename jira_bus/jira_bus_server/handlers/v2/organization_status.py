import logging

from jira_bus_server.controllers.organization_status import (
    OrganizationStatusAsyncController)
from jira_bus_server.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class OrganizationStatusHandler(BaseHandler):
    def _get_controller_class(self):
        return OrganizationStatusAsyncController

    async def get(self, organization_id):
        """
        ---
        description: >
            Get Jira connection status for specified OptScale organization.\n\n
            Required permission: TOKEN(INFO_ORGANIZATION) or CLUSTER_SECRET
        tags: [organization_status]
        summary: Get organization connection status
        responses:
            200:
                description: Connection status
                schema:
                    type: object
                    properties:
                        connected:
                            type: boolean
                            description: >
                                true if this organization is connected to Jira,
                                false otherwise
                        connected_tenants:
                            type: array
                            items:
                                type: object
                                properties:
                                    client_key:
                                        type: string
                                        description: >
                                            Client key (Jira tenant id)
                                    description:
                                        type: string
                                        description: >
                                            Jira tenant description
                                    display_url:
                                        type: boolean
                                        description: >
                                            User-facing Jira tenant URL
            404:
                description: |
                    Not found:
                    - OJ0008: organization not found
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_optscale_permission(
                'INFO_ORGANIZATION', 'organization', organization_id)
        connected_tenants = await self.controller.get_connected_tenants(
            organization_id)
        self.write({
            'connected': bool(connected_tenants),
            'connected_tenants': connected_tenants,
        })
