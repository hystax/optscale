import logging

from jira_bus_server.controllers.app_lifecycle import (
    AppLifecycleAsyncController)
from jira_bus_server.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class AppLifecycleInstalledHandler(BaseHandler):
    def _get_controller_class(self):
        return AppLifecycleAsyncController

    async def post(self):
        """
        ---
        description: >
            Handle "installed" app lifecycle hook\n\n
            Required permission: ATLASSIAN_ASYMMETRIC
        tags: [app_lifecycle]
        summary: Handle "installed" app lifecycle hook
        parameters:
        -   in: body
            name: body
            description: request payload, filled by Jira
            required: true
            schema:
                type: object
        responses:
            204:
                description: Success
        """
        await self.check_atlassian_auth_asymmetric()
        await self.controller.installed(self._request_body())

        # This is the status code Jira expects.
        # It will say "The app failed to install" if the code is different.
        self.set_status(204)
