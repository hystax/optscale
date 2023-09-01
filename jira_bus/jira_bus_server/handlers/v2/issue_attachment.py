import logging

from jira_bus.jira_bus_server.controllers.issue_attachment import (
    IssueAttachmentAsyncController,
)
from jira_bus.jira_bus_server.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class IssueAttachmentCollectionHandler(BaseHandler):
    def _get_controller_class(self):
        return IssueAttachmentAsyncController

    async def post(self, resource_id):
        """
        ---
        description: >
            Attach current Jira issue to specified shareable resource.
            Current user must be assigned to OptScale and must have permissions
            to create/update shareable resource bookings.\n\n
            Required permission: ATLASSIAN(require_account, require_issue)
        tags: [issue_attachment]
        summary: Attach current issue
        parameters:
        -   name: resource_id
            in: path
            description: shareable resource id
            required: true
            type: string
        -   in: body
            name: body
            description: request parameters
            required: true
            schema:
                type: object
                properties:
                    auto_detach_status:
                        type: string
                        description: >
                            Issue status on which attachment will be
                            automatically deleted. Default is null (no
                            auto-delete).
                    booking_id:
                        type: string
                        description: >
                            Booking id for which attachment is created. Default
                            is null (search for current booking automatically).
        responses:
            200:
                description: Created attachment info
            404:
                description: |
                    Not found:
                    - OJ0008: user not found
            424:
                description: |
                    Failed dependency:
                    - OJ0021: OptScale user is not assigned for account
        """
        client_key, account_id, issue_key = await self.check_atlassian_auth(
            context_qsh=True, require_account=True, require_issue=True
        )
        request_body = self._request_body()
        auto_detach_status = request_body.get("auto_detach_status")
        booking_id = request_body.get("booking_id")
        result = await self.controller.create_attachment(
            client_key,
            account_id,
            issue_key,
            resource_id,
            auto_detach_status,
            booking_id,
        )
        self.write(result)


class IssueAttachmentItemHandler(BaseHandler):
    def _get_controller_class(self):
        return IssueAttachmentAsyncController

    async def patch(self, attachment_id):
        """
        ---
        description: >
            Update Jira issue attachment.
            Current user must be assigned to OptScale and must have
            permissions to create/update shareable resource bookings.\n\n
            Required permission: ATLASSIAN(require_account)
        tags: [issue_attachment]
        summary: Update issue attachment
        parameters:
        -   name: attachment_id
            in: path
            description: issue attachment id
            required: true
            type: string
        -   in: body
            name: body
            description: request parameters
            required: true
            schema:
                type: object
                properties:
                    auto_detach_status:
                        type: string
                        description: >
                            Issue status on which attachment will be
                            automatically deleted. Default is null (no
                            auto-delete).
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
        _, account_id, _ = await self.check_atlassian_auth(
            context_qsh=True, require_account=True
        )
        params = self._request_body()
        await self.controller.update_attachment(account_id, attachment_id, params)
        self.set_status(204)

    async def delete(self, attachment_id):
        """
        ---
        description: >
            Delete Jira issue attachment.
            Current user must be assigned to OptScale and must have
            permissions to create/update shareable resource bookings.\n\n
            Required permission: ATLASSIAN(require_account)
        tags: [issue_attachment]
        summary: Delete issue attachment
        parameters:
        -   name: attachment_id
            in: path
            description: issue attachment id
            required: true
            type: string
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
        _, account_id, _ = await self.check_atlassian_auth(
            context_qsh=True, require_account=True
        )
        await self.controller.delete_attachment(account_id, attachment_id)
        self.set_status(204)
