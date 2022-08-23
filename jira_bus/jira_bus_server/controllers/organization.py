import logging

from jira_bus_server.controllers.base import (BaseController,
                                              BaseAsyncControllerWrapper)

LOG = logging.getLogger(__name__)


class OrganizationController(BaseController):
    def list_organizations(self, account_id):
        auth_token = self.get_auth_token(account_id)
        rest_client = self._get_rest_client(token=auth_token)
        auth_client = self._get_auth_client(token=auth_token)
        _, org_list = rest_client.organization_list()
        _, actions_resources = auth_client.action_resources_get('EDIT_PARTNER')
        managed_organizations = {
            r_id for r_type, r_id in actions_resources['EDIT_PARTNER']
            if r_type == 'organization'}
        return [
            {
                'id': org['id'],
                'name': org['name'],
                'is_manager': org['id'] in managed_organizations,
            }
            for org in org_list['organizations']
        ]


class OrganizationAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return OrganizationController
