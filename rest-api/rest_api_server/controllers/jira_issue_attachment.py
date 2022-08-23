import logging
from datetime import datetime
from rest_api_server.controllers.base import BaseController, MongoMixin
from rest_api_server.controllers.shareable_resource import (
    ShareableBookingController)
from rest_api_server.controllers.employee import (
    EmployeeController)
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.exceptions import Err
from sqlalchemy.sql import and_, exists
from optscale_exceptions.common_exc import (
    ConflictException, NotFoundException, ForbiddenException)
from rest_api_server.models.models import JiraIssueAttachment, ShareableBooking

LOG = logging.getLogger(__name__)


class JiraIssueAttachmentController(BaseController, MongoMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._shareable_booking_controller = None
        self._employee_ctrl = None

    def _get_model_type(self):
        return JiraIssueAttachment

    @property
    def shareable_booking_controller(self):
        if not self._shareable_booking_controller:
            self._shareable_booking_controller = ShareableBookingController(
                self.session, self._config, self.token)
        return self._shareable_booking_controller

    @property
    def employee_ctrl(self):
        if not self._employee_ctrl:
            self._employee_ctrl = EmployeeController(
                self.session, self._config, self.token)
        return self._employee_ctrl

    def validate_shareable_booking(self, shareable_booking_id, user_id,
                                   organization_id=None):
        shareable_booking = self.shareable_booking_controller.get(
            shareable_booking_id)
        if not shareable_booking:
            raise NotFoundException(Err.OE0002, [ShareableBooking.__name__,
                                                 shareable_booking_id])
        if user_id:
            employee = self.employee_ctrl.get_employee_by_user_and_organization(
                user_id, organization_id or shareable_booking.organization_id)
            if shareable_booking.acquired_by_id != employee.id:
                raise ForbiddenException(Err.OE0501, [])
        return shareable_booking

    def check_attachment_exists(self, shareable_booking_id, client_key,
                                project_key, issue_number, **kwargs):
        attachment_exist = self.session.query(
            exists().where(
                and_(
                    self.model_type.deleted.is_(False),
                    self.model_type.shareable_booking_id == shareable_booking_id,
                    self.model_type.client_key == client_key,
                    self.model_type.project_key == project_key,
                    self.model_type.issue_number == issue_number
                )
            )
        ).scalar()
        if attachment_exist:
            raise ConflictException(Err.OE0502, [])

    def create(self, organization_id, user_id, **kwargs):
        shareable_booking_id = kwargs.get('shareable_booking_id')
        self.validate_shareable_booking(shareable_booking_id, user_id,
                                        organization_id)
        self.check_attachment_exists(**kwargs)
        jira_issue_attachment = super().create(**kwargs)
        return jira_issue_attachment

    def _get(self, item_id):
        attachment = self.get(item_id)
        if not attachment:
            raise NotFoundException(Err.OE0002, [JiraIssueAttachment.__name__,
                                                 item_id])
        return attachment

    def edit(self, item_id, user_id, **kwargs):
        attachment = self._get(item_id)
        shareable_booking = self.validate_shareable_booking(
            attachment.shareable_booking_id, user_id)

        attachment = super().edit(item_id, **kwargs)
        auto_detach_status = attachment.auto_detach_status
        if auto_detach_status and attachment.status == auto_detach_status:
            self.delete(item_id, user_id, shareable_booking)
        return attachment

    def delete(self, item_id, user_id, shareable_booking=None):
        attachment = self._get(item_id)
        if not shareable_booking:
            self.validate_shareable_booking(
                attachment.shareable_booking_id, user_id)
        attachment.deleted_at = int(datetime.utcnow().timestamp())
        self.shareable_booking_controller.check_autorelease(
            attachment.shareable_booking_id)
        self.session.commit()

    def list(self, **kwargs):
        organization_id = kwargs.get('organization_id')
        client_key = kwargs.get('client_key')
        project_key = kwargs.get('project_key')
        issue_number = kwargs.get('issue_number')
        attachments = self.session.query(JiraIssueAttachment).join(
            ShareableBooking, and_(
                ShareableBooking.id == JiraIssueAttachment.shareable_booking_id,
                ShareableBooking.deleted.is_(False),
                ShareableBooking.organization_id == organization_id
            )
        ).filter(
            JiraIssueAttachment.deleted.is_(False),
            JiraIssueAttachment.client_key == client_key,
            JiraIssueAttachment.project_key == project_key,
            JiraIssueAttachment.issue_number == issue_number
        ).all()
        return attachments


class JiraIssueAttachmentAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return JiraIssueAttachmentController
