import logging
from datetime import datetime

from jira_bus.jira_bus_server.controllers.base import (
    BaseController,
    BaseAsyncControllerWrapper,
)
from jira_bus.jira_bus_server.models.models import UserAssignment
from jira_bus.jira_bus_server.utils import gen_id

LOG = logging.getLogger(__name__)


class UserAssignmentController(BaseController):
    def get_assignment(self, account_id):
        user_assignment = self._get_user_assignment_by_account_id(account_id)
        return user_assignment.to_dict()

    def create_assignment(self, account_id):
        user_assignment = (
            self._get_user_assignment_by_account_id(account_id, raise_not_found=False) or
            UserAssignment()
        )
        user_assignment.jira_account_id = account_id
        user_assignment.secret = gen_id()

        self.session.add(user_assignment)
        self.session.commit()
        return user_assignment.secret

    def assign_auth_user(self, auth_user_id, secret):
        user_assignment = self._get_user_assignment_by_secret(secret)
        user_assignment.auth_user_id = auth_user_id
        self.session.add(user_assignment)
        self.session.commit()
        auth_token = self._get_auth_token_by_auth_user_id(auth_user_id)
        auth_client = self._get_auth_client(token=auth_token)
        auth_client.user_update(auth_user_id, jira_connected=True)

    def delete_assignment(self, account_id):
        user_assignment = self._get_user_assignment_by_account_id(
            account_id, raise_not_found=False
        )
        if user_assignment:
            user_assignment.deleted_at = int(datetime.utcnow().timestamp())
            self.session.add(user_assignment)
            self.session.commit()
            if user_assignment.auth_user_id is not None:
                auth_token = self._get_auth_token_by_auth_user_id(
                    user_assignment.auth_user_id
                )
                auth_client = self._get_auth_client(token=auth_token)
                auth_client.user_update(
                    user_assignment.auth_user_id, jira_connected=False
                )


class UserAssignmentAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return UserAssignmentController
