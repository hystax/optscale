import logging

from jira_bus.jira_bus_server.controllers.base import (
    BaseController,
    BaseAsyncControllerWrapper,
)

LOG = logging.getLogger(__name__)


class IssueInfoController(BaseController):
    def get_issue_info(self, client_key, issue_key):
        app_installation = self._get_app_installation_by_client_key(client_key)
        result = self._get_issue_info(app_installation, issue_key)
        return result


class IssueInfoAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return IssueInfoController
