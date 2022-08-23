import logging

from jira_bus_server.controllers.shareable_resource import (
    ShareableResourceAsyncController)
from jira_bus_server.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class ShareableResourceHandler(BaseHandler):
    def _get_controller_class(self):
        return ShareableResourceAsyncController

    async def get(self):
        """
        ---
        description: >
            Get OptScale shareable resource list for current Jira tenant.
            An OptScale organization must be assigned to Jira tenant.

            Required permission: ATLASSIAN(require_account, require_issue
            (if current_issue is True))
        tags: [shareable_resource]
        summary: Get shareable resource list
        parameters:
        -   name: current_issue
            in: query
            description: >
                Show only resources with current issue attached. Default is
                `false`.
            required: false
            type: boolean
        responses:
            200:
                description: Shareable resources
                schema:
                    type: object
                    properties:
                        shareable_resources:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: Resource id
                                    name:
                                        type: string
                                        description: Resource name
                                    book_permission:
                                        type: string
                                        enum: [no_login, allowed, forbidden]
                                        description: >
                                            Whether current user can book the
                                            resource. `no_login` means that
                                            Jira user is not connected to
                                            OptScale, `forbidden` means that
                                            user is connected, but has no
                                            permission, and `allowed` means
                                            that user is connected and has
                                            permission
                                    current_booking:
                                        type: object
                                        description: >
                                            Current booking information. Is set
                                            to null if there is no current
                                            booking
                                        properties:
                                            id:
                                                type: string
                                                description: booking id
                                            acquired_by_me:
                                                type: boolean
                                                description: >
                                                    Set to true if current user
                                                    is connected to OptScale
                                                    and current booking belongs
                                                    to him. False otherwise
                                            details:
                                                type: object
                                                description: >
                                                    Booking info from OptScale
                                                    RestAPI
                                    current_attachment:
                                        type: object
                                        description: >
                                            Issue attachment info for current
                                            issue. Exists only if all following
                                            conditions are met: 1) issue is
                                            provided in request token, 2)
                                            current booking exists, 3) current
                                            booking contains current issue as
                                            an attachment.
                                        properties:
                                            id:
                                                type: string
                                                description: attachment id
                                            details:
                                                type: object
                                                description: >
                                                    Attachment info from
                                                    OptScale RestAPI
                                    details:
                                        type: object
                                        description: >
                                            Resource info from OptScale RestAPI
            404:
                description: |
                    Not found:
                    - OJ0019: Organization is not assigned for tenant
        """
        current_issue = self.get_arg('current_issue', bool, False)
        client_key, account_id, issue_key = await self.check_atlassian_auth(
            context_qsh=True,
            require_account=True,
            require_issue=current_issue
        )
        result = await self.controller.list_shareable_resources(
            client_key=client_key,
            account_id=account_id,
            current_issue=current_issue,
            issue_key=issue_key,
        )
        self.write({
            'shareable_resources': result
        })
