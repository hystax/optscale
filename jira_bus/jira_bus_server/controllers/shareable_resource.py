import logging
from datetime import datetime
from enum import Enum

from jira_bus_server.controllers.base import (BaseController,
                                              BaseAsyncControllerWrapper)

LOG = logging.getLogger(__name__)


class BookPermissions(Enum):
    NO_LOGIN = 'no_login'
    ALLOWED = 'allowed'
    FORBIDDEN = 'forbidden'


class ShareableResourceController(BaseController):

    def _get_book_permissions(self, resource_ids, auth_token=None):
        if auth_token is not None:
            auth_client = self._get_auth_client(token=auth_token)
            payload_list = [('cloud_resource', r_id) for r_id in resource_ids]
            _, allowed_actions = auth_client.allowed_action_get(payload_list)
            permissions = {}
            for r_id, actions in allowed_actions.items():
                if 'BOOK_ENVIRONMENTS' in actions:
                    permissions[r_id] = BookPermissions.ALLOWED.value
                else:
                    permissions[r_id] = BookPermissions.FORBIDDEN.value
        else:
            permissions = {r_id: BookPermissions.NO_LOGIN.value
                           for r_id in resource_ids}
        return permissions

    def _get_employee_id(self, rest_client, organization_id):
        _, employee_list = rest_client.employee_list(
            organization_id, current_only=True)
        return employee_list['employees'][0]['id']

    def _get_current_bookings(self, resource_data, employee_id=None):
        now_timestamp = int(datetime.utcnow().timestamp())
        current_bookings = {}
        for resource_item in resource_data['data']:
            r_id = resource_item['id']
            current_bookings[r_id] = None
            for booking in resource_item['shareable_bookings']:
                employee_match = booking['acquired_by']['id'] == employee_id
                start_match = booking['acquired_since'] <= now_timestamp
                end_match = (booking['released_at'] >= now_timestamp or
                             booking['released_at'] == 0)
                if start_match and end_match:
                    current_bookings[r_id] = {
                        'id': booking['id'],
                        'acquired_by_me': employee_match,
                        'details': booking,
                    }
                    break
        return current_bookings

    def _get_current_attachments(self, current_bookings, client_key,
                                 project_key=None, issue_number=None):
        current_attachments = {}
        for r_id, current_booking in current_bookings.items():
            current_attachments[r_id] = None
            if current_booking is not None:
                attachments = current_booking['details'][
                    'jira_issue_attachments']
                for attachment in attachments:
                    if (attachment['client_key'] == client_key and
                            attachment['project_key'] == project_key and
                            attachment['issue_number'] == issue_number):
                        current_attachments[r_id] = {
                            'id': attachment['id'],
                            'details': attachment,
                        }
        return current_attachments

    def list_shareable_resources(self, client_key, account_id,
                                 current_issue=False, issue_key=None):
        org_assignment = self._get_org_assignment_by_client_key(client_key)
        rest_client = self._get_rest_client(secret=self._cluster_secret)
        list_params = {}
        project_key = None,
        issue_number = None,
        if issue_key:
            project_key, issue_number = self._parse_issue_key(issue_key)
        if current_issue and project_key and issue_number:
            list_params.update({
                'client_key': client_key,
                'project_key': project_key,
                'issue_number': issue_number,
            })
        _, resource_data = rest_client.shareable_resources_list(
            org_assignment.organization_id, list_params)

        auth_token = None
        employee_id = None
        user_assignment = self._get_user_assignment_by_account_id(
            account_id, raise_not_found=False)
        if user_assignment and user_assignment.auth_user_id:
            auth_token = self._get_auth_token_by_auth_user_id(
                user_assignment.auth_user_id)
            employee_id = self._get_employee_id(
                self._get_rest_client(token=auth_token),
                org_assignment.organization_id)

        resource_ids = [item['id'] for item in resource_data['data']]
        book_permissions = self._get_book_permissions(
            resource_ids, auth_token)
        current_bookings = self._get_current_bookings(
            resource_data, employee_id)
        current_attachments = self._get_current_attachments(
            current_bookings, client_key, project_key, issue_number)
        return [
            {
                'id': item['id'],
                'name': item['name'],
                'book_permission': book_permissions[item['id']],
                'current_booking': current_bookings[item['id']],
                'current_attachment': current_attachments[item['id']],
                'details': item,
            }
            for item in resource_data['data']
        ]


class ShareableResourceAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ShareableResourceController
