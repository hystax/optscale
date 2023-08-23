import logging

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.inactive_users_base import ArchiveInactiveUsersBase
from bumiworker.bumiworker.modules.recommendations.inactive_users import (
    InactiveUsers as InactiveUsersRecommendation)


LOG = logging.getLogger(__name__)


class InactiveUsers(ArchiveInactiveUsersBase, InactiveUsersRecommendation):
    SUPPORTED_CLOUD_TYPES = [
        'aws_cnr',
        'nebius'
    ]

    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            self.reason_description_map[ArchiveReason.RESOURCE_DELETED])

    def _handle_optimization(self, user_info, optimization):
        if not user_info:
            self._set_reason_properties(
                optimization, ArchiveReason.RECOMMENDATION_APPLIED)
        elif user_info.get('is_password_used'):
            self._set_reason_properties(
                optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT,
                description=self.PASSWORD_USED_DESCRIPTION)
        elif user_info.get('is_access_keys_used'):
            self._set_reason_properties(
                optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT,
                description=self.ACCESS_KEY_USED_DESCRIPTION)
        elif user_info.get('is_service_account_used'):
            self._set_reason_properties(
                optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT,
                description=self.SERVICE_ACCOUNT_USED_DESCRIPTION)
        else:
            self._set_reason_properties(
                optimization, ArchiveReason.OPTIONS_CHANGED)
        return optimization


def main(organization_id, config_client, created_at, **kwargs):
    return InactiveUsers(organization_id, config_client, created_at).get()
