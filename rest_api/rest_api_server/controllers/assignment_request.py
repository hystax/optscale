import logging

from datetime import datetime

from sqlalchemy.sql import and_, or_

from rest_api.rest_api_server.controllers.assignment import AssignmentController
from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.cloud_account import (
    CloudAccountController)
from rest_api.rest_api_server.controllers.cloud_resource import CloudResourceController
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException, ForbiddenException,
    FailedDependency)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import (
    AssignmentRequest, CloudAccount, Organization)
from rest_api.rest_api_server.utils import (
    check_string_attribute, raise_not_provided_exception,
    raise_does_not_exist_exception, check_int_attribute)
from rest_api.rest_api_server.models.enums import (
    AssignmentRequestStatuses,
    AssignmentRequestTypes as ReqTypes)

LOG = logging.getLogger(__name__)


class AssignmentRequestController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._assignment_ctrl = None
        self._employee_ctrl = None
        self._resource_ctrl = None
        self._cloud_account_ctrl = None

    @property
    def assignment_ctrl(self):
        if not self._assignment_ctrl:
            self._assignment_ctrl = AssignmentController(
                self.session, self._config, self.token
            )
        return self._assignment_ctrl

    @property
    def employee_ctrl(self):
        if not self._employee_ctrl:
            self._employee_ctrl = EmployeeController(
                self.session, self._config, self.token
            )
        return self._employee_ctrl

    @property
    def resource_ctrl(self):
        if not self._resource_ctrl:
            self._resource_ctrl = CloudResourceController(
                self.session, self._config, self.token
            )
        return self._resource_ctrl

    @property
    def cloud_account_ctrl(self):
        if not self._cloud_account_ctrl:
            self._cloud_account_ctrl = CloudAccountController(
                self.session, self._config, self.token
            )
        return self._cloud_account_ctrl

    def _get_model_type(self):
        return AssignmentRequest

    @staticmethod
    def _validate_parameters(**params):
        allowed_parameters = ['resource_id', 'message', 'approver_id']
        for param in allowed_parameters:
            value = params.get(param)
            if value is not None:
                check_string_attribute(param, value)
        unexpected_params = [
            p for p in params.keys() if p not in allowed_parameters]
        if unexpected_params:
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])

    @staticmethod
    def _validate_patch_parameters(**params):
        allowed_parameters = ['action']
        if params.pop('action') == 'accept':
            allowed_parameters.extend(['owner_id', 'pool_id'])
        for param in allowed_parameters:
            value = params.get(param)
            if value is not None:
                check_string_attribute(param, value)
        unexpected_params = [
            p for p in params.keys() if p not in allowed_parameters]
        if unexpected_params:
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])

    def _get_organization_by_resource_id(self, resource_id):
        # we should be able to define organization even if resource was deleted
        resource = self.resource_ctrl.get(resource_id, include_deleted=True)
        if not resource:
            raise_does_not_exist_exception('resource_id', resource_id)
        if resource.get('cloud_account_id'):
            cloud_acc = self.session.query(CloudAccount).filter(
                CloudAccount.id == resource['cloud_account_id']).scalar()
            if cloud_acc:
                return cloud_acc.organization
        else:
            return self.session.query(Organization).filter(
                Organization.id == resource['organization_id']).one_or_none()

    def _get_assignment_request_by_id(self, request_id, user_id):
        request = self.get(item_id=request_id)
        if request is None:
            raise NotFoundException(
                Err.OE0002, [AssignmentRequest.__name__, request_id])
        return request

    def _finish_request(self, request, target_request_status):
        self.update(request.id, status=target_request_status,
                    deleted_at=int(datetime.utcnow().timestamp()))

    def list_assignment_requests(self, user_id, organization_id=None,
                                 req_type=None):
        employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=organization_id)
        resp = {}
        if req_type == ReqTypes.INCOMING.value:
            resp.update({ReqTypes.INCOMING.value: self.list(
                approver_id=employee.id)})
        elif req_type == ReqTypes.OUTGOING.value:
            resp.update({ReqTypes.OUTGOING.value: self.list(
                requester_id=employee.id)})
        else:
            requests = self.session.query(self.model_type).filter(and_(
                self.model_type.deleted.is_(False),
                or_(self.model_type.approver_id == employee.id,
                    self.model_type.requester_id == employee.id))).all()
            resp.update(
                {ReqTypes.INCOMING.value: [req for req in requests
                                           if req.approver_id == employee.id],
                 ReqTypes.OUTGOING.value: [req for req in requests
                                           if req.requester_id == employee.id]}
            )
        return resp

    def _prepare_assign_req_data(self, organization_id, **kwargs):
        resource_id = kwargs.get('resource_id')
        if not resource_id:
            raise_not_provided_exception('resource_id')
        resource = None
        try:
            resource = self.resource_ctrl.get(resource_id)
        except NotFoundException:
            raise_does_not_exist_exception('resource_id', resource_id)
        if resource.get('cluster_id'):
            raise FailedDependency(Err.OE0464, [resource_id])
        approver_id = kwargs.get('approver_id')
        if not approver_id:
            raise_not_provided_exception('approver_id')
        approver = self.employee_ctrl.get(approver_id,
                                          organization_id=organization_id)
        if not approver:
            raise_does_not_exist_exception('approver_id', approver_id)
        source_pool_id = resource.get('pool_id')
        return resource, approver, source_pool_id

    def validate_assign_request(self, resource, current_employee, token,
                                approver):
        if approver.id == current_employee.id:
            raise ForbiddenException(Err.OE0424, [])
        if self.assignment_ctrl.validate_resource(
                resource, current_employee, token):
            return
        else:
            raise ForbiddenException(Err.OE0381, [resource['cloud_resource_id']])

    def create_assignment_request(self, user_id, organization_id, token,
                                  **kwargs):
        self._validate_parameters(**kwargs)
        employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=organization_id)
        message = kwargs.get('message')
        resource, approver, source_pool_id = self._prepare_assign_req_data(
            organization_id, **kwargs
        )
        self.validate_assign_request(resource, current_employee=employee,
                                     token=token, approver=approver)
        requests = self.assignment_ctrl.invalidate_requests([resource['id']])
        if requests:
            self.session.bulk_save_objects(requests)
        request = self.create(
            resource_id=resource['id'], source_pool_id=source_pool_id,
            message=message, approver_id=approver.id,
            requester_id=employee.id)
        return request

    def _publish_assignment_request_activity(self, assignment_request,
                                             evt_class):
        employee_requester = assignment_request.requester
        employee_approver = assignment_request.approver
        request_desc_map = {
            'ASSIGNMENT_REQUEST_ACCEPTED': {
                'routing_key': 'employee.assignment_request_accepted',
                'action': 'assignment_request_accepted'
            },
            'ASSIGNMENT_REQUEST_DECLINED': {
                'routing_key': 'employee.assignment_request_declined',
                'action': 'assignment_request_declined'
            }
        }
        event_params = request_desc_map.get(evt_class, {})
        if not event_params:
            LOG.error('Not valid event class was passed: %s. '
                      'Activity was not sent.', evt_class)
            return
        resource = self.resource_ctrl.get(assignment_request.resource_id,
                                          include_deleted=True)
        meta = {
            'object_name': employee_requester.name,
            'approver_name': employee_approver.name,
            'approver_id': employee_approver.id,
            'resource_name': resource['name'] if resource.get('name') else '',
            'resource_cloud_res_id': resource['cloud_resource_id']
        }

        self.publish_activities_task(
            employee_requester.organization_id, employee_requester.id,
            'employee', event_params.get('action'),
            meta, event_params.get('routing_key'), add_token=True)

    def accept_assignment_request(self, request_id, user_id, token, **kwargs):
        self._validate_patch_parameters(**kwargs)
        request = self._get_assignment_request_by_id(request_id, user_id)
        org = self._get_organization_by_resource_id(request.resource_id)
        employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=org.id)
        if request.approver_id != employee.id:
            raise ForbiddenException(Err.OE0391, [])
        owner_id = kwargs.get('owner_id', request.approver_id)
        pool_id = kwargs.get('pool_id')
        created_at = kwargs.get('created_at', request.created_at)
        if isinstance(created_at, datetime):
            created_at = int(created_at.timestamp())
        self.assignment_ctrl.create_assignment(
            user_id=user_id, organization_id=org.id,
            resource_id=request.resource_id,
            owner_id=owner_id,
            pool_id=pool_id,
            created_at=created_at,
            token=token,
            by_request=True
        )
        self._finish_request(request, AssignmentRequestStatuses.APPROVED)
        self._publish_assignment_request_activity(
            request, "ASSIGNMENT_REQUEST_ACCEPTED")

    def decline_assignment_request(self, request_id, user_id, token=None,
                                   **kwargs):
        self._validate_patch_parameters(**kwargs)
        request = self._get_assignment_request_by_id(request_id, user_id)
        org = self._get_organization_by_resource_id(request.resource_id)
        employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=org.id)
        if request.approver_id != employee.id:
            raise ForbiddenException(Err.OE0391, [])
        self._finish_request(request, AssignmentRequestStatuses.DECLINED)
        self._publish_assignment_request_activity(
            request, "ASSIGNMENT_REQUEST_DECLINED")

    def cancel_assignment_request(self, request_id, user_id, token=None,
                                  **kwargs):
        self._validate_patch_parameters(**kwargs)
        request = self._get_assignment_request_by_id(request_id, user_id)
        org = self._get_organization_by_resource_id(request.resource_id)
        employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=org.id)
        if request.requester_id != employee.id:
            raise ForbiddenException(Err.OE0419, [])
        self._finish_request(request, AssignmentRequestStatuses.CANCELED)


class AssignmentRequestAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AssignmentRequestController
