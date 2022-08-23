from collections import OrderedDict

from bumi_worker.modules.inactive_users_base import InactiveUsersBase


DEFAULT_DAYS_THRESHOLD = 90


class InactiveUsers(InactiveUsersBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DEFAULT_DAYS_THRESHOLD},
            'skip_cloud_accounts': {'default': []}
        })

    def handle_aws_user(self, user, now, cloud_adapter, days_threshold):
        inactive_threshold = self._get_inactive_threshold(days_threshold)

        def is_outdated(last_used_):
            return self._is_outdated(now, last_used_, inactive_threshold)

        is_old_user = is_outdated(user.get('CreateDate', now))
        password_last_used = self._get_password_last_used(user)
        is_password_unused = is_outdated(password_last_used)
        if not is_old_user or not is_password_unused:
            return

        access_keys_last_used = self._get_access_keys_last_used(
            user, cloud_adapter)
        is_access_keys_unused = is_outdated(access_keys_last_used)

        if is_password_unused and is_access_keys_unused:
            last_used = max(access_keys_last_used, password_last_used)
            return {
                'user_name': user['UserName'],
                'user_id': user['UserId'],
                'last_used': int(last_used.timestamp())
            }


def main(organization_id, config_client, created_at, **kwargs):
    return InactiveUsers(organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Inactive IAM users'
