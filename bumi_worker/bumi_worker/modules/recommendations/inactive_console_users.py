from collections import OrderedDict
from datetime import timedelta

from bumi_worker.modules.inactive_users_base import InactiveUsersBase


DEFAULT_DAYS_THRESHOLD = 90


class InactiveConsoleUsers(InactiveUsersBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DEFAULT_DAYS_THRESHOLD},
            'skip_cloud_accounts': {'default': []}
        })

    def _get_inactive_keys_threshold(self, days_threshold):
        return timedelta(days=(days_threshold / 2))

    def handle_aws_user(self, user, now, cloud_adapter, days_threshold):
        days_threshold_delta = self._get_inactive_threshold(days_threshold)
        inactive_access_keys_delta = self._get_inactive_keys_threshold(
            days_threshold)

        def is_outdated(last_used_, inactive_threshold):
            return self._is_outdated(now, last_used_, inactive_threshold)

        is_old_user = is_outdated(user.get('CreateDate', now),
                                  days_threshold_delta)
        password_last_used = self._get_password_last_used(user)
        is_console_password_unused = is_outdated(
            password_last_used, days_threshold_delta)
        if not is_old_user or not is_console_password_unused:
            return

        has_user_console_access = cloud_adapter.get_login_profile(
            user['UserName']) is not None

        access_keys_last_used = self._get_access_keys_last_used(
            user, cloud_adapter)
        is_access_keys_used = not is_outdated(
            access_keys_last_used, inactive_access_keys_delta)

        if (is_console_password_unused and is_access_keys_used and
                has_user_console_access):
            return {
                'user_name': user['UserName'],
                'user_id': user['UserId'],
                'last_used': int(password_last_used.timestamp())
            }


def main(organization_id, config_client, created_at, **kwargs):
    return InactiveConsoleUsers(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'IAM users with unused console access'
