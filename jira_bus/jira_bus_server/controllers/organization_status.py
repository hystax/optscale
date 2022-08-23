import json
import logging

from jira_bus_server.controllers.base import (BaseController,
                                              BaseAsyncControllerWrapper)

LOG = logging.getLogger(__name__)


class OrganizationStatusController(BaseController):
    def get_connected_tenants(self, organization_id):
        org_assignment = self._get_org_assignment_by_org_id(
            organization_id, raise_not_found=False)

        # Currently, there is one-to-one relation between organization and
        # Jira tenant, but it may change later, so let's use a list
        connected_tenants = []

        if org_assignment is not None:
            app_installation = org_assignment.app_installation
            extra_payload = json.loads(app_installation.extra_payload)
            connected_tenants.append({
                'client_key': app_installation.client_key,
                'description': extra_payload.get('description'),
                # Jira docs say to use displayUrl if it's present for
                # user-facing links
                'display_url': extra_payload.get(
                    'displayUrl') or extra_payload['baseUrl'],
            })

        return connected_tenants


class OrganizationStatusAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return OrganizationStatusController
