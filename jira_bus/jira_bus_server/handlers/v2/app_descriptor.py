import logging

from jira_bus.jira_bus_server.controllers.app_descriptor import (
    AppDescriptorAsyncController,
)
from jira_bus.jira_bus_server.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class AppDescriptorHandler(BaseHandler):
    def _get_controller_class(self):
        return AppDescriptorAsyncController

    async def get(self):
        """
        ---
        description: >
            Get installation app descriptor for Jira app\n\n
            Required permission: none
        tags: [app_descriptor]
        summary: Get the installation app descriptor for Jira plugin
        parameters:
        -   name: base_host
            in: query
            description: >
                Base OptScale host to put inside app descriptor. Defaults to
                OptScale public IP.
            required: false
            type: string
        responses:
            200:
                description: App descriptor JSON for Jira
                schema:
                    type: object
        """
        base_host = self.get_arg("base_host", str)
        result = await self.controller.app_descriptor(base_host=base_host)
        self.write(result)
