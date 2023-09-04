import logging

from jira_bus.jira_bus_server.controllers.shareable_book import (
    ShareableBookAsyncController,
)
from jira_bus.jira_bus_server.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class ShareableBookCollectionHandler(BaseHandler):
    def _get_controller_class(self):
        return ShareableBookAsyncController

    async def post(self, resource_id):
        """
        ---
        description: >
            Create a shareable booking for current user. The user must be
            assigned to OptScale and must have permissions to create/update
            shareable resource bookings.\n\n
            Required permission: ATLASSIAN(require_account)
        tags: [shareable_book]
        summary: Create resource booking
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
                    jira_auto_release:
                        type: string
                        description: >
                            Release booking automatically when all Jira issues
                            are detached. Default is true.
        responses:
            200:
                description: Created booking info
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
            context_qsh=True, require_account=True
        )
        jira_auto_release = bool(self._request_body().get("jira_auto_release", True))
        result = await self.controller.create_booking(
            client_key, account_id, resource_id, jira_auto_release
        )
        self.write(result)


class ShareableBookItemHandler(BaseHandler):
    def _get_controller_class(self):
        return ShareableBookAsyncController

    async def patch(self, booking_id):
        """
        ---
        description: >
            Release shareable resource booking.
            Current user must be assigned to OptScale and must have
            permissions to create/update shareable resource bookings.\n\n
            Required permission: ATLASSIAN(require_account)
        tags: [shareable_book]
        summary: Update resource booking
        parameters:
        -   name: booking_id
            in: path
            description: booking id
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
        await self.controller.release_booking(account_id, booking_id)
        self.set_status(204)

    async def delete(self, booking_id):
        """
        ---
        description: >
            Delete shareable resource booking.
            Current user must be assigned to OptScale and must have
            permissions to create/update shareable resource bookings.\n\n
            Required permission: ATLASSIAN(require_account)
        tags: [shareable_book]
        summary: Delete resource booking
        parameters:
        -   name: booking_id
            in: path
            description: booking id
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
        await self.controller.delete_booking(account_id, booking_id)
        self.set_status(204)
