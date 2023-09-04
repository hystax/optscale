import logging

from jira_bus.jira_bus_server.controllers.organization_assignment import (
    OrganizationAssignmentAsyncController,
)
from jira_bus.jira_bus_server.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class OrganizationAssignmentHandler(BaseHandler):
    def _get_controller_class(self):
        return OrganizationAssignmentAsyncController

    async def _check_organization_admin(self, auth_token, organization_id):
        await self.check_optscale_permission(
            "EDIT_PARTNER", "organization", organization_id, auth_token
        )

    async def get(self):
        """
        ---
        description: >
            Get organization assignment for current Jira tenant\n\n
            Required permission: ATLASSIAN
        tags: [organization_assignment]
        summary: Get organization assignment
        parameters:
        -   name: details
            in: query
            description: >
                Fetch organization details from RestAPI. Default is `false`.
            required: false
            type: boolean
        responses:
            200:
                description: Organization assignment
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Unique organization assignment id
                        organization_id:
                            type: string
                            description: OptScale organization id
                        app_installation_id:
                            type: string
                            description: App installation id
                        created_at:
                            type: integer
                            description: Created timestamp (service field)
                        deleted_at:
                            type: integer
                            description: Deleted timestamp (service field)
                        details:
                            type: object
                            description: >
                                Organization details (available when details
                                parameter is set to true)
                            properties:
                                id:
                                    type: string
                                    description: OptScale organization id
                                name:
                                    type: string
                                    description: OptScale organization name
            404:
                description: |
                    Not found:
                    - OJ0019: Organization is not assigned for tenant
        """
        client_key, _, _ = await self.check_atlassian_auth(context_qsh=True)
        details = self.get_arg("details", bool, False)
        org_assignment = await self.controller.get_organization_assignment(client_key)
        if details:
            org_assignment["details"] = await (
                self.controller.get_organization_details(
                    org_assignment["organization_id"]
                )
            )
        self.write(org_assignment)

    async def post(self):
        """
        ---
        description: >
            Create or update OptScale organization assignment for current Jira
            tenant. Current user must be assigned to OptScale and must have
            manager permissions on both currently-assigned organization
            (if exists) and newly-provided organization.\n\n
            Required permission: ATLASSIAN(require_account)
        tags: [organization_assignment]
        summary: Create or update organization assignment
        parameters:
        -   in: body
            name: body
            description: request parameters
            required: true
            schema:
                type: object
                properties:
                    organization_id:
                        type: string
                        description: OptScale organization id
        responses:
            204:
                description: Success
            404:
                description: |
                    Not found:
                    - OJ0008: user not found
            424:
                description: |
                    Failed dependency:
                    - OJ0021: OptScale user is not assigned for account
        """
        params = self._request_body()
        organization_id = params.get("organization_id")
        client_key, account_id, _ = await self.check_atlassian_auth(
            require_account=True, context_qsh=True
        )
        auth_token = await self.controller.get_auth_token(account_id)
        found_assignment = await self.controller.get_organization_assignment(
            client_key, raise_not_found=False
        )
        if found_assignment:
            await self._check_organization_admin(
                auth_token, found_assignment["organization_id"]
            )
        await self._check_organization_admin(auth_token, organization_id)
        await self.controller.create_organization_assignment(
            client_key, organization_id
        )
        self.set_status(204)

    async def delete(self):
        """
        ---
        description: >
            Delete OptScale organization assignment for current Jira tenant.
            Current user must be assigned to OptScale and must have
            manager permissions on currently-assigned organization.\n\n
            Required permission: ATLASSIAN(require_account)
        tags: [organization_assignment]
        summary: Delete organization assignment
        responses:
            204:
                description: Success
            404:
                description: |
                    Not found:
                    - OJ0008: user not found
            424:
                description: |
                    Failed dependency:
                    - OJ0021: OptScale user is not assigned for account
        """
        client_key, account_id, _ = await self.check_atlassian_auth(
            require_account=True, context_qsh=True
        )
        found_assignment = await self.controller.get_organization_assignment(
            client_key, raise_not_found=False
        )
        if found_assignment:
            auth_token = await self.controller.get_auth_token(account_id)
            await self._check_organization_admin(
                auth_token, found_assignment["organization_id"]
            )
            await self.controller.delete_organization_assignment(client_key)
        self.set_status(204)
