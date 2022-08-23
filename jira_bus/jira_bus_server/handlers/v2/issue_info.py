import logging

from jira_bus_server.controllers.issue_info import IssueInfoAsyncController
from jira_bus_server.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class IssueInfoHandler(BaseHandler):
    def _get_controller_class(self):
        return IssueInfoAsyncController

    async def get(self):
        """
        ---
        description: >
            Get information about current Jira issue.\n\n
            Required permission: ATLASSIAN(require_issue)
        tags: [issue_info]
        summary: Get issue info
        responses:
            200:
                description: Issue info
                schema:
                    type: object
                    properties:
                        issue_key:
                            type: string
                            description: Issue key
                        project_key:
                            type: string
                            description: Project key
                        issue_number:
                            type: integer
                            description: Issue number in project
                        issue_link:
                            type: string
                            description: User-facing issue link
                        available_statuses:
                            type: array
                            description: Available issue statuses
                            items:
                                type: string
                        current_status:
                            type: string
                            description: Current issue status
        """
        client_key, _, issue_key = await self.check_atlassian_auth(
            context_qsh=True, require_issue=True)
        result = await self.controller.get_issue_info(client_key, issue_key)
        self.write(result)
