import logging

from rest_api.rest_api_server.controllers.assignment_bulk import AssignmentBulkController
from rest_api.rest_api_server.controllers.assignment_request import (
    AssignmentRequestController)
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, ForbiddenException)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import AssignmentRequest
from rest_api.rest_api_server.utils import (
    check_string_attribute, raise_not_provided_exception,
    raise_does_not_exist_exception, check_list_attribute)

LOG = logging.getLogger(__name__)


class AssignmentRequestBulkController(AssignmentRequestController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._assignment_bulk_ctrl = None

    @property
    def assignment_bulk_ctrl(self):
        if not self._assignment_bulk_ctrl:
            self._assignment_bulk_ctrl = AssignmentBulkController(
                self.session, self._config, self.token
            )
        return self._assignment_bulk_ctrl

    @staticmethod
    def _validate_parameters(**params):
        allowed_parameters = ['resource_ids', 'approver_id', 'message']
        for param in allowed_parameters:
            value = params.get(param)
            if param == 'resource_ids':
                check_list_attribute(param, value)
                for item in value:
                    check_string_attribute('id', item)
            elif value is not None:
                check_string_attribute(param, value)
        unexpected_params = [
            p for p in params.keys() if p not in allowed_parameters]
        if unexpected_params:
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])

    def _prepare_assign_request_common_data(self, organization_id, employee_id,
                                            user_id, **kwargs):
        approver_id = kwargs.get('approver_id')
        if not approver_id:
            raise_not_provided_exception('approver_id')
        approver = self.employee_ctrl.get(approver_id,
                                          organization_id=organization_id)
        if not approver:
            raise_does_not_exist_exception('approver_id', approver_id)
        if approver.id == employee_id:
            raise ForbiddenException(Err.OE0424, [])
        message = kwargs.get('message', None)
        return approver, message

    def create_assignment_requests_bulk(self, user_id, organization_id, token,
                                        **kwargs):
        result = {"succeeded": [],
                  "failed": []}
        self._validate_parameters(**kwargs)
        employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=organization_id)
        approver, message = self._prepare_assign_request_common_data(
            organization_id, employee.id, user_id, **kwargs)
        succeeded, failed = self.assignment_bulk_ctrl.prepare_resources(
            employee, token, by_request=True, **kwargs)
        result["failed"] = failed
        assignment_requests = []
        for resource in succeeded:
            assignment_request = AssignmentRequest(
                resource_id=resource['id'],
                source_pool_id=resource.get('pool_id'),
                message=message,
                approver_id=approver.id,
                requester_id=employee.id)
            assignment_requests.append(assignment_request)
        old_requests = self.assignment_bulk_ctrl.invalidate_requests(
            [res['id'] for res in succeeded])
        if old_requests:
            self.session.bulk_save_objects(old_requests)
            self.session.flush()
        self.session.bulk_save_objects(assignment_requests)
        self.session.commit()
        result["succeeded"] = [res['id'] for res in succeeded]
        return result


class AssignmentRequestAsyncBulkController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AssignmentRequestBulkController
