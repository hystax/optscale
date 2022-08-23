import logging
from sqlalchemy import and_
from herald_client.client_v2 import Client as HeraldClient
from optscale_exceptions.common_exc import NotFoundException
from rest_api_server.controllers.base import BaseController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.employee import EmployeeController
from rest_api_server.exceptions import Err
from rest_api_server.models.models import Organization
from rest_api_server.utils import CURRENCY_MAP

LOG = logging.getLogger(__name__)


class AuditSubmitController(BaseController):

    def get_organization(self, organization_id):
        org = self.session.query(Organization).filter(
            and_(Organization.id == organization_id,
                 Organization.deleted.is_(False))).one_or_none()
        if not org:
            raise NotFoundException(Err.OE0002, [Organization.__name__,
                                                 organization_id])
        return org

    def send_submit_audit_service_email(self, org_id, org_name, currency,
                                        employee_id, employee_name):
        recipient = self._config.optscale_email_recipient()
        if not recipient:
            return
        public_ip = self._config.public_ip()
        subject = '[%s] Organization submitted for technical audit' % public_ip
        template_params = {
            'texts': {
                'organization': {
                    'id': org_id,
                    'name': org_name,
                    'currency_code': CURRENCY_MAP.get(currency, '$')
                },
                'employee': {
                    'id': employee_id,
                    'name': employee_name,
                }
            }
        }
        HeraldClient(
            url=self._config.herald_url(),
            secret=self._config.cluster_secret()
        ).email_send(
            [recipient], subject, template_type="organization_audit_submit",
            template_params=template_params)

    def submit(self, organization_id):
        organization = self.get_organization(organization_id)
        user_id = self.get_user_id()
        employee = EmployeeController(
            self.session, self._config, self.token
                ).get_employee_by_user_and_organization(
                    user_id, organization_id=organization_id)
        meta = {
            'object_name': organization.name,
            'employee_name': employee.name,
            'employee_id': employee.id
        }
        self.publish_activities_task(
            organization.id, organization.id, 'organization',
            'technical_audit_submit', meta,
            'organization.technical_audit_submit', add_token=True)
        self.send_submit_audit_service_email(organization.id, organization.name,
                                             organization.currency, employee.id,
                                             employee.name)


class AuditSubmitAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AuditSubmitController
