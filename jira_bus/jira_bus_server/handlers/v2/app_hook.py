import logging

from jira_bus_server.controllers.app_hook import AppHookAsyncController
from jira_bus_server.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class AppHookIssueUpdatedHandler(BaseHandler):
    def _get_controller_class(self):
        return AppHookAsyncController

    async def post(self):
        """
        ---
        description: >
            Process "Issue Updated" hook coming from Jira\n\n
            Required permission: ATLASSIAN
        tags: [hook]
        summary: Handle "Issue Updated" Jira hook
        parameters:
        -   in: body
            name: body
            description: hook body, filled by Jira
            required: true
            schema:
                type: object
        responses:
            204:
                description: Success
        """
        client_key, _, _ = await self.check_atlassian_auth()
        await self.controller.issue_updated(client_key, self._request_body())
        self.set_status(204)


class AppHookIssueDeletedHandler(BaseHandler):
    def _get_controller_class(self):
        return AppHookAsyncController

    async def post(self):
        """
        ---
        description: >
            Process "Issue Deleted" hook coming from Jira\n\n
            Required permission: ATLASSIAN
        tags: [hook]
        summary: Handle "Issue Deleted" Jira hook
        parameters:
        -   in: body
            name: body
            description: hook body, filled by Jira
            required: true
            schema:
                type: object
        responses:
            204:
                description: Success
        """
        client_key, _, _ = await self.check_atlassian_auth()
        await self.controller.issue_deleted(client_key, self._request_body())
        self.set_status(204)
