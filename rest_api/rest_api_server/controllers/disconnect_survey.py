import logging
from sys import getsizeof
from sqlalchemy import and_

from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import Organization
from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.utils import check_string_attribute

from optscale_client.herald_client.client_v2 import Client as HeraldClient
from tools.optscale_exceptions.common_exc import NotFoundException, WrongArgumentsException


LOG = logging.getLogger(__name__)


class DisconnectSurveyController(BaseController):

    MAX_PAYLOAD_SIZE = 5 * 1024  # 5 Kb

    def _validate_parameters(self, **params):
        allowed_parameters = ['survey_type', 'payload']
        for param in allowed_parameters:
            value = params.get(param)
            if value is None:
                raise WrongArgumentsException(Err.OE0548, [param])
            if param == 'survey_type':
                check_string_attribute(param, value)
            if param == 'payload':
                self._check_payload(value)

        unexpected_params = [
            p for p in params.keys() if p not in allowed_parameters]
        if unexpected_params:
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])

    @staticmethod
    def _get_data(**params):
        return params.get('survey_type'), params.get('payload')

    @staticmethod
    def _check_payload_type(payload):
        if not isinstance(payload, dict):
            raise WrongArgumentsException(Err.OE0426, [])

    def _check_payload_size(self, payload):
        if getsizeof(payload) >= self.MAX_PAYLOAD_SIZE:
            raise WrongArgumentsException(Err.OE0547, [self.MAX_PAYLOAD_SIZE])  # TODO: add error

    def _check_payload(self, payload):
        self._check_payload_size(payload)
        self._check_payload_type(payload)

    def get_organization(self, organization_id):
        org = self.session.query(Organization).filter(
            and_(Organization.id == organization_id,
                 Organization.deleted.is_(False))).one_or_none()
        if not org:
            raise NotFoundException(Err.OE0002, [Organization.__name__,
                                                 organization_id])
        return org

    def send_survey_service_email(self, org_id, org_name, user_id, survey_type, data):
        recipient = self._config.optscale_email_recipient()
        if not recipient:
            return
        subject = '%s [%s, %s]' % (survey_type, org_id, org_name)
        payload = [{"k": k, "v": v} for k, v in data.items()]
        template_params = {
            'texts': {
                'organization': {
                    'id': org_id,
                    'name': org_name,
                },
                'user': user_id,
                'data': payload
            }
        }
        HeraldClient(
            url=self._config.herald_url(),
            secret=self._config.cluster_secret()
        ).email_send(
            [recipient], subject, template_type="disconnect_survey",
            template_params=template_params)

    def submit(self, organization_id, **kwargs):
        self._validate_parameters(**kwargs)
        survey_type, data = self._get_data(**kwargs)
        org = self.get_organization(organization_id)
        user_id = self.get_user_id()

        employee = EmployeeController(
            self.session, self._config, self.token
        ).get_employee_by_user_and_organization(
            user_id, organization_id=organization_id)

        self.send_survey_service_email(
            organization_id,
            org.name,
            employee.name,
            survey_type,
            data
        )


class DisconnectSurveyAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return DisconnectSurveyController
