import logging
from datetime import datetime

from jira_bus.jira_bus_server.controllers.base import (
    BaseController,
    BaseAsyncControllerWrapper,
)
from jira_bus.jira_bus_server.models.models import OrganizationAssignment

LOG = logging.getLogger(__name__)


class OrganizationAssignmentController(BaseController):
    def get_organization_assignment(self, client_key, raise_not_found=True):
        org_assignment = self._get_org_assignment_by_client_key(
            client_key, raise_not_found=raise_not_found
        )
        if org_assignment:
            return org_assignment.to_dict()

    def get_organization_details(self, organization_id):
        rest_client = self._get_rest_client(secret=self._cluster_secret)
        _, org_details = rest_client.organization_get(organization_id)
        return {
            "id": org_details["id"],
            "name": org_details["name"],
        }

    def create_organization_assignment(self, client_key, organization_id):
        app_installation = self._get_app_installation_by_client_key(client_key)
        org_assignment = (
            self._get_org_assignment_by_client_key(client_key, raise_not_found=False) or
            OrganizationAssignment()
        )
        org_assignment.organization_id = organization_id
        org_assignment.app_installation_id = app_installation.id
        self.session.add(org_assignment)
        self.session.commit()

    def delete_organization_assignment(self, client_key):
        org_assignment = self._get_org_assignment_by_client_key(
            client_key, raise_not_found=False
        )
        if org_assignment:
            org_assignment.deleted_at = int(datetime.utcnow().timestamp())
            self.session.add(org_assignment)
            self.session.commit()


class OrganizationAssignmentAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return OrganizationAssignmentController
