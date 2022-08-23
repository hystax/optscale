import logging
from datetime import datetime

from jira_bus_server.controllers.base import (BaseController,
                                              BaseAsyncControllerWrapper)

LOG = logging.getLogger(__name__)


class ShareableBookController(BaseController):
    def _get_employee_id(self, rest_client, organization_id):
        _, employee_list = rest_client.employee_list(
            organization_id, current_only=True)
        return employee_list['employees'][0]['id']

    def create_booking(self, client_key, account_id, resource_id,
                       jira_auto_release):
        org_assignment = self._get_org_assignment_by_client_key(client_key)
        auth_token = self.get_auth_token(account_id)
        rest_client = self._get_rest_client(token=auth_token)
        employee_id = self._get_employee_id(
            rest_client, org_assignment.organization_id)
        _, created_booking = rest_client.shareable_book_create(
            organization_id=org_assignment.organization_id,
            params={
                'resource_id': resource_id,
                'acquired_by_id': employee_id,
                'jira_auto_release': jira_auto_release,
            }
        )
        return created_booking

    def release_booking(self, account_id, booking_id):
        auth_token = self.get_auth_token(account_id)
        rest_client = self._get_rest_client(token=auth_token)
        now_timestamp = int(datetime.utcnow().timestamp())
        rest_client.shareable_book_release(booking_id, {
            'released_at': now_timestamp})

    def delete_booking(self, account_id, booking_id):
        auth_token = self.get_auth_token(account_id)
        rest_client = self._get_rest_client(token=auth_token)
        rest_client.shareable_book_delete(booking_id)


class ShareableBookAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ShareableBookController
