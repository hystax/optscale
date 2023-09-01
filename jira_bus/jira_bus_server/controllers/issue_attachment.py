import logging
from datetime import datetime

from jira_bus.jira_bus_server.controllers.base import (
    BaseController,
    BaseAsyncControllerWrapper,
)
from jira_bus.jira_bus_server.exceptions import Err

from tools.optscale_exceptions.common_exc import NotFoundException

LOG = logging.getLogger(__name__)


class IssueAttachmentController(BaseController):
    def _find_existing_booking(
        self, rest_client, employee_id, resource_id, raise_not_found=True
    ):
        now_timestamp = int(datetime.utcnow().timestamp())
        _, resource_info = rest_client.cloud_resource_get(resource_id, details=True)
        for booking in resource_info["details"]["shareable_bookings"]:
            employee_match = booking["acquired_by"]["id"] == employee_id
            start_match = booking["acquired_since"] <= now_timestamp
            end_match = (
                booking["released_at"] >= now_timestamp or booking["released_at"] == 0
            )
            if employee_match and start_match and end_match:
                return booking["id"]
        if raise_not_found:
            raise NotFoundException(Err.OJ0025, [])

    def _create_booking(self, rest_client, organization_id, employee_id, resource_id):
        _, created_booking = rest_client.shareable_book_create(
            organization_id=organization_id,
            params={
                "resource_id": resource_id,
                "acquired_by_id": employee_id,
                "jira_auto_release": True,
            },
        )
        return created_booking["id"]

    def _delete_booking(self, rest_client, booking_id):
        rest_client.shareable_book_delete(booking_id)

    def _get_employee_id(self, rest_client, organization_id):
        _, employee_list = rest_client.employee_list(organization_id, current_only=True)
        return employee_list["employees"][0]["id"]

    def create_attachment(
        self,
        client_key,
        account_id,
        issue_key,
        resource_id,
        auto_detach_status,
        booking_id=None,
    ):
        app_installation = self._get_app_installation_by_client_key(client_key)
        org_assignment = self._get_org_assignment_by_client_key(client_key)
        auth_token = self.get_auth_token(account_id)
        rest_client = self._get_rest_client(token=auth_token)
        issue_info = self._get_issue_info(app_installation, issue_key)
        employee_id = self._get_employee_id(rest_client, org_assignment.organization_id)
        if not booking_id:
            booking_id = self._find_existing_booking(
                rest_client, employee_id, resource_id
            )
        attachment_params = {
            "client_key": client_key,
            "project_key": issue_info["project_key"],
            "issue_number": issue_info["issue_number"],
            "issue_link": issue_info["issue_link"],
            "status": issue_info["current_status"],
            "shareable_booking_id": booking_id,
            "auto_detach_status": auto_detach_status,
        }
        _, created_attachment = rest_client.jira_issue_attachment_create(
            org_assignment.organization_id, attachment_params
        )
        return created_attachment

    def update_attachment(self, account_id, attachment_id, params):
        auth_token = self.get_auth_token(account_id)
        rest_client = self._get_rest_client(token=auth_token)
        rest_client.jira_issue_attachment_update(attachment_id, params)

    def delete_attachment(self, account_id, attachment_id):
        auth_token = self.get_auth_token(account_id)
        rest_client = self._get_rest_client(token=auth_token)
        rest_client.jira_issue_attachment_delete(attachment_id)


class IssueAttachmentAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return IssueAttachmentController
