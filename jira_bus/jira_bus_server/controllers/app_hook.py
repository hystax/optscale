import logging

from jira_bus.jira_bus_server.controllers.base import (
    BaseController,
    BaseAsyncControllerWrapper,
)
from jira_bus.jira_bus_server.exceptions import Err

from tools.optscale_exceptions.common_exc import WrongArgumentsException


LOG = logging.getLogger(__name__)


class AppHookController(BaseController):
    def _parse_issue_payload(self, hook_payload):
        try:
            issue_key = hook_payload["issue"]["key"]
            issue_status = hook_payload["issue"]["fields"]["status"]["name"]
        except KeyError:
            raise WrongArgumentsException(Err.OJ0024, hook_payload)
        project_key, issue_number = self._parse_issue_key(issue_key)
        return project_key, issue_number, issue_status

    def issue_updated(self, client_key, hook_payload):
        project_key, issue_number, issue_status = self._parse_issue_payload(
            hook_payload
        )
        rest_client = self._get_rest_client(secret=self._cluster_secret)
        org_assignment = self._get_org_assignment_by_client_key(client_key)
        _, attachments = rest_client.jira_issue_attachment_list(
            org_assignment.organization_id, client_key, project_key, issue_number
        )
        for attachment in attachments["jira_issue_attachments"]:
            try:
                rest_client.jira_issue_attachment_update(
                    attachment["id"], {"status": issue_status}
                )
            except Exception as exc:
                LOG.exception(
                    "Failed to update attachment %s: %s", attachment["id"], str(exc)
                )

    def issue_deleted(self, client_key, hook_payload):
        project_key, issue_number, issue_status = self._parse_issue_payload(
            hook_payload
        )
        rest_client = self._get_rest_client(secret=self._cluster_secret)
        org_assignment = self._get_org_assignment_by_client_key(client_key)
        _, attachments = rest_client.jira_issue_attachment_list(
            org_assignment.organization_id, client_key, project_key, issue_number
        )
        for attachment in attachments["jira_issue_attachments"]:
            try:
                rest_client.jira_issue_attachment_delete(attachment["id"])
            except Exception as exc:
                LOG.exception(
                    "Failed to delete attachment %s: %s", attachment["id"], str(exc)
                )


class AppHookAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AppHookController
