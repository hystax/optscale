import logging
import uuid
from sqlalchemy import and_
from optscale_exceptions.common_exc import NotFoundException
from rest_api_server.exceptions import Err
from rest_api_server.models.models import Organization
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.report_import import ReportImportFileController


LOG = logging.getLogger(__name__)


class CodeReportFileController(ReportImportFileController):
    BUCKET_NAME = 'code-reports'

    def get_organization(self, organization_id):
        return self.session.query(Organization).filter(and_(
            Organization.id == organization_id,
            Organization.deleted.is_(False)
        )).one_or_none()

    def initialize_upload(self, organization_id):
        org = self.get_organization(organization_id)
        if org is None:
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        self.filename = '{0}/{1}.zip'.format(organization_id, str(uuid.uuid4()))
        mpu = self.s3_client.create_multipart_upload(Bucket=self.BUCKET_NAME,
                                                     Key=self.filename)
        self.mpu_id = mpu['UploadId']

    def complete_upload(self, organization_id):
        if len(self.buffer) != 0:
            self.flush_buffer()
        self.s3_client.complete_multipart_upload(
            Bucket=self.BUCKET_NAME,
            Key=self.filename,
            UploadId=self.mpu_id,
            MultipartUpload={'Parts': self.parts},
        )


class CodeReportAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return CodeReportFileController
