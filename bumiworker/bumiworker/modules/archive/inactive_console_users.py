import logging

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.inactive_users_base import ArchiveInactiveUsersBase
from bumiworker.bumiworker.modules.recommendations.inactive_console_users import (
    InactiveConsoleUsers as InactiveConsoleUsersRecommendation)


LOG = logging.getLogger(__name__)


class InactiveConsoleUsers(ArchiveInactiveUsersBase,
                           InactiveConsoleUsersRecommendation):
    LOGIN_PROFILE_REVOKED_DESCRIPTION = 'login profile was revoked'

    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            self.LOGIN_PROFILE_REVOKED_DESCRIPTION)

    def _handle_optimization(self, user_info, optimization):
        if not user_info:
            self._set_reason_properties(
                optimization, ArchiveReason.RESOURCE_DELETED)
        elif user_info.get('is_password_used'):
            self._set_reason_properties(
                optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT,
                description=self.PASSWORD_USED_DESCRIPTION)
        elif user_info.get('is_access_keys_used') is False:
            self._set_reason_properties(
                optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT,
                description=self.ACCESS_KEY_USED_DESCRIPTION)
        elif user_info.get('has_user_console_access') is False:
            self._set_reason_properties(
                optimization, ArchiveReason.RECOMMENDATION_APPLIED)
        else:
            self._set_reason_properties(
                optimization, ArchiveReason.OPTIONS_CHANGED)
        return optimization

    def handle_aws_user(self, user, now, cloud_adapter, days_threshold):
        result = super().handle_aws_user(
            user, now, cloud_adapter, days_threshold)
        if not result:
            return

        has_user_console_access = cloud_adapter.get_login_profile(
            user['UserName']) is not None
        result['has_user_console_access'] = has_user_console_access
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return InactiveConsoleUsers(
        organization_id, config_client, created_at).get()
